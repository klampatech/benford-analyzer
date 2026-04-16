"""Core Benford's Law analysis module."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class BenfordResult:
    """Result of Benford's Law analysis."""
    digit: int
    expected: List[float]
    observed: List[float]
    chi_squared: float
    p_value: float
    is_suspicious: bool
    verdict: str
    explanation: str


def extract_numbers(text: str) -> List[int]:
    """Extract all integers from text."""
    pattern = r'\b\d{1,15}\b'
    matches = re.findall(pattern, text)
    return [int(m) for m in matches if not m.startswith('0') or m == '0']


def get_leading_digits(numbers: List[int], position: int = 1) -> List[int]:
    """Extract leading digits from numbers at specified position."""
    result = []
    for n in numbers:
        if n == 0:
            continue
        n_str = str(abs(n))
        if len(n_str) >= position:
            digit = int(n_str[position - 1])
            result.append(digit)
    return result


def extract_leading_digits_from_text(text: str, position: int = 1) -> List[int]:
    """Extract leading digits directly from raw text.
    
    This is a convenience function that combines extract_numbers and
    get_leading_digits into a single operation for efficiency.
    
    Args:
        text: Raw text containing numbers
        position: Which digit position to extract (1 = first digit, 2 = second, etc.)
    
    Returns:
        List of leading digits found in the text
    """
    numbers = extract_numbers(text)
    return get_leading_digits(numbers, position)


def expected_benford_frequencies(digit: int = 1) -> List[float]:
    """Get expected Benford frequencies for leading digits.
    
    For digit position 1: frequencies for digits 1-9
    For digit position 2: frequencies for digits 0-9
    """
    if digit == 1:
        # First digit follows: P(d) = log10(1 + 1/d) for d in 1..9
        return [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
    elif digit == 2:
        # Second digit follows: P(d) = sum of log10(1 + 1/(10n+d)) for n in 1..9
        return [0.120, 0.114, 0.109, 0.104, 0.100, 0.096, 0.093, 0.090, 0.088, 0.085]
    return []


def analyze_benford(numbers: List[int], digits: List[int] = [1, 2]) -> dict:
    """Run full Benford analysis on a list of numbers.
    
    Returns chi-squared statistic and p-value to determine if the data
    follows Benford's Law distribution.
    """
    results = {}
    
    for digit_pos in digits:
        leading = get_leading_digits(numbers, digit_pos)
        
        if len(leading) < 30:
            results[digit_pos] = {
                "error": "Insufficient data (need at least 30 numbers)"
            }
            continue
        
        expected = expected_benford_frequencies(digit_pos)
        n = len(leading)
        
        # Count observed frequencies
        if digit_pos == 1:
            # First digit: count 1-9
            observed_counts = [leading.count(i) for i in range(1, 10)]
            range_start, range_end = 1, 10
        else:
            # Second digit: count 0-9
            observed_counts = [leading.count(i) for i in range(0, 10)]
            range_start, range_end = 0, 10
        
        observed = [count / n for count in observed_counts]
        
        # Chi-squared calculation using counts
        # sum((O-E)²/E) where O and E are COUNTS, not proportions
        chi_sq = 0.0
        for exp_prob, obs_count in zip(expected, observed_counts):
            exp_count = exp_prob * n
            if exp_count > 0:
                chi_sq += (obs_count - exp_count) ** 2 / exp_count
        
        # Degrees of freedom for chi-squared test
        df = len(expected) - 1
        
        # Critical values from chi-squared distribution (alpha=0.05)
        if digit_pos == 1:
            critical_value = 15.51  # df=8
        else:
            critical_value = 16.92  # df=9
        
        is_suspicious = chi_sq > critical_value
        
        # P-value calculation using scipy or approximation
        try:
            from scipy import stats
            p_value = float(1 - stats.chi2.cdf(chi_sq, df))
        except ImportError:
            # Fallback: Wilson-Hilferty transformation
            import math
            if chi_sq <= 0 or df <= 0:
                p_value = 1.0
            else:
                z = ((chi_sq / df) ** (1.0/3.0) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
                t = 1 / (1 + 0.2316419 * abs(z))
                poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
                cdf = 1 - (1 / math.sqrt(2 * math.pi)) * math.exp(-z*z/2) * poly
                p_value = max(0.0, min(1.0, 1 - cdf if z > 0 else cdf))
        
        verdict = "SUSPICIOUS" if is_suspicious else "NORMAL"
        explanation = (
            f"Analysis of {n} numbers shows "
            f"{verdict.lower()} distribution at digit position {digit_pos}. "
            f"Chi-squared: {chi_sq:.3f}, p-value: {p_value:.3e}"
        )
        
        results[digit_pos] = {
            "expected": expected,
            "observed": observed,
            "chi_squared": round(chi_sq, 4),
            "p_value": round(p_value, 6),
            "is_suspicious": is_suspicious,
            "verdict": verdict,
            "explanation": explanation,
            "sample_size": n,
            "observed_counts": observed_counts
        }
    
    return results


def analyze_text(text: str, digits: List[int] = [1, 2]) -> dict:
    """Analyze text for Benford's Law compliance."""
    numbers = extract_numbers(text)
    
    if len(numbers) < 30:
        return {
            "error": "Insufficient numbers in text (need at least 30)",
            "numbers_found": len(numbers)
        }
    
    results = analyze_benford(numbers, digits)
    
    return {
        "numbers_found": len(numbers),
        "digits_analyzed": digits,
        "results": results
    }
