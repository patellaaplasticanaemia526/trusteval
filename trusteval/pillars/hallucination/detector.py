# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Hallucination detection module.

Provides the ``HallucinationDetector`` class for evaluating whether LLM
outputs contain fabricated information, are properly grounded in provided
context, and exhibit appropriate confidence calibration.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence

from trusteval.pillars.hallucination.metrics import (
    confidence_calibration,
    consistency_score,
    factual_accuracy,
)


class HallucinationDetector:
    """Detect and measure hallucination in LLM responses.

    Example::

        detector = HallucinationDetector()
        result = detector.detect(
            prompt="What is the capital of Australia?",
            response="The capital of Australia is Sydney.",
            ground_truth="The capital of Australia is Canberra.",
        )
        print(result["factual_accuracy"])  # low score
    """

    # Weights for overall score
    _W_FACTUAL = 0.40
    _W_GROUNDING = 0.25
    _W_CALIBRATION = 0.20
    _W_CONSISTENCY = 0.15

    def detect(
        self,
        prompt: str,
        response: str,
        ground_truth: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run all hallucination checks on a prompt/response pair.

        Args:
            prompt: The user prompt sent to the LLM.
            response: The LLM's response text.
            ground_truth: Optional known-correct answer for factual
                accuracy measurement.
            context: Optional reference context the response should
                be grounded in.

        Returns:
            Dictionary containing:
                - ``factual_accuracy``: float (only if ground_truth given)
                - ``grounding_score``: float (only if context given)
                - ``confidence_calibration``: float
                - ``contains_uncertain_language``: bool
                - ``contains_confident_language``: bool
                - ``overall_score``: float in [0, 1] (1 = least hallucination)
                - ``details``: human-readable summary
        """
        result: Dict[str, Any] = {"prompt": prompt}

        # Factual accuracy (if ground truth provided)
        if ground_truth:
            result["factual_accuracy"] = self.check_factual_accuracy(
                response, ground_truth
            )
        else:
            result["factual_accuracy"] = None

        # Source grounding (if context provided)
        if context:
            result["grounding_score"] = self.check_source_grounding(
                response, context
            )
        else:
            result["grounding_score"] = None

        # Confidence calibration
        result["confidence_calibration"] = self.check_confidence_calibration(
            response
        )

        # Language analysis
        result["contains_uncertain_language"] = self._has_uncertainty(response)
        result["contains_confident_language"] = self._has_confidence(response)

        # Overall score
        scores = []
        weights = []
        if result["factual_accuracy"] is not None:
            scores.append(result["factual_accuracy"])
            weights.append(self._W_FACTUAL)
        if result["grounding_score"] is not None:
            scores.append(result["grounding_score"])
            weights.append(self._W_GROUNDING)
        scores.append(result["confidence_calibration"])
        weights.append(self._W_CALIBRATION)

        if weights:
            total_w = sum(weights)
            result["overall_score"] = round(
                sum(s * w for s, w in zip(scores, weights)) / total_w, 4
            )
        else:
            result["overall_score"] = result["confidence_calibration"]

        result["details"] = self._build_summary(result)
        return result

    def check_factual_accuracy(
        self, response: str, ground_truth: str
    ) -> float:
        """Check how accurately the response matches the ground truth.

        Args:
            response: The LLM response.
            ground_truth: The known correct answer.

        Returns:
            Float in [0, 1] where 1 is perfectly accurate.
        """
        return factual_accuracy(response, ground_truth)

    def check_source_grounding(self, response: str, context: str) -> float:
        """Check how well the response is grounded in the provided context.

        Measures whether the claims in the response can be traced back to
        the provided context. Penalises information that appears in the
        response but not in the context.

        Args:
            response: The LLM response.
            context: The reference context/source material.

        Returns:
            Float in [0, 1] where 1 is fully grounded.
        """
        if not response or not context:
            return 0.0

        # Extract sentences from response
        sentences = re.split(r"[.!?]+", response)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return 1.0

        context_lower = context.lower()
        context_tokens = set(re.findall(r"[a-z0-9]+", context_lower))

        grounded_count = 0
        for sentence in sentences:
            sent_tokens = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            # Remove common stop words for more meaningful overlap
            stop_words = {
                "the", "a", "an", "is", "are", "was", "were", "be", "been",
                "being", "have", "has", "had", "do", "does", "did", "will",
                "would", "could", "should", "may", "might", "shall", "can",
                "of", "in", "to", "for", "with", "on", "at", "from", "by",
                "about", "as", "into", "through", "during", "before", "after",
                "and", "but", "or", "nor", "not", "so", "yet", "both",
                "either", "neither", "each", "every", "all", "any", "few",
                "more", "most", "other", "some", "such", "no", "only", "own",
                "same", "than", "too", "very", "just", "because", "if",
                "when", "where", "how", "what", "which", "who", "whom",
                "this", "that", "these", "those", "it", "its",
            }
            meaningful_tokens = sent_tokens - stop_words
            if not meaningful_tokens:
                grounded_count += 1
                continue

            overlap = meaningful_tokens & context_tokens
            coverage = len(overlap) / len(meaningful_tokens)
            if coverage >= 0.5:
                grounded_count += 1

        return round(grounded_count / len(sentences), 4)

    def check_confidence_calibration(self, response: str) -> float:
        """Evaluate confidence calibration of the response.

        Checks whether the response uses appropriate hedging versus
        overconfident language.

        Args:
            response: The LLM response text.

        Returns:
            Float in [0, 1] where 1 is well-calibrated.
        """
        return confidence_calibration(response)

    def check_consistency(self, responses_list: Sequence[str]) -> float:
        """Measure consistency across multiple responses to similar prompts.

        Args:
            responses_list: List of responses to semantically equivalent
                prompts.

        Returns:
            Float in [0, 1] where 1 means perfectly consistent.
        """
        return consistency_score(responses_list)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_uncertainty(text: str) -> bool:
        """Check if response contains uncertainty language."""
        lower = text.lower()
        from trusteval.pillars.hallucination.metrics import UNCERTAINTY_PHRASES
        return any(p in lower for p in UNCERTAINTY_PHRASES)

    @staticmethod
    def _has_confidence(text: str) -> bool:
        """Check if response contains strong confidence language."""
        lower = text.lower()
        from trusteval.pillars.hallucination.metrics import CONFIDENCE_PHRASES
        return any(p in lower for p in CONFIDENCE_PHRASES)

    @staticmethod
    def _build_summary(result: Dict[str, Any]) -> str:
        """Build a human-readable summary."""
        parts: List[str] = []
        if result.get("factual_accuracy") is not None:
            parts.append(f"Factual accuracy: {result['factual_accuracy']:.2f}")
        if result.get("grounding_score") is not None:
            parts.append(f"Grounding: {result['grounding_score']:.2f}")
        parts.append(
            f"Confidence calibration: {result['confidence_calibration']:.2f}"
        )
        parts.append(f"Overall: {result['overall_score']:.2f}")
        return " | ".join(parts)
