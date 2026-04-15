"""Tests for verdict generation module."""
import pytest
from src.engine.verdict import (
    VerdictResult,
    DigitFlag,
    compute_mad,
    authenticity_score_from_mad,
    confidence_from_p_value,
    p_value_to_verdict,
    generate_verdict,
    generate_combined_verdict
)


class TestComputeMAD:
    """Tests for MAD calculation."""
    
    def test_mad_zero_for_identical_distributions(self):
        expected = [0.3, 0.2, 0.1, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03]
        observed = expected.copy()
        mad = compute_mad(expected, observed)
        assert mad == 0.0
    
    def test_mad_positive_for_different_distributions(self):
        expected = [0.3, 0.2, 0.1, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03]
        # Uniform distribution
        observed = [0.111] * 9
        mad = compute_mad(expected, observed)
        assert mad > 0.0
    
    def test_mad_handles_empty(self):
        mad = compute_mad([], [])
        assert mad == 0.0


class TestAuthenticityScore:
    """Tests for authenticity score calculation."""
    
    def test_perfect_match_gives_100(self):
        score = authenticity_score_from_mad(0.0)
        assert score == 100
    
    def test_max_deviation_gives_low_score(self):
        score = authenticity_score_from_mad(0.06)
        assert score <= 10
    
    def test_score_bounded_0_100(self):
        assert authenticity_score_from_mad(-0.1) == 100  # Clamped to 0
        assert authenticity_score_from_mad(1.0) == 0  # Clamped to max


class TestConfidenceFromPValue:
    """Tests for confidence band calculation."""
    
    def test_high_confidence_high_p_value(self):
        conf, band = confidence_from_p_value(0.15)
        assert conf == 85
        assert band == "High"
    
    def test_medium_confidence_at_05(self):
        conf, band = confidence_from_p_value(0.05)
        assert conf == 70
        assert band == "Medium"
    
    def test_low_confidence_suspicious(self):
        conf, band = confidence_from_p_value(0.02)
        assert conf == 50
        assert band == "Low"
    
    def test_very_low_confidence_highly_suspicious(self):
        conf, band = confidence_from_p_value(0.005)
        assert conf == 30
        assert band == "Very Low"


class TestPValueToVerdict:
    """Tests for verdict string generation."""
    
    def test_natural_for_high_p_value(self):
        verdict, code = p_value_to_verdict(0.1)
        assert verdict == "Likely Natural"
        assert code == "natural"
    
    def test_suspicious_for_moderate_p_value(self):
        verdict, code = p_value_to_verdict(0.03)
        assert verdict == "Suspicious"
        assert code == "suspicious"
    
    def test_highly_suspicious_for_low_p_value(self):
        verdict, code = p_value_to_verdict(0.005)
        assert verdict == "Highly Suspicious"
        assert code == "highly_suspicious"


class TestGenerateVerdict:
    """Tests for full verdict generation."""
    
    def test_insufficient_data(self):
        result = generate_verdict(
            expected=[0.3],
            observed=[0.3],
            chi_squared=0,
            p_value=1.0,
            sample_size=5,  # Less than 30
            digit_position=1
        )
        assert result.verdict == "Insufficient Data"
        assert result.verdict_code == "insufficient_data"
        assert result.authenticity_score == 0
    
    def test_natural_data(self):
        # Perfect Benford distribution
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        observed = expected.copy()  # Perfect match
        chi_sq = 0.0
        p_val = 0.99
        
        result = generate_verdict(
            expected=expected,
            observed=observed,
            chi_squared=chi_sq,
            p_value=p_val,
            sample_size=1000,
            digit_position=1
        )
        
        assert result.verdict == "Likely Natural"
        assert result.authenticity_score == 100
        assert len(result.flags) == 0
    
    def test_flag_7_overrepresentation(self):
        # Simulate data where 7 appears much more than expected
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        # Make 7 appear 18% instead of ~5.8%
        observed = [0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.18, 0.03, 0.01]
        
        result = generate_verdict(
            expected=expected,
            observed=observed,
            chi_squared=20.0,  # High chi-squared
            p_value=0.01,  # Just under threshold
            sample_size=500,
            digit_position=1
        )
        
        assert result.verdict_code in ("suspicious", "highly_suspicious")
        # Should have flagged the 7 overrepresentation
        flag_7s = [f for f in result.flags if f.digit == 7]
        assert len(flag_7s) > 0
    
    def test_verdict_result_to_dict(self):
        result = VerdictResult(
            verdict="Likely Natural",
            verdict_code="natural",
            authenticity_score=85,
            confidence_percent=70,
            confidence_band="Medium",
            flags=[],
            explanation="Test explanation",
            raw_chi_squared=5.0,
            raw_p_value=0.5,
            raw_mad=0.01,
            sample_size=100
        )
        
        d = result.to_dict()
        assert d["verdict"] == "Likely Natural"
        assert d["authenticity_score"] == 85
        assert d["flags"] == []


class TestGenerateCombinedVerdict:
    """Tests for combined verdict generation."""
    
    def test_combines_first_and_second_digit(self):
        first_result = {
            "expected": [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046],
            "observed": [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046],
            "chi_squared": 0.1,
            "p_value": 0.99,
            "sample_size": 1000
        }
        second_result = {
            "expected": [0.120, 0.114, 0.109, 0.104, 0.100, 0.096, 0.093, 0.090, 0.088, 0.085],
            "observed": [0.120, 0.114, 0.109, 0.104, 0.100, 0.096, 0.093, 0.090, 0.088, 0.085],
            "chi_squared": 0.1,
            "p_value": 0.99,
            "sample_size": 1000
        }
        
        result = generate_combined_verdict(first_result, second_result)
        
        assert "verdict" in result
        assert "verdict_code" in result
        assert "second_digit_verdict" in result
        assert result["verdict"] == "Likely Natural"
    
    def test_second_digit_affects_verdict(self):
        # First digit normal
        first_result = {
            "expected": [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046],
            "observed": [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046],
            "chi_squared": 0.1,
            "p_value": 0.99,
            "sample_size": 1000
        }
        # Second digit suspicious
        second_result = {
            "expected": [0.120, 0.114, 0.109, 0.104, 0.100, 0.096, 0.093, 0.090, 0.088, 0.085],
            "observed": [0.30, 0.10, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],  # Very suspicious
            "chi_squared": 50.0,
            "p_value": 0.001,
            "sample_size": 1000
        }
        
        result = generate_combined_verdict(first_result, second_result)
        
        # If second digit is suspicious and first is natural, verdict should be suspicious
        assert result["verdict_code"] in ("suspicious", "highly_suspicious") or result["verdict"] != "Likely Natural"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])