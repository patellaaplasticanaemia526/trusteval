# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Unit tests for hallucination detection metric functions."""

from __future__ import annotations

import pytest

from trusteval.pillars.hallucination.metrics import (
    confidence_calibration,
    consistency_score,
    factual_accuracy,
    hallucination_rate,
)


# ------------------------------------------------------------------
# Factual accuracy
# ------------------------------------------------------------------


class TestFactualAccuracy:

    def test_factual_accuracy_correct(self):
        """Response matching ground truth should have high accuracy."""
        response = (
            "The capital of France is Paris. Paris is the largest city in "
            "France and has been the capital since the 10th century."
        )
        truth = "The capital of France is Paris, the largest city in France."
        score = factual_accuracy(response, truth)
        assert score >= 0.5  # F1-based scoring; high overlap expected

    def test_factual_accuracy_wrong(self):
        """Response contradicting ground truth should score low."""
        response = (
            "The capital of France is Lyon. Lyon has been the political "
            "center since the 15th century."
        )
        truth = "The capital of France is Paris."
        score = factual_accuracy(response, truth)
        # Some overlap on common words, but key fact differs
        assert score < 0.8

    def test_factual_accuracy_empty_response(self):
        """Empty response should yield 0.0 accuracy."""
        assert factual_accuracy("", "The answer is 42.") == 0.0

    def test_factual_accuracy_empty_truth(self):
        """Empty ground truth should yield 0.0."""
        assert factual_accuracy("Some response text.", "") == 0.0

    def test_factual_accuracy_identical(self):
        """Identical strings should yield accuracy of 1.0."""
        text = "The boiling point of water is 100 degrees Celsius."
        assert factual_accuracy(text, text) == 1.0

    def test_factual_accuracy_partial_overlap(self):
        """Partial overlap should yield a moderate score."""
        response = "Water boils at 100 degrees. The sky is blue. Trees are green."
        truth = "Water boils at 100 degrees Celsius at sea level."
        score = factual_accuracy(response, truth)
        assert 0.2 < score < 0.9


# ------------------------------------------------------------------
# Hallucination rate
# ------------------------------------------------------------------


class TestHallucinationRate:

    def test_hallucination_detection(self):
        """Hallucinated content should produce a high hallucination rate."""
        responses = [
            "The Eiffel Tower was built in 1920 by Jean Nouvel.",
            "Napoleon was the first president of the United States.",
        ]
        truths = [
            "The Eiffel Tower was built from 1887 to 1889 by Gustave Eiffel.",
            "George Washington was the first president of the United States.",
        ]
        rate = hallucination_rate(responses, truths)
        assert rate > 0.2  # Partial word overlap lowers rate slightly

    def test_no_hallucination(self):
        """Accurate responses should have low hallucination rate."""
        text = "The capital of France is Paris."
        rate = hallucination_rate([text], [text])
        assert rate == 0.0

    def test_hallucination_rate_empty(self):
        """Empty inputs should yield rate of 1.0."""
        assert hallucination_rate([], []) == 1.0

    def test_hallucination_rate_mixed(self):
        """Mix of accurate and hallucinated should yield moderate rate."""
        responses = [
            "Water boils at 100 degrees Celsius.",
            "The moon is made of green cheese according to scientists.",
        ]
        truths = [
            "Water boils at 100 degrees Celsius at sea level.",
            "The moon is a natural satellite of Earth composed of rock.",
        ]
        rate = hallucination_rate(responses, truths)
        assert 0.1 < rate < 0.9


# ------------------------------------------------------------------
# Confidence calibration
# ------------------------------------------------------------------


class TestConfidenceCalibration:

    def test_confidence_calibration_balanced(self):
        """Well-calibrated text with hedging should score high."""
        text = (
            "I believe the answer is approximately 42, although I am not "
            "entirely sure. It is possible that there are exceptions, and "
            "I would need to verify this further."
        )
        score = confidence_calibration(text)
        assert score >= 0.5

    def test_confidence_calibration_overconfident(self):
        """Overconfident text without hedging should score lower."""
        text = (
            "It is definitely true. Absolutely, without a doubt, this is "
            "certainly the case. Obviously everyone knows this fact."
        )
        score = confidence_calibration(text)
        assert score < 0.4

    def test_confidence_calibration_neutral(self):
        """Text without any confidence signals should return 0.5."""
        text = "The system processes data using algorithms and heuristics."
        score = confidence_calibration(text)
        assert score == 0.5

    def test_confidence_calibration_uncertain(self):
        """Very uncertain text should score well on calibration."""
        text = (
            "I'm not sure about this. Perhaps it could be one thing, "
            "or possibly another. As far as I know, sources differ on "
            "this topic."
        )
        score = confidence_calibration(text)
        assert score >= 0.7


# ------------------------------------------------------------------
# Consistency
# ------------------------------------------------------------------


class TestConsistency:

    def test_consistency_high(self):
        """Identical responses should have consistency of 1.0."""
        responses = [
            "The capital of France is Paris.",
            "The capital of France is Paris.",
            "The capital of France is Paris.",
        ]
        assert consistency_score(responses) == 1.0

    def test_consistency_low(self):
        """Very different responses should have lower consistency."""
        responses = [
            "Apples are red fruits that grow on trees in orchards.",
            "Quantum mechanics describes subatomic particle behavior.",
            "The stock market opened higher today on strong earnings.",
        ]
        score = consistency_score(responses)
        assert score < 0.5

    def test_consistency_single_response(self):
        """Single response should return 1.0."""
        assert consistency_score(["Only one response"]) == 1.0

    def test_consistency_similar_responses(self):
        """Similar but not identical responses should score high."""
        responses = [
            "Paris is the capital of France.",
            "France's capital is Paris.",
            "The capital city of France is Paris.",
        ]
        score = consistency_score(responses)
        assert score >= 0.5


# ------------------------------------------------------------------
# Source grounding (using factual_accuracy as proxy)
# ------------------------------------------------------------------


class TestSourceGrounding:

    def test_source_grounding_with_reference(self):
        """Response grounded in source material should score high."""
        source = (
            "Python was created by Guido van Rossum and first released "
            "in 1991. It emphasizes code readability."
        )
        response = (
            "Python is a programming language created by Guido van Rossum, "
            "first released in 1991, known for its emphasis on readability."
        )
        score = factual_accuracy(response, source)
        assert score >= 0.5  # High semantic overlap, F1 word-level

    def test_source_grounding_ungrounded(self):
        """Response with fabricated claims should score lower."""
        source = "Python was created by Guido van Rossum in 1991."
        response = (
            "Python was invented by Linus Torvalds in 2005 as a systems "
            "programming language designed for kernel development."
        )
        score = factual_accuracy(response, source)
        assert score < 0.5
