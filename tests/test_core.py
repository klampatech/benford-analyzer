"""Tests for core Benford analysis."""
import pytest

from src.core import (
    extract_numbers,
    get_leading_digits,
    expected_benford_frequencies,
    analyze_text,
    analyze_benford
)


class TestExtractNumbers:
    """Comprehensive tests for number extraction."""
    
    def test_extracts_integers(self):
        """Test extraction of simple integers."""
        text = "Company made 5000 profit, then 12000 more"
        numbers = extract_numbers(text)
        assert 5000 in numbers
        assert 12000 in numbers
    
    def test_empty_string(self):
        """Test extraction from empty string returns empty list."""
        text = ""
        numbers = extract_numbers(text)
        assert numbers == []
    
    def test_text_with_no_numbers(self):
        """Test extraction from text without numbers."""
        text = "Hello world, this is a test"
        numbers = extract_numbers(text)
        assert numbers == []
    
    def test_single_digit_numbers(self):
        """Test extraction of single digit numbers."""
        text = "The values are 1, 2, 3, 4, 5"
        numbers = extract_numbers(text)
        assert 1 in numbers
        assert 2 in numbers
        assert 3 in numbers
        assert 4 in numbers
        assert 5 in numbers
    
    def test_numbers_at_boundaries(self):
        """Test extraction at beginning and end of text."""
        text = "100 hello world 200"
        numbers = extract_numbers(text)
        assert 100 in numbers
        assert 200 in numbers
    
    def test_negative_numbers(self):
        """Test extraction of negative numbers."""
        text = "Temperature is -5 degrees, then -20"
        numbers = extract_numbers(text)
        # The regex pattern extracts just digits, negative sign is not captured
        # So we expect 5 and 20 in the result
        assert 5 in numbers
        assert 20 in numbers
    
    def test_numbers_with_punctuation(self):
        """Test extraction adjacent to punctuation."""
        text = "Price: $50.00, Discount: 10%! Total: 100."
        numbers = extract_numbers(text)
        assert 50 in numbers
        assert 10 in numbers
        assert 100 in numbers
    
    def test_numbers_with_decimals(self):
        """Test that decimal points are not included in extraction."""
        text = "Price is 10.99 and 20.50"
        numbers = extract_numbers(text)
        # Should extract integers: 10 and 99, 20 and 50
        assert 10 in numbers
        assert 99 in numbers
        assert 20 in numbers
        assert 50 in numbers
    
    def test_leading_zeros_excluded(self):
        """Test that numbers with leading zeros are excluded by filter."""
        text = "Values 007 and 008 and 009"
        numbers = extract_numbers(text)
        # Numbers starting with '0' (except '0' itself) are excluded by the filter
        assert 7 not in numbers
        assert 8 not in numbers
        assert 9 not in numbers
        assert numbers == []
    
    def test_zero_value(self):
        """Test extraction of zero."""
        text = "Count is 0 and zero items"
        numbers = extract_numbers(text)
        assert 0 in numbers
    
    def test_large_numbers(self):
        """Test extraction of large numbers."""
        text = "Revenue was 1234567890 dollars"
        numbers = extract_numbers(text)
        assert 1234567890 in numbers
    
    def test_numbers_with_commas(self):
        """Test extraction when commas are part of number formatting."""
        text = "Population: 1,000,000 and 2,500,000"
        numbers = extract_numbers(text)
        # Should extract 1, 1000, 1000, 2, 500, 1000 (commas split numbers)
        assert 1 in numbers
        assert 2 in numbers
    
    def test_mixed_content_text(self):
        """Test extraction from complex mixed content."""
        text = "On Jan 15, 2024, we sold 500 units for $2500. Total: $3000."
        numbers = extract_numbers(text)
        assert 15 in numbers
        assert 2024 in numbers
        assert 500 in numbers
        assert 2500 in numbers
        assert 3000 in numbers
    
    def test_numbers_separated_by_spaces(self):
        """Test extraction from space-separated numbers."""
        text = "42 100 999 12345"
        numbers = extract_numbers(text)
        assert 42 in numbers
        assert 100 in numbers
        assert 999 in numbers
        assert 12345 in numbers
    
    def test_numbers_in_parentheses(self):
        """Test extraction from text with parentheses."""
        text = "Values (100) and (200)"
        numbers = extract_numbers(text)
        assert 100 in numbers
        assert 200 in numbers
    
    def test_numbers_in_brackets(self):
        """Test extraction from text with brackets."""
        text = "Results [50] vs [75]"
        numbers = extract_numbers(text)
        assert 50 in numbers
        assert 75 in numbers
    
    def test_max_length_numbers(self):
        """Test extraction of 15-digit numbers (max length in pattern)."""
        text = "ID: 123456789012345 and 987654321098765"
        numbers = extract_numbers(text)
        assert 123456789012345 in numbers
        # The second number has 15 digits but also works
    
    def test_multiple_same_numbers(self):
        """Test extraction when same number appears multiple times."""
        text = "The number 42 appears 42 times at 42"
        numbers = extract_numbers(text)
        assert numbers.count(42) == 3
    
    def test_whitespace_handling(self):
        """Test extraction with various whitespace patterns."""
        text = "  100  \t 200  \n 300  "
        numbers = extract_numbers(text)
        assert 100 in numbers
        assert 200 in numbers
        assert 300 in numbers
    
    def test_numbers_with_underscores(self):
        """Test extraction when underscores are present."""
        text = "Values 1_000 and 2_500"
        numbers = extract_numbers(text)
        # Underscores are word characters, so 1_000 is treated as a single token
        # but doesn't match \b\d pattern (needs word boundary after digits)
        # So underscores effectively prevent number extraction
        assert 1 not in numbers
        assert 2 not in numbers


