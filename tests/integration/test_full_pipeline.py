# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""End-to-end integration tests for the full evaluation pipeline.

All LLM calls are mocked. These tests verify that the pipeline correctly
orchestrates pillar evaluations, aggregates scores, and produces a
complete EvaluationResult with export capabilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from trusteval.core.pipeline import EvaluationPipeline
from trusteval.core.result import EvaluationResult, PillarResult
from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level
from trusteval.pillars.bias.detector import BiasDetector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pillar_fn(pillar_name: str, score: float, details: Dict[str, Any] | None = None):
    """Create a deterministic pillar evaluation function."""
    def fn(name: str, prompts: List[str]) -> PillarResult:
        n = len(prompts)
        pass_count = int(n * score)
        return PillarResult(
            pillar=name,
            score=score,
            test_count=n,
            pass_count=pass_count,
            details=details or {"metric": f"{pillar_name}_metric", "value": score},
        )
    return fn


# ==================================================================
# Full pipeline tests
# ==================================================================


class TestFullEvaluationPipeline:

    def test_full_evaluation_pipeline(self):
        """Full pipeline should run all pillars and compute overall results."""
        weights = {
            "hallucination": 0.30,
            "bias": 0.25,
            "pii": 0.25,
            "toxicity": 0.20,
        }
        scorer = Scorer(weights=weights)

        pillar_fns = {
            "hallucination": _make_pillar_fn("hallucination", 0.90, {
                "factual_accuracy": 0.92, "consistency": 0.88,
            }),
            "bias": _make_pillar_fn("bias", 0.85, {
                "stereotype_score": 0.05, "parity": 0.90,
            }),
            "pii": _make_pillar_fn("pii", 0.95, {
                "pii_echo_rate": 0.0, "types_detected": [],
            }),
            "toxicity": _make_pillar_fn("toxicity", 0.88, {
                "hate_speech": 0.95, "profanity": 0.92,
            }),
        }

        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns,
            scorer=scorer,
            parallel=False,
        )

        prompts = [
            "Describe the ideal CEO.",
            "What is the capital of France?",
            "How do I protect my personal data?",
            "Tell me about different cultures.",
            "What are the benefits of exercise?",
        ]

        pillar_results = pipeline.run(prompts)

        # All four pillars should have results
        assert len(pillar_results) == 4
        for name in weights:
            assert name in pillar_results
            assert pillar_results[name].test_count == 5
            assert pillar_results[name].score > 0

        # Compute overall
        overall, grade, trust = pipeline.compute_overall(pillar_results)
        assert 0.8 <= overall <= 1.0
        assert grade in ("A", "B")
        assert trust == "TRUSTED"

        # Build full EvaluationResult
        result = EvaluationResult(
            provider="openai",
            model="gpt-4o",
            industry="healthcare",
            overall_score=overall,
            overall_grade=grade,
            trust_level=trust,
            pillars=pillar_results,
            metadata={"mode": "integration_test"},
            duration_seconds=5.0,
        )

        assert result.overall_score > 0
        assert result.trust_level == "TRUSTED"
        assert len(result.pillars) == 4

    def test_full_pipeline_sequential_vs_parallel(self):
        """Sequential and parallel execution should produce equivalent results."""
        weights = {"hallucination": 0.5, "bias": 0.5}
        scorer = Scorer(weights=weights)

        pillar_fns = {
            "hallucination": _make_pillar_fn("hallucination", 0.85),
            "bias": _make_pillar_fn("bias", 0.75),
        }

        prompts = ["Test prompt 1", "Test prompt 2"]

        seq_pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=False,
        )
        par_pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=True,
        )

        seq_results = seq_pipeline.run(prompts)
        par_results = par_pipeline.run(prompts)

        for name in weights:
            assert seq_results[name].score == par_results[name].score


# ==================================================================
# Pipeline with export
# ==================================================================


class TestPipelineWithExport:

    def test_pipeline_with_export(self, tmp_path):
        """Pipeline results should be exportable as JSON."""
        scorer = Scorer(weights={"hallucination": 0.5, "bias": 0.5})
        pillar_fns = {
            "hallucination": _make_pillar_fn("hallucination", 0.88),
            "bias": _make_pillar_fn("bias", 0.82),
        }
        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=False,
        )

        pillar_results = pipeline.run(["Prompt 1", "Prompt 2", "Prompt 3"])
        overall, grade, trust = pipeline.compute_overall(pillar_results)

        result = EvaluationResult(
            provider="openai",
            model="gpt-4o",
            industry="general",
            overall_score=overall,
            overall_grade=grade,
            trust_level=trust,
            pillars=pillar_results,
            duration_seconds=3.5,
        )

        # Export to JSON
        json_path = tmp_path / "eval_result.json"
        exported = result.export(json_path, format="json")
        assert exported.is_file()

        # Verify JSON content
        data = json.loads(exported.read_text(encoding="utf-8"))
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4o"
        assert "hallucination" in data["pillars"]
        assert "bias" in data["pillars"]
        assert data["overall_score"] > 0

    def test_pipeline_with_html_export(self, tmp_path):
        """Pipeline results should be exportable as HTML."""
        scorer = Scorer(weights={"hallucination": 1.0})
        pillar_fns = {"hallucination": _make_pillar_fn("hallucination", 0.9)}
        pipeline = EvaluationPipeline(
            pillar_fns=pillar_fns, scorer=scorer, parallel=False,
        )

        pillar_results = pipeline.run(["Test"])
        overall, grade, trust = pipeline.compute_overall(pillar_results)

        result = EvaluationResult(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            industry="finance",
            overall_score=overall,
            pillars=pillar_results,
        )

        html_path = tmp_path / "report.html"
        exported = result.export(html_path, format="html")
        assert exported.is_file()
        content = exported.read_text(encoding="utf-8")
        assert "TrustEval" in content
        assert "hallucination" in content

    def test_result_summary(self):
        """summary() should produce a readable multi-line report."""
        result = EvaluationResult(
            provider="openai",
            model="gpt-4o",
            industry="healthcare",
            overall_score=0.88,
            overall_grade="A",
            trust_level="TRUSTED",
            pillars={
                "hallucination": PillarResult(
                    pillar="hallucination", score=0.90, test_count=10, pass_count=9
                ),
            },
            duration_seconds=45.2,
        )
        summary = result.summary()
        assert "TrustEval" in summary
        assert "openai" in summary
        assert "TRUSTED" in summary
        assert "hallucination" in summary


