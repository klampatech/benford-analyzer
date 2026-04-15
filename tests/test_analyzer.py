"""Tests for the Benford analyzer module."""
import pytest
import math

from src.engine.analyzer import (
    benford_expected_probability,
    get_expected_benford_frequencies,
    get_leading_digit,
    get_leading_digits,
    compute_mad,
    compute_chi_squared,
    chi_squared_critical_value,
    compute_p_value,
    analyze_single_position,
    analyze_benford,
    analyze_text,
    BenfordAnalysisResult
)


class TestBenfordExpectedProbability:
    """Tests for Benford expected probability calculation."""
    
    def test_first_digit_probabilities_sum_to_one(self):
        """Test that first digit probabilities sum to approximately 1."""
        total = sum(benford_expected_probability(d, 1) for d in range(1, 10))
        assert abs(total - 1.0) < 0.001
    
    def test_known_first_digit_probabilities(self):
        """Test against known Benford probabilities for first digit."""
        # P(1) = log10(2) ≈ 0.301
        assert abs(benford_expected_probability(1, 1) - 0.301) < 0.001
        # P(9) = log10(10/9) ≈ 0.046
        assert abs(benford_expected_probability(9, 1) - 0.046) < 0.001
    
    def test_second_digit_probabilities_sum_to_one(self):
        """Test that second digit probabilities sum to approximately 1."""
        total = sum(benford_expected_probability(d, 2) for d in range(0, 10))
        assert abs(total - 1.0) < 0.001
    
    def test_invalid_digit_returns_zero(self):
        """Test that invalid digit values return 0."""
        assert benford_expected_probability(0, 1) == 0.0  # First digit can't be 0
        assert benford_expected_probability(10, 1) == 0.0  # Out of range
        assert benford_expected_probability(-1, 1) == 0.0  # Negative


class TestGetExpectedBenfordFrequencies:
    """Tests for expected Benford frequencies generator."""
    
    def test_first_digit_frequencies(self):
        """Test first digit frequencies (9 values for 1-9)."""
        freq = get_expected_benford_frequencies(1)
        assert len(freq) == 9
        assert abs(sum(freq) - 1.0) < 0.001
    
    def test_second_digit_frequencies(self):
        """Test second digit frequencies (10 values for 0-9)."""
        freq = get_expected_benford_frequencies(2)
        assert len(freq) == 10
        assert abs(sum(freq) - 1.0) < 0.001


class TestGetLeadingDigit:
    """Tests for leading digit extraction."""
    
    def test_first_digit(self):
        """Test first digit extraction."""
        assert get_leading_digit(12345, 1) == 1
        assert get_leading_digit(9876, 1) == 9
        assert get_leading_digit(5, 1) == 5
    
    def test_second_digit(self):
        """Test second digit extraction."""
        assert get_leading_digit(12345, 2) == 2
        assert get_leading_digit(9876, 2) == 8
    
    def test_third_digit(self):
        """Test third digit extraction."""
        assert get_leading_digit(12345, 3) == 3
        assert get_leading_digit(9876, 3) == 7
    
    def test_position_beyond_length(self):
        """Test extraction when position exceeds digit count."""
        assert get_leading_digit(123, 5) == -1
        assert get_leading_digit(5, 2) == -1
    
    def test_zero_number(self):
        """Test that zero returns -1."""
        assert get_leading_digit(0, 1) == -1
    
    def test_negative_numbers(self):
        """Test that negative numbers use absolute value."""
        assert get_leading_digit(-12345, 1) == 1
        assert get_leading_digit(-12345, 2) == 2


class TestGetLeadingDigits:
    """Tests for batch leading digit extraction."""
    
    def test_extracts_first_digits(self):
        """Test extraction of first digits from list."""
        numbers = [123, 456, 789, 100]
        digits = get_leading_digits(numbers, 1)
        assert 1 in digits
        assert 4 in digits
        assert 7 in digits
    
    def test_handles_short_numbers(self):
        """Test that short numbers are skipped."""
        numbers = [5, 12, 123]
        digits = get_leading_digits(numbers, 3)
        # Only 123 has a 3rd digit
        assert len(digits) == 1
        assert 3 in digits
    
    def test_empty_list(self):
        """Test with empty list."""
        digits = get_leading_digits([], 1)
        assert digits == []