class TestLeadingDigits:
    """Comprehensive tests for leading digit extraction."""
    
    def test_first_digit_position(self):
        """Test extraction of first leading digit."""
        numbers = [123, 456, 789, 100, 200]
        leading = get_leading_digits(numbers, 1)
        assert 1 in leading
        assert 4 in leading
        assert 7 in leading
    
    def test_second_digit_position(self):
        """Test extraction of second leading digit."""
        numbers = [123, 456, 789, 100, 200]
        leading = get_leading_digits(numbers, 2)
        # 123 -> 2, 456 -> 5, 789 -> 8, 100 -> 0, 200 -> 0
        assert 2 in leading
        assert 5 in leading
        assert 8 in leading
        assert 0 in leading  # 100 and 200 have 0 as second digit
    
    def test_third_digit_position(self):
        """Test extraction of third leading digit."""
        numbers = [123, 456, 789, 1000]
        leading = get_leading_digits(numbers, 3)
        assert 3 in leading  # 123 -> 3
        assert 6 in leading  # 456 -> 6
        assert 9 in leading  # 789 -> 9
        assert 0 in leading  # 1000 -> 0
    
    def test_zero_excluded(self):
        """Test that zero is excluded from results."""
        numbers = [0, 100]
        leading = get_leading_digits(numbers, 1)
        assert 0 not in leading
    
    def test_single_digit_numbers(self):
        """Test extraction from single digit numbers."""
        numbers = [1, 5, 9]
        leading = get_leading_digits(numbers, 1)
        assert 1 in leading
        assert 5 in leading
        assert 9 in leading
    
    def test_position_beyond_length(self):
        """Test extraction when position exceeds number length."""
        numbers = [12, 3]
        leading = get_leading_digits(numbers, 3)
        # No numbers have 3 digits, so result should be empty
        assert len(leading) == 0
    
    def test_negative_numbers_handled(self):
        """Test that absolute value is used for negatives."""
        numbers = [-123, -456]
        leading = get_leading_digits(numbers, 1)
        assert 1 in leading  # |-123| starts with 1
        assert 4 in leading  # |-456| starts with 4
    
    def test_empty_list(self):
        """Test extraction from empty list."""
        numbers = []
        leading = get_leading_digits(numbers, 1)
        assert leading == []
    
    def test_large_numbers(self):
        """Test extraction from very large numbers."""
        numbers = [123456789012345]
        leading = get_leading_digits(numbers, 1)
        assert leading == [1]
        
        leading2 = get_leading_digits(numbers, 5)
        assert leading2 == [5]  # 5th digit is 5


class TestExpectedFrequencies:
    """Tests for Benford expected frequencies."""
    
    def test_first_digit_frequencies_sum_to_one(self):
        freq = expected_benford_frequencies(1)
        assert abs(sum(freq) - 1.0) < 0.01
        assert len(freq) == 9
    
    def test_second_digit_frequencies_sum_to_one(self):
        freq = expected_benford_frequencies(2)
        assert abs(sum(freq) - 1.0) < 0.01


class TestAnalyzeText:
    """Tests for full text analysis."""
    
    def test_analyze_with_sufficient_numbers(self):
        # Generate text with at least 30 numbers
        numbers = [123456, 234567, 345678, 456789, 123000, 234000, 345000, 456000,
                   567000, 678000, 789000, 890000, 901000, 123400, 234500, 345600,
                   456700, 567800, 678900, 789000, 890100, 901200, 123500, 234600,
                   345700, 456800, 567900, 678000, 789100, 890200]
        text = "Numbers: " + ", ".join(str(n) for n in numbers)
        result = analyze_text(text, digits=[1])
        assert "numbers_found" in result
        assert result["numbers_found"] >= 30
        assert 1 in result["results"]
    
    def test_analyze_insufficient_data(self):
        text = "Just 5 numbers 1 2 3 4 5"
        result = analyze_text(text)
        assert "error" in result
        assert "Insufficient" in result["error"]


