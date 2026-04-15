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