class TestComputeMad:
    """Tests for Mean Absolute Deviation computation."""
    
    def test_perfect_match(self):
        """Test MAD with perfect match."""
        expected = [0.3, 0.2, 0.1]
        observed = [0.3, 0.2, 0.1]
        mad = compute_mad(expected, observed)
        assert mad == 0.0
    
    def test_known_deviation(self):
        """Test MAD with known deviation."""
        expected = [0.3, 0.2, 0.1]
        observed = [0.35, 0.2, 0.05]
        mad = compute_mad(expected, observed)
        # MAD = (|0.35-0.3| + |0.2-0.2| + |0.05-0.1|) / 3 = 0.05/3 ≈ 0.0167
        assert abs(mad - 0.0333) < 0.01
    
    def test_empty_lists(self):
        """Test MAD with empty lists."""
        mad = compute_mad([], [])
        assert mad == 0.0
    
    def test_different_lengths(self):
        """Test MAD with mismatched lengths."""
        mad = compute_mad([0.3, 0.2], [0.3])
        assert mad == 0.0


class TestComputeChiSquared:
    """Tests for chi-squared calculation."""
    
    def test_zero_difference(self):
        """Test chi-squared with no difference."""
        expected = [0.3, 0.3, 0.4]
        observed = [0.3, 0.3, 0.4]
        chi_sq = compute_chi_squared(expected, observed, 100)
        assert chi_sq == 0.0
    
    def test_known_difference(self):
        """Test chi-squared with known difference."""
        # Count-based chi-squared: sum((O-E)²/E) where O and E are counts
        expected = [0.5, 0.5]
        observed = [0.6, 0.4]
        chi_sq = compute_chi_squared(expected, observed, 100)
        # With n=100: exp counts = [50, 50], obs counts = [60, 40]
        # chi_sq = (60-50)²/50 + (40-50)²/50 = 100/50 + 100/50 = 2 + 2 = 4.0
        assert abs(chi_sq - 4.0) < 0.001
    
    def test_handles_zero_expected(self):
        """Test that chi-squared handles zero expected values."""
        expected = [0.5, 0.0, 0.5]
        observed = [0.5, 0.0, 0.5]
        chi_sq = compute_chi_squared(expected, observed, 100)
        assert chi_sq == 0.0


class TestChiSquaredCriticalValue:
    """Tests for chi-squared critical value."""
    
    def test_common_values(self):
        """Test common critical values."""
        # df=8, alpha=0.05
        critical = chi_squared_critical_value(8, 0.05)
        assert abs(critical - 15.51) < 0.1
        
        # df=9, alpha=0.05
        critical = chi_squared_critical_value(9, 0.05)
        assert abs(critical - 16.92) < 0.1


class TestComputePValue:
    """Tests for p-value calculation."""
    
    def test_low_chi_squared_gives_high_p_value(self):
        """Test that low chi-squared gives high p-value."""
        p = compute_p_value(5.0, 8)  # Low chi-squared
        assert p > 0.5
    
    def test_high_chi_squared_gives_low_p_value(self):
        """Test that high chi-squared gives low p-value."""
        p = compute_p_value(25.0, 8)  # High chi-squared
        assert p < 0.05