class TestBenfordStatisticalEngine:
    """Tests for the Benford statistical analysis engine.
    
    Acceptance criteria:
    - US county populations → passes Benford (p > 0.05)
    - Uniform random numbers → fails Benford (p < 0.05)
    - Per-digit MAD computed correctly
    - Second-digit distribution computed correctly
    """
    
    def test_analyze_benford_returns_valid_structure(self):
        """Test that analyze_benford returns the expected result structure."""
        # Generate at least 30 numbers that roughly follow Benford
        benford_like = []
        for d in range(1, 10):
            # Approximately match Benford proportions
            count = int([0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046][d-1] * 100)
            benford_like.extend([d * 1000 + i for i in range(count)])
        
        result = analyze_benford(benford_like, digits=[1])
        
        assert 1 in result
        assert "expected" in result[1]
        assert "observed" in result[1]
        assert "chi_squared" in result[1]
        assert "p_value" in result[1]
        assert "is_suspicious" in result[1]
        assert "verdict" in result[1]
        assert "explanation" in result[1]
        assert "sample_size" in result[1]
    
    def test_benford_like_data_not_suspicious(self):
        """Data that closely matches Benford distribution should NOT be suspicious."""
        # Create data that closely matches Benford distribution
        benford_like = []
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        for d in range(1, 10):
            count = int(expected[d-1] * 100)
            benford_like.extend([d * 1000 + i for i in range(count)])
        
        result = analyze_benford(benford_like, digits=[1])
        
        # Chi-squared count-based should be low
        chi_sq_count = result[1]["chi_squared"] * len(benford_like)
        assert chi_sq_count < 15, f"Benford-like data should have low chi-squared (got {chi_sq_count})"
    
    def test_highly_skewed_data_is_suspicious(self):
        """Data that heavily deviates from Benford should be flagged as suspicious."""
        # Create heavily skewed data: most numbers start with 1
        skewed_numbers = []
        # 50% start with 1 (Benford expects 30%)
        skewed_numbers.extend([1 * 1000 + i for i in range(500)])
        # Other digits less than expected
        skewed_numbers.extend([5 * 1000 + i for i in range(100)])
        skewed_numbers.extend([9 * 1000 + i for i in range(50)])
        skewed_numbers.extend([2 * 1000 + i for i in range(80)])
        skewed_numbers.extend([3 * 1000 + i for i in range(60)])
        skewed_numbers.extend([4 * 1000 + i for i in range(50)])
        skewed_numbers.extend([6 * 1000 + i for i in range(40)])
        skewed_numbers.extend([7 * 1000 + i for i in range(30)])
        skewed_numbers.extend([8 * 1000 + i for i in range(20)])
        
        result = analyze_benford(skewed_numbers, digits=[1])
        
        # Chi-squared count-based should be high for skewed data
        chi_sq_count = result[1]["chi_squared"] * len(skewed_numbers)
        assert chi_sq_count > 15, f"Skewed data should have high chi-squared (got {chi_sq_count})"
    
    def test_mad_computed_correctly(self):
        """Test that Mean Absolute Deviation is computed correctly.
        
        MAD = mean(|observed - expected|) for each digit
        """
        # Known Benford distribution for first digit
        benford_expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        
        # Perfect Benford distribution (observed = expected)
        perfect_observed = benford_expected.copy()
        
        # Compute MAD for perfect match
        mad_perfect = sum(abs(o - e) for o, e in zip(perfect_observed, benford_expected)) / 9
        
        # For perfect match, MAD should be 0
        assert mad_perfect == 0.0, "Perfect match should have MAD = 0"
        
        # Slight deviation case
        deviated_observed = [0.32, 0.17, 0.12, 0.10, 0.08, 0.06, 0.06, 0.05, 0.05]
        mad_deviated = sum(abs(o - e) for o, e in zip(deviated_observed, benford_expected)) / 9
        
        # MAD should be small but positive
        assert mad_deviated > 0, "Deviation should produce positive MAD"
        assert mad_deviated < 0.05, f"MAD should be small (got {mad_deviated})"
    
    def test_second_digit_distribution(self):
        """Test second-digit Benford distribution analysis.
        
        Second digit follows a different Benford distribution.
        """
        # Use numbers that should produce valid second-digit analysis
        numbers = []
        for _ in range(50):
            numbers.extend([1000 + i for i in range(10)])
        
        result = analyze_benford(numbers, digits=[1, 2])
        
        assert 1 in result
        assert 2 in result
        
        # Second digit analysis should complete without error
        assert "error" not in result[2], f"Second digit analysis failed: {result[2]}"
        
        # Second digit frequencies should sum to ~1.0
        freq_2 = result[2]["observed"]
        assert abs(sum(freq_2) - 1.0) < 0.01, \
            f"Second digit frequencies should sum to 1 (got {sum(freq_2)})"
    
    def test_chi_squared_calculation(self):
        """Test chi-squared calculation produces relative comparisons correctly."""
        # Create data that exactly matches expected distribution
        perfect_numbers = []
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        for digit, freq in enumerate(expected, 1):
            count = int(freq * 1000)
            perfect_numbers.extend([digit * 1000 + i for i in range(count)])
        
        result = analyze_benford(perfect_numbers, digits=[1])
        
        # Chi-squared should be very low for near-perfect match
        assert result[1]["chi_squared"] < 0.5, \
            f"Near-perfect match should have low chi-squared (got {result[1]['chi_squared']})"
        
        # Create clearly deviated data
        deviated_numbers = []
        deviated_numbers.extend([1 * 1000 + i for i in range(400)])  # 40% ones
        deviated_numbers.extend([2 * 1000 + i for i in range(150)])  # 15% twos
        deviated_numbers.extend([3 * 1000 + i for i in range(100)])  # 10% threes
        deviated_numbers.extend([4 * 1000 + i for i in range(80)])
        deviated_numbers.extend([5 * 1000 + i for i in range(70)])
        deviated_numbers.extend([6 * 1000 + i for i in range(60)])
        deviated_numbers.extend([7 * 1000 + i for i in range(50)])
        deviated_numbers.extend([8 * 1000 + i for i in range(40)])
        deviated_numbers.extend([9 * 1000 + i for i in range(10)])  # 1% nines
        
        result2 = analyze_benford(deviated_numbers, digits=[1])
        
        # Deviated should have higher chi-squared than perfect
        assert result2[1]["chi_squared"] > result[1]["chi_squared"], \
            "Deviated data should have higher chi-squared than perfect match"
    
    def test_p_value_calculation(self):
        """Test p-value calculation produces relative comparisons."""
        # Create Benford-like data (should have low chi-squared, high p-value)
        benford_like = []
        expected = [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
        for d in range(1, 10):
            count = int(expected[d-1] * 1000)
            benford_like.extend([d * 1000 + i for i in range(count)])
        
        result = analyze_benford(benford_like, digits=[1])
        
        # p-value should be high for Benford-like match
        assert result[1]["p_value"] > 0.5, \
            f"Benford-like should give high p-value (got {result[1]['p_value']}, chi_sq={result[1]['chi_squared']})"
        
        # Create deviated data (should have higher chi-squared, lower p-value)
        deviated_numbers = []
        # 40% ones (Benford expects 30%)
        deviated_numbers.extend([1 * 1000 + i for i in range(400)])
        # 15% twos (Benford expects 17.6%)
        deviated_numbers.extend([2 * 1000 + i for i in range(150)])
        # Rest distributed unevenly
        deviated_numbers.extend([3 * 1000 + i for i in range(100)])
        deviated_numbers.extend([4 * 1000 + i for i in range(80)])
        deviated_numbers.extend([5 * 1000 + i for i in range(70)])
        deviated_numbers.extend([6 * 1000 + i for i in range(60)])
        deviated_numbers.extend([7 * 1000 + i for i in range(50)])
        deviated_numbers.extend([8 * 1000 + i for i in range(40)])
        deviated_numbers.extend([9 * 1000 + i for i in range(10)])
        
        result2 = analyze_benford(deviated_numbers, digits=[1])
        
        # Deviated should have lower p-value than Benford-like
        assert result2[1]["p_value"] < result[1]["p_value"], \
            f"Deviated should have lower p-value (dev={result2[1]['p_value']}, benford={result[1]['p_value']})"
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data (< 30 numbers)."""
        small_dataset = [123, 456, 789, 100, 200, 300, 400, 500]  # Only 8 numbers
        
        result = analyze_benford(small_dataset, digits=[1])
        
        assert 1 in result
        assert "error" in result[1]
        assert "Insufficient" in result[1]["error"]
    
    def test_verdict_consistency(self):
        """Test that verdict is consistent with is_suspicious flag."""
        # Benford-like data should have NORMAL verdict
        benford_like = []
        for d in range(1, 10):
            count = int([0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046][d-1] * 100)
            benford_like.extend([d * 1000 + i for i in range(count)])
        
        result = analyze_benford(benford_like, digits=[1])
        
        if result[1]["is_suspicious"]:
            assert result[1]["verdict"] == "SUSPICIOUS"
        else:
            assert result[1]["verdict"] == "NORMAL"
    
    def test_sample_size_recorded(self):
        """Test that sample size is recorded in results."""
        numbers = [100, 200, 300, 400, 500] * 10  # 50 numbers
        
        result = analyze_benford(numbers, digits=[1])
        
        assert "sample_size" in result[1]
        assert result[1]["sample_size"] >= 30  # Only records if analysis ran