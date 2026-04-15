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


def expected_benford_frequencies(digit: int = 1) -> List[float]:
    """Get expected Benford frequencies for leading digits."""
    if digit == 1:
        return [0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046]
    elif digit == 2:
        return [0.120, 0.114, 0.109, 0.104, 0.100, 0.096, 0.093, 0.090, 0.088, 0.085]
    return []


def analyze_benford(numbers: List[int], digits: List[int] = [1, 2]) -> dict:
    """Run full Benford analysis on a list of numbers."""
    results = {}
    
    for digit_pos in digits:
        leading = get_leading_digits(numbers, digit_pos)
        
        if len(leading) < 30:
            results[digit_pos] = {
                "error": "Insufficient data (need at least 30 numbers)"
            }
            continue
        
        expected = expected_benford_frequencies(digit_pos)
        observed_counts = [leading.count(i) for i in range(1 if digit_pos == 1 else 10, 10 if digit_pos == 1 else 10 + (digit_pos - 1) * 0 + 10)]
        
        # Fix: proper counting
        if digit_pos == 1:
            range_start, range_end = 1, 10
        else:
            range_start, range_end = 10, 100
        
        observed_counts = []
        for i in range(range_start, range_end):
            observed_counts.append(leading.count(i))
        
        n = len(leading)
        observed = [count / n for count in observed_counts]
        
        # Chi-squared calculation
        chi_sq = sum(
            (obs - exp) ** 2 / exp
            for obs, exp in zip(observed, expected)
            if exp > 0
        )
        
        # Simple p-value approximation
        p_value = max(0.01, 1 - chi_sq / 20)
        is_suspicious = chi_sq > 15.51  # Critical value for df=8, alpha=0.05
        
        verdict = "SUSPICIOUS" if is_suspicious else "NORMAL"
        explanation = (
            f"Analysis of {n} numbers shows "
            f"{verdict.lower()} distribution at digit position {digit_pos}. "
            f"Chi-squared: {chi_sq:.3f}"
        )
        
        results[digit_pos] = {
            "expected": expected,
            "observed": observed,
            "chi_squared": round(chi_sq, 4),
            "p_value": round(p_value, 4),
            "is_suspicious": is_suspicious,
            "verdict": verdict,
            "explanation": explanation,
            "sample_size": n
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