class TestAnalyzeSinglePosition:
    """Tests for single position analysis."""
    
    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        numbers = [1, 2, 3, 4, 5]
        result = analyze_single_position(numbers, 1)
        
        assert result.verdict == "Insufficient Data"
        assert "Need at least 30" in result.explanation
    
    def test_normal_benford_data(self):
        """Test analysis of data that follows Benford distribution."""
        # Generate data that follows Benford
        numbers = []
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        for digit, freq in enumerate(expected, 1):
            count = int(freq * 1000)
            numbers.extend([digit * 1000 + i for i in range(count)])
        
        result = analyze_single_position(numbers, 1)
        
        assert result.verdict == "NORMAL"
        assert not result.is_suspicious
        assert result.sample_size >= 30
        assert result.p_value > 0.05
    
    def test_skewed_data_suspicious(self):
        """Test that heavily skewed data is flagged as suspicious."""
        # Create data with heavy first-digit skew
        numbers = []
        numbers.extend([1 * 1000 + i for i in range(500)])  # 50% start with 1
        numbers.extend([5 * 1000 + i for i in range(150)])
        numbers.extend([9 * 1000 + i for i in range(100)])
        numbers.extend([2 * 1000 + i for i in range(100)])
        numbers.extend([3 * 1000 + i for i in range(50)])
        numbers.extend([4 * 1000 + i for i in range(50)])
        numbers.extend([6 * 1000 + i for i in range(30)])
        numbers.extend([7 * 1000 + i for i in range(30)])
        numbers.extend([8 * 1000 + i for i in range(20)])
        
        result = analyze_single_position(numbers, 1)
        
        assert result.is_suspicious
        assert result.verdict == "SUSPICIOUS"
    
    def test_per_digit_breakdown(self):
        """Test that per-digit breakdown is populated."""
        # Generate enough data
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        assert len(result.digit_breakdown) == 9
        for bd in result.digit_breakdown:
            assert 1 <= bd.digit <= 9
            assert bd.expected > 0
            assert bd.actual >= 0
    
    def test_to_dict_serialization(self):
        """Test dictionary serialization."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        d = result.to_dict()
        
        assert "sample_size" in d
        assert "digit_position" in d
        assert "expected_frequencies" in d
        assert "observed_frequencies" in d
        assert "chi_squared" in d
        assert "p_value" in d
        assert "mad" in d
        assert "digit_breakdown" in d
        assert "is_suspicious" in d
        assert "verdict" in d


class TestAnalyzeBenford:
    """Tests for full Benford analysis."""
    
    def test_analyzes_multiple_positions(self):
        """Test analysis of multiple digit positions."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        results = analyze_benford(numbers, [1, 2])
        
        assert 1 in results
        assert 2 in results
    
    def test_results_contain_all_required_fields(self):
        """Test that results contain all required fields."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        results = analyze_benford(numbers, [1])
        
        result = results[1]
        assert isinstance(result, BenfordAnalysisResult)
        assert result.sample_size > 0
        assert len(result.expected_frequencies) == 9
        assert len(result.observed_frequencies) == 9


class TestAnalyzeText:
    """Tests for text analysis."""
    
    def test_insufficient_numbers(self):
        """Test text with insufficient numbers."""
        text = "Only 5 numbers here 1 2 3 4 5"
        result = analyze_text(text)
        
        assert "error" in result
        assert "Insufficient" in result["error"]
    
    def test_sufficient_numbers(self):
        """Test text with sufficient numbers."""
        # Generate text with many numbers
        numbers = [d * 1000 + i for d in range(1, 10) for i in range(50)]
        text = "Numbers: " + ", ".join(str(n) for n in numbers)
        
        result = analyze_text(text)
        
        assert "error" not in result
        assert result["numbers_found"] >= 30
        assert 1 in result["results"]


# Acceptance criteria tests
class TestBenfordEngineAcceptance:
    """Tests for acceptance criteria from the issue."""
    
    def test_input_100_200_300_400(self):
        """Test that [100, 200, 300, 400] produces expected first digits."""
        numbers = [100, 200, 300, 400]
        # First digits are [1, 2, 3, 4]
        
        result = analyze_single_position(numbers, 1)
        
        # With only 4 numbers, we should get insufficient data warning
        assert result.sample_size == 4
        assert "Insufficient" in result.verdict
    
    def test_returns_chi_squared(self):
        """Test that chi-squared value is returned."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        assert result.chi_squared >= 0
    
    def test_returns_p_value(self):
        """Test that p-value is returned."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        assert 0 <= result.p_value <= 1
    
    def test_returns_mad_score(self):
        """Test that MAD score is returned."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        assert result.mad >= 0
    
    def test_per_digit_breakdown(self):
        """Test per-digit breakdown with all required fields."""
        numbers = [d * 100 + i for d in range(1, 10) for i in range(100)]
        result = analyze_single_position(numbers, 1)
        
        for bd in result.digit_breakdown:
            assert "digit" in bd.__dict__ or hasattr(bd, 'digit')
            assert bd.digit >= 1
            assert bd.digit <= 9
            assert bd.expected >= 0
            assert bd.actual >= 0
            assert bd.deviation >= 0
    
    def test_handles_small_sample(self):
        """Test graceful handling of < 30 numbers."""
        numbers = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]
        
        result = analyze_single_position(numbers, 1)
        
        assert result.verdict == "Insufficient Data"
        assert "at least 30" in result.explanation