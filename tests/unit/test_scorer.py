# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Unit tests for the Scorer, grade computation, and trust-level mapping."""

from __future__ import annotations

import pytest

from trusteval.core.scorer import Scorer, compute_grade, compute_trust_level
from trusteval.utils.exceptions import ScoringError, ValidationError


# ------------------------------------------------------------------
# Grade computation
# ------------------------------------------------------------------


class TestComputeGrade:

    def test_grade_a(self):
        """Score >= 0.85 should yield grade A."""
        assert compute_grade(0.85) == "A"
        assert compute_grade(0.90) == "A"
        assert compute_grade(1.0) == "A"

    def test_grade_b(self):
        """Score in [0.70, 0.85) should yield grade B."""
        assert compute_grade(0.70) == "B"
        assert compute_grade(0.75) == "B"
        assert compute_grade(0.84) == "B"

    def test_grade_c(self):
        """Score in [0.55, 0.70) should yield grade C."""
        assert compute_grade(0.55) == "C"
        assert compute_grade(0.60) == "C"
        assert compute_grade(0.69) == "C"

    def test_grade_d(self):
        """Score in [0.40, 0.55) should yield grade D."""
        assert compute_grade(0.40) == "D"
        assert compute_grade(0.50) == "D"
        assert compute_grade(0.54) == "D"

    def test_grade_f(self):
        """Score in [0.0, 0.40) should yield grade F."""
        assert compute_grade(0.0) == "F"
        assert compute_grade(0.20) == "F"
        assert compute_grade(0.39) == "F"

    def test_grade_boundary_exact(self):
        """Boundary values should map to the higher grade."""
        assert compute_grade(0.85) == "A"
        assert compute_grade(0.70) == "B"
        assert compute_grade(0.55) == "C"
        assert compute_grade(0.40) == "D"

    def test_grade_invalid_score(self):
        """Score outside [0, 1] should raise ValidationError."""
        with pytest.raises(ValidationError):
            compute_grade(1.5)
        with pytest.raises(ValidationError):
            compute_grade(-0.1)


# ------------------------------------------------------------------
# Trust level
# ------------------------------------------------------------------


class TestTrustLevel:

    def test_trust_level_trusted(self):
        """Grades A and B should map to TRUSTED."""
        assert compute_trust_level("A") == "TRUSTED"
        assert compute_trust_level("B") == "TRUSTED"

    def test_trust_level_conditional(self):
        """Grades C and D should map to CONDITIONAL."""
        assert compute_trust_level("C") == "CONDITIONAL"
        assert compute_trust_level("D") == "CONDITIONAL"

    def test_trust_level_untrusted(self):
        """Grade F should map to UNTRUSTED."""
        assert compute_trust_level("F") == "UNTRUSTED"

    def test_trust_level_case_insensitive(self):
        """Trust level lookup should be case-insensitive."""
        assert compute_trust_level("a") == "TRUSTED"
        assert compute_trust_level("f") == "UNTRUSTED"

    def test_trust_level_invalid_grade(self):
        """Unknown grade should raise ScoringError."""
        with pytest.raises(ScoringError):
            compute_trust_level("Z")
        with pytest.raises(ScoringError):
            compute_trust_level("X")


# ------------------------------------------------------------------
# Weighted average
# ------------------------------------------------------------------


class TestWeightedAverage:

    def test_weighted_average(self):
        """Weighted average should respect pillar weights."""
        scorer = Scorer(weights={"a": 0.5, "b": 0.5})
        result = scorer.weighted_average({"a": 0.8, "b": 0.6})
        assert result == pytest.approx(0.7, abs=1e-4)

    def test_weighted_average_unequal_weights(self):
        """Unequal weights should shift the average toward the heavier pillar."""
        scorer = Scorer(weights={"a": 0.75, "b": 0.25})
        result = scorer.weighted_average({"a": 1.0, "b": 0.0})
        assert result == pytest.approx(0.75, abs=1e-4)

    def test_weighted_average_single_pillar(self):
        """Single pillar should return its own score."""
        scorer = Scorer(weights={"only": 1.0})
        result = scorer.weighted_average({"only": 0.42})
        assert result == pytest.approx(0.42, abs=1e-4)

    def test_weighted_average_partial_overlap(self):
        """Only overlapping pillars should contribute, with re-normalised weights."""
        scorer = Scorer(weights={"a": 0.5, "b": 0.3, "c": 0.2})
        # Only "a" and "c" provided — weights re-normalise over these two
        result = scorer.weighted_average({"a": 1.0, "c": 0.5})
        # a_weight = 0.5/(0.5+0.2) = 5/7, c_weight = 0.2/(0.5+0.2) = 2/7
        expected = (5 / 7) * 1.0 + (2 / 7) * 0.5
        assert result == pytest.approx(expected, abs=1e-4)

    def test_weighted_average_no_overlap(self):
        """No overlap between scores and weights should raise ScoringError."""
        scorer = Scorer(weights={"a": 1.0})
        with pytest.raises(ScoringError):
            scorer.weighted_average({"b": 0.5})


# ------------------------------------------------------------------
# Scorer initialisation
# ------------------------------------------------------------------


class TestScorerInit:

    def test_empty_weights_raises(self):
        """Empty weights dict should raise ScoringError."""
        with pytest.raises(ScoringError):
            Scorer(weights={})

    def test_negative_weight_raises(self):
        """Negative weight should raise ScoringError."""
        with pytest.raises(ScoringError):
            Scorer(weights={"a": -1.0})

    def test_weights_normalised(self):
        """Weights should be normalised to sum to 1.0."""
        scorer = Scorer(weights={"a": 3.0, "b": 7.0})
        assert scorer.weights["a"] == pytest.approx(0.3, abs=1e-6)
        assert scorer.weights["b"] == pytest.approx(0.7, abs=1e-6)

    def test_scorer_grade_method(self):
        """Scorer.grade should return the correct letter grade."""
        scorer = Scorer(weights={"x": 1.0})
        assert scorer.grade({"x": 0.9}) == "A"
        assert scorer.grade({"x": 0.5}) == "D"

    def test_scorer_trust_level_method(self):
        """Scorer.trust_level should return the correct trust level."""
        scorer = Scorer(weights={"x": 1.0})
        assert scorer.trust_level({"x": 0.9}) == "TRUSTED"
        assert scorer.trust_level({"x": 0.3}) == "UNTRUSTED"