# ==================================================================
# Compare models
# ==================================================================


class TestPipelineCompareModels:

    def test_pipeline_compare_models(
        self, mock_openai_provider, mock_anthropic_provider
    ):
        """Evaluating two different providers should produce comparable structures."""
        weights = {"hallucination": 0.5, "bias": 0.5}
        scorer = Scorer(weights=weights)

        # Simulate evaluation for each provider
        results = {}
        for provider_mock, provider_name, model_name in [
            (mock_openai_provider, "openai", "gpt-4o"),
            (mock_anthropic_provider, "anthropic", "claude-3-sonnet-20240229"),
        ]:
            pillar_fns = {
                "hallucination": _make_pillar_fn("hallucination", 0.85),
                "bias": _make_pillar_fn("bias", 0.80),
            }
            pipeline = EvaluationPipeline(
                pillar_fns=pillar_fns, scorer=scorer, parallel=False,
            )

            pillar_results = pipeline.run(["Compare prompt"])
            overall, grade, trust = pipeline.compute_overall(pillar_results)

            results[provider_name] = EvaluationResult(
                provider=provider_name,
                model=model_name,
                industry="general",
                overall_score=overall,
                overall_grade=grade,
                trust_level=trust,
                pillars=pillar_results,
            )

        # Both results should have the same structure
        assert "openai" in results
        assert "anthropic" in results
        assert results["openai"].overall_score == results["anthropic"].overall_score
        assert len(results["openai"].pillars) == len(results["anthropic"].pillars)

        # Both should be serialisable
        for name, result in results.items():
            data = result.to_dict()
            assert data["provider"] == name
            assert "pillars" in data
            json_str = result.to_json()
            parsed = json.loads(json_str)
            assert parsed["overall_score"] > 0

    def test_pipeline_compare_different_scores(self):
        """Models with different scores should produce different grades."""
        scorer = Scorer(weights={"hallucination": 1.0})

        # Good model
        good_pipeline = EvaluationPipeline(
            pillar_fns={"hallucination": _make_pillar_fn("hallucination", 0.92)},
            scorer=scorer,
            parallel=False,
        )
        good_results = good_pipeline.run(["Test"])
        good_overall, good_grade, good_trust = good_pipeline.compute_overall(good_results)

        # Weak model
        weak_pipeline = EvaluationPipeline(
            pillar_fns={"hallucination": _make_pillar_fn("hallucination", 0.35)},
            scorer=scorer,
            parallel=False,
        )
        weak_results = weak_pipeline.run(["Test"])
        weak_overall, weak_grade, weak_trust = weak_pipeline.compute_overall(weak_results)

        assert good_overall > weak_overall
        assert good_grade == "A"
        assert weak_grade == "F"
        assert good_trust == "TRUSTED"
        assert weak_trust == "UNTRUSTED"


# ==================================================================
# Bias integration in pipeline
# ==================================================================


class TestBiasIntegrationInPipeline:

    def test_bias_detector_in_pipeline(self):
        """BiasDetector should integrate cleanly as a pillar function."""
        detector = BiasDetector()

        def bias_eval_fn(name: str, prompts: List[str]) -> PillarResult:
            scores = []
            for prompt in prompts:
                # Use a neutral mock response
                result = detector.detect(
                    prompt=prompt,
                    response=(
                        "The ideal candidate has strong leadership skills, "
                        "strategic vision, and the ability to inspire teams."
                    ),
                )
                scores.append(result["overall_score"])
            avg_score = sum(scores) / len(scores) if scores else 0.0
            return PillarResult(
                pillar=name,
                score=avg_score,
                test_count=len(prompts),
                pass_count=sum(1 for s in scores if s >= 0.55),
            )

        scorer = Scorer(weights={"bias": 1.0})
        pipeline = EvaluationPipeline(
            pillar_fns={"bias": bias_eval_fn},
            scorer=scorer,
            parallel=False,
        )
        results = pipeline.run(["Describe the ideal CEO.", "Describe a leader."])
        assert results["bias"].score > 0.5
        assert results["bias"].test_count == 2
