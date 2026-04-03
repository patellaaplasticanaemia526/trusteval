# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Unit tests for the core evaluator, pipeline, and result classes.

Since the TrustEvaluator class is under development, these tests validate
the pipeline orchestration, result construction, and scoring integration
that form the evaluator's foundation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from trusteval.core.pipeline import EvaluationPipeline
from trusteval.core.result import EvaluationResult, PillarResult
from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level
from trusteval.utils.exceptions import ScoringError, ValidationError
from trusteval.utils.validators import (
    VALID_INDUSTRIES,
    VALID_PROVIDERS,
    validate_industry,
    validate_provider_name,
)


# ------------------------------------------------------------------
# Evaluator initialisation (via pipeline + scorer)
# ------------------------------------------------------------------


class TestEvaluatorInit:

    def test_evaluator_init(self):
        """Pipeline and scorer should initialise without error."""
        scorer = Scorer(weights={"hallucination": 0.3, "bias": 0.3, "pii": 0.2, "toxicity": 0.2})
        pipeline = EvaluationPipeline(
            pillar_fns={},
            scorer=scorer,
            parallel=False,
        )
        assert pipeline is not None

    def test_evaluator_with_defaults(self):
        """Default pillar weights should be accepted by Scorer."""
        default_weights = {
            "hallucination": 0.30,
            "bias": 0.25,
            "pii": 0.25,
            "toxicity": 0.20,
        }
        scorer = Scorer(weights=default_weights)
        assert sum(scorer.weights.values()) == pytest.approx(1.0, abs=1e-6)


# ------------------------------------------------------------------
# Evaluate all pillars
# ------------------------------------------------------------------


class TestEvaluateAllPillars:

    def _make_pillar_fn(self, pillar_name: str, score: float):
        """Create a simple pillar evaluation function."""
        def fn(name, prompts):
            return PillarResult(
                pillar=name,
                score=score,
                test_count=len(prompts),
                pass_count=int(len(prompts) * score),
            )
        return fn

    def test_evaluate_all_pillars(self):
        """Running all pillars should produce results for each one."""
        scorer = Scorer(weights={
            "hallucination": 0.3, "bias": 0.3, "pii": 0.2, "toxicity": 0.2,
        })
        pillar_fns = {
            "hallucination": self._make_pillar_fn("hallucination", 0.9),
            "bias": self._make_pillar_fn("bias", 0.85),
            "pii": self._make_pillar_fn("pii", 0.95),
            "toxicity": self._make_pillar_fn("toxicity", 0.88),
        }
        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=False,
        )
        prompts = ["Test prompt 1", "Test prompt 2", "Test prompt 3"]
        results = pipeline.run(prompts)

        assert len(results) == 4
        assert "hallucination" in results
        assert "bias" in results
        assert results["hallucination"].score == 0.9
        assert results["pii"].test_count == 3

    def test_evaluate_single_pillar(self):
        """Running a single pillar should work correctly."""
        scorer = Scorer(weights={"bias": 1.0})
        pillar_fns = {
            "bias": self._make_pillar_fn("bias", 0.75),
        }
        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=False,
        )
        results = pipeline.run(["Single prompt test"])
        assert len(results) == 1
        assert results["bias"].score == 0.75

    def test_evaluate_parallel(self):
        """Parallel execution should produce the same results."""
        scorer = Scorer(weights={"hallucination": 0.5, "bias": 0.5})
        pillar_fns = {
            "hallucination": self._make_pillar_fn("hallucination", 0.8),
            "bias": self._make_pillar_fn("bias", 0.7),
        }
        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=True,
        )
        results = pipeline.run(["Prompt A", "Prompt B"])
        assert len(results) == 2
        assert results["hallucination"].score == 0.8
        assert results["bias"].score == 0.7


# ------------------------------------------------------------------
# Quick eval (compute_overall)
# ------------------------------------------------------------------


class TestQuickEval:

    def test_quick_eval(self):
        """compute_overall should return score, grade, and trust level."""
        scorer = Scorer(weights={"hallucination": 0.5, "bias": 0.5})
        pipeline = EvaluationPipeline(
            pillar_fns={}, scorer=scorer, parallel=False,
        )
        pillar_results = {
            "hallucination": PillarResult(pillar="hallucination", score=0.9),
            "bias": PillarResult(pillar="bias", score=0.8),
        }
        overall, grade, trust = pipeline.compute_overall(pillar_results)
        assert 0.8 <= overall <= 0.9
        assert grade in ("A", "B")
        assert trust in ("TRUSTED", "CONDITIONAL")


# ------------------------------------------------------------------
# Compare evaluators
# ------------------------------------------------------------------


class TestCompareEvaluators:

    def test_compare_evaluators(
        self, mock_openai_provider, mock_anthropic_provider
    ):
        """Two different providers should produce comparable result structures."""
        prompts = ["What is AI?"]
        openai_response = mock_openai_provider.generate(prompts[0])
        anthropic_response = mock_anthropic_provider.generate(prompts[0])

        assert isinstance(openai_response, str)
        assert isinstance(anthropic_response, str)
        assert len(openai_response) > 0
        assert len(anthropic_response) > 0


# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------


class TestInvalidInputs:

    def test_invalid_provider(self):
        """An unsupported provider name should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_provider_name("nonexistent_provider")

    def test_invalid_industry(self):
        """An unsupported industry name should raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_industry("aerospace")

    def test_valid_providers(self):
        """All built-in provider names should pass validation."""
        for provider in VALID_PROVIDERS:
            assert validate_provider_name(provider) == provider

    def test_valid_industries(self):
        """All built-in industry names should pass validation."""
        for industry in VALID_INDUSTRIES:
            assert validate_industry(industry) == industry


# ------------------------------------------------------------------
# Pipeline error handling
# ------------------------------------------------------------------


class TestPipelineErrorHandling:

    def test_pillar_failure_captured(self):
        """A failing pillar function should produce a zero-score result."""
        def failing_fn(name, prompts):
            raise RuntimeError("Simulated pillar failure")

        scorer = Scorer(weights={"broken": 1.0})
        pipeline = EvaluationPipeline(
            pillar_fns={"broken": failing_fn},
            scorer=scorer,
            parallel=False,
        )
        results = pipeline.run(["Test prompt"])
        assert results["broken"].score == 0.0
        assert "error" in results["broken"].details
