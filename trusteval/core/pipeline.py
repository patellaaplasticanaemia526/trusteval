# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Evaluation pipeline orchestrator.

Coordinates the execution of pillar evaluations either sequentially or
in parallel, collects ``PillarResult`` objects, and feeds them into the
``Scorer`` to produce the final ``EvaluationResult``.
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List

from trusteval.core.result import PillarResult
from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level
from trusteval.utils.logger import get_logger

logger = get_logger(__name__)

# Type alias for a pillar evaluation function.  It receives the pillar
# name and a list of prompts, and returns a ``PillarResult``.
PillarEvalFn = Callable[[str, List[str]], PillarResult]


class EvaluationPipeline:
    """Orchestrates running multiple pillar evaluations.

    Args:
        pillar_fns: Mapping of pillar name to its evaluation callable.
        scorer: A ``Scorer`` instance with the desired pillar weights.
        parallel: If ``True`` (default), run pillars concurrently using
            a thread pool; otherwise run them sequentially.
        max_workers: Maximum thread-pool workers when *parallel* is
            ``True``.  Defaults to the number of pillars.
        timeout_seconds: Per-pillar timeout in seconds.
    """

    def __init__(
        self,
        pillar_fns: Dict[str, PillarEvalFn],
        scorer: Scorer,
        parallel: bool = True,
        max_workers: int | None = None,
        timeout_seconds: int = 300,
    ) -> None:
        self._pillar_fns = dict(pillar_fns)
        self._scorer = scorer
        self._parallel = parallel
        self._max_workers = max_workers or len(pillar_fns)
        self._timeout = timeout_seconds

    def run(self, prompts: List[str]) -> Dict[str, PillarResult]:
        """Execute all pillar evaluations and return their results.

        Args:
            prompts: The list of prompt strings to evaluate.

        Returns:
            Mapping of pillar name to its ``PillarResult``.
        """
        if self._parallel and len(self._pillar_fns) > 1:
            return self._run_parallel(prompts)
        return self._run_sequential(prompts)

    async def run_async(self, prompts: List[str]) -> Dict[str, PillarResult]:
        """Asynchronous variant of ``run``.

        Wraps each pillar function in ``asyncio.to_thread`` so blocking
        callables can execute without stalling the event loop.

        Args:
            prompts: The list of prompt strings to evaluate.

        Returns:
            Mapping of pillar name to its ``PillarResult``.
        """
        results: Dict[str, PillarResult] = {}

        async def _eval(name: str, fn: PillarEvalFn) -> tuple[str, PillarResult]:
            result = await asyncio.to_thread(fn, name, prompts)
            return name, result

        tasks = [_eval(name, fn) for name, fn in self._pillar_fns.items()]
        for coro in asyncio.as_completed(tasks):
            name, result = await coro
            logger.info(f"Pillar '{name}' completed: score={result.score:.2f}")
            results[name] = result

        return results

    def compute_overall(
        self, pillar_results: Dict[str, PillarResult]
    ) -> tuple[float, str, str]:
        """Compute aggregate score, grade, and trust level.

        Args:
            pillar_results: Mapping of pillar name to ``PillarResult``.

        Returns:
            Tuple of ``(overall_score, overall_grade, trust_level)``.
        """
        scores = {name: pr.score for name, pr in pillar_results.items()}
        overall = self._scorer.weighted_average(scores)
        grade = compute_grade(overall)
        trust = compute_trust_level(grade)
        return overall, grade, trust

    # -- Private helpers -----------------------------------------------------

    def _run_sequential(self, prompts: List[str]) -> Dict[str, PillarResult]:
        """Run pillars one at a time."""
        results: Dict[str, PillarResult] = {}
        for name, fn in self._pillar_fns.items():
            logger.info(f"Running pillar '{name}' (sequential)...")
            try:
                start = time.monotonic()
                result = fn(name, prompts)
                elapsed = time.monotonic() - start
                logger.info(
                    f"Pillar '{name}' completed in {elapsed:.1f}s — "
                    f"score={result.score:.2f}"
                )
                results[name] = result
            except Exception as exc:
                logger.error(f"Pillar '{name}' failed: {exc}")
                results[name] = PillarResult(
                    pillar=name,
                    score=0.0,
                    details={"error": str(exc)},
                )
        return results

    def _run_parallel(self, prompts: List[str]) -> Dict[str, PillarResult]:
        """Run pillars concurrently via a thread pool."""
        results: Dict[str, PillarResult] = {}

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_name = {
                executor.submit(fn, name, prompts): name
                for name, fn in self._pillar_fns.items()
            }

            for future in as_completed(future_to_name, timeout=self._timeout):
                name = future_to_name[future]
                try:
                    result = future.result()
                    logger.info(
                        f"Pillar '{name}' completed: score={result.score:.2f}"
                    )
                    results[name] = result
                except Exception as exc:
                    logger.error(f"Pillar '{name}' failed: {exc}")
                    results[name] = PillarResult(
                        pillar=name,
                        score=0.0,
                        details={"error": str(exc)},
                    )

        return results
