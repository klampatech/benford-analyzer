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
    """Tests for number extraction."""
    
    def test_extracts_integers(self):
        text = "Company made 5000 profit, then 12000 more"
        numbers = extract_numbers(text)
        assert 5000 in numbers
        assert 12000 in numbers
    
    def test_ignores_leading_zeros(self):
        text = "Values 007 and 008 and 009"
        numbers = extract_numbers(text)
        # These should be handled correctly
    
    def test_handles_large_numbers(self):
        text = "Revenue was 1234567890 dollars"
        numbers = extract_numbers(text)
        assert 1234567890 in numbers


class TestLeadingDigits:
    """Tests for leading digit extraction."""
    
    def test_first_digit_position(self):
        numbers = [123, 456, 789, 100, 200]
        leading = get_leading_digits(numbers, 1)
        assert 1 in leading
        assert 4 in leading
        assert 7 in leading
    
    def test_second_digit_position(self):
        numbers = [123, 456, 789, 100, 200]
        leading = get_leading_digits(numbers, 2)
        # 123 -> 2, 456 -> 5, 789 -> 8, etc.


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
