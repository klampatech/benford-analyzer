"""Benford's Law statistical analysis engine.

This module provides comprehensive Benford analysis including:
- First and second digit distribution analysis
- Chi-squared statistical tests
- Mean Absolute Deviation (MAD) computation
- Detailed per-digit breakdown
- Plain-English verdicts
"""
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DigitBreakdown:
    """Per-digit breakdown of expected vs actual frequencies."""
    digit: int
    expected: float
    actual: float
    deviation: float
    deviation_pct: float


@dataclass
class BenfordAnalysisResult:
    """Comprehensive result of Benford analysis.
    
    Contains all statistical metrics and per-digit breakdown.
    """
    sample_size: int
    digit_position: int  # 1 = first digit, 2 = second digit
    
    # Distribution data
    expected_frequencies: List[float]
    observed_frequencies: List[float]
    
    # Statistical tests
    chi_squared: float
    chi_squared_critical: float
    degrees_of_freedom: int
    p_value: float
    
    # MAD (Mean Absolute Deviation)
    mad: float
    
    # Verdict
    is_suspicious: bool
    verdict: str
    explanation: str
    
    # Optional fields with defaults
    digit_breakdown: List[DigitBreakdown] = field(default_factory=list)
    observed_counts: List[int] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "sample_size": self.sample_size,
            "digit_position": self.digit_position,
            "expected_frequencies": [round(f, 4) for f in self.expected_frequencies],
            "observed_frequencies": [round(f, 4) for f in self.observed_frequencies],
            "chi_squared": round(self.chi_squared, 4),
            "chi_squared_critical": round(self.chi_squared_critical, 2),
            "degrees_of_freedom": self.degrees_of_freedom,
            "p_value": round(self.p_value, 4),
            "mad": round(self.mad, 4),
            "digit_breakdown": [
                {
                    "digit": d.digit,
                    "expected": round(d.expected, 4),
                    "actual": round(d.actual, 4),
                    "deviation": round(d.deviation, 4),
                    "deviation_pct": round(d.deviation_pct, 2)
                }
                for d in self.digit_breakdown
            ],
            "is_suspicious": self.is_suspicious,
            "verdict": self.verdict,
            "explanation": self.explanation,
            "observed_counts": self.observed_counts
        }


def benford_expected_probability(d: int, position: int = 1) -> float:
    """Calculate expected Benford probability for a digit.
    
    Formula: P(d) = log10(1 + 1/d) for first digit
    For second digit and beyond, use: P(d) = sum(log10(1 + 1/(10*n + d))) for n in 1..9
    
    Args:
        d: The digit (1-9 for first, 0-9 for second+)
        position: Which digit position (1 = first, 2 = second, etc.)
    
    Returns:
        Expected probability following Benford's Law
    """
    if position == 1:
        if d < 1 or d > 9:
            return 0.0
        return math.log10(1 + 1/d)
    else:
        # For second digit and beyond: sum over all possible first digits
        # P(d_pos) = sum_{n=1}^{9} log10(1 + 1/(10*n + d_pos-1))
        if d < 0 or d > 9:
            return 0.0
        total = 0.0
        for n in range(1, 10):
            total += math.log10(1 + 1/(10*n + d))
        return total


def get_expected_benford_frequencies(position: int = 1) -> List[float]:
    """Get expected Benford frequencies for a digit position.
    
    Args:
        position: 1 for first digit (returns 9 values for 1-9),
                  2 for second digit (returns 10 values for 0-9)
    
    Returns:
        List of expected frequencies
    """
    if position == 1:
        return [benford_expected_probability(d, 1) for d in range(1, 10)]
    else:
        return [benford_expected_probability(d, 2) for d in range(0, 10)]


def get_leading_digit(n: int, position: int = 1) -> int:
    """Extract the leading digit at a specific position.
    
    Args:
        n: The number
        position: 1 for first digit, 2 for second, etc.
    
    Returns:
        The digit at the specified position, or -1 if not available
    """
    if n == 0:
        return -1
    
    n = abs(n)
    digits = str(n)
    
    if position > len(digits):
        return -1
    
    return int(digits[position - 1])


def get_leading_digits(numbers: List[int], position: int = 1) -> List[int]:
    """Extract leading digits at a specific position from a list of numbers.
    
    Args:
        numbers: List of numbers
        position: Which digit position to extract
    
    Returns:
        List of leading digits
    """
    return [get_leading_digit(n, position) for n in numbers if get_leading_digit(n, position) != -1]


def compute_mad(expected: List[float], observed: List[float]) -> float:
    """Compute Mean Absolute Deviation between expected and observed frequencies.
    
    MAD = mean(|observed - expected|)
    
    Args:
        expected: Expected frequencies
        observed: Observed frequencies
    
    Returns:
        Mean Absolute Deviation
    """
    if len(expected) != len(observed) or len(expected) == 0:
        return 0.0
    return sum(abs(o - e) for o, e in zip(observed, expected)) / len(expected)


def compute_chi_squared(expected: List[float], observed: List[float], n: int) -> float:
    """Compute chi-squared statistic for Benford analysis.
    
    Uses the count-based chi-squared formula: sum((O-E)²/E)
    where O and E are counts, not proportions.
    
    Args:
        expected: Expected frequencies (should sum to 1)
        observed: Observed frequencies (should sum to 1)
        n: Sample size
    
    Returns:
        Chi-squared statistic (count-based)
    """
    chi_sq = 0.0
    for exp, obs in zip(expected, observed):
        if exp > 0:
            # Convert to counts
            exp_count = exp * n
            obs_count = obs * n
            chi_sq += (obs_count - exp_count) ** 2 / exp_count
    return chi_sq


def chi_squared_critical_value(df: int, alpha: float = 0.05) -> float:
    """Get critical value for chi-squared distribution.
    
    Uses approximation for common degrees of freedom and alpha levels.
    
    Args:
        df: Degrees of freedom
        alpha: Significance level (default 0.05)
    
    Returns:
        Critical value
    """
    # Critical values for common scenarios
    critical_values = {
        (8, 0.05): 15.51,   # df=8, alpha=0.05
        (9, 0.05): 16.92,   # df=9, alpha=0.05
        (8, 0.01): 20.09,   # df=8, alpha=0.01
        (9, 0.01): 21.67,   # df=9, alpha=0.01
    }
    
    return critical_values.get((df, alpha), 15.0)


def compute_p_value(chi_squared: float, df: int) -> float:
    """Compute p-value from chi-squared statistic.
    
    Uses scipy.stats.chi2 for accurate p-value calculation.
    Falls back to approximation if scipy is unavailable.
    
    Args:
        chi_squared: Chi-squared statistic
        df: Degrees of freedom
    
    Returns:
        P-value (probability of observing this or more extreme result)
    """
    try:
        from scipy import stats
        # p-value = P(X > chi_squared) = 1 - CDF(chi_squared)
        return float(1 - stats.chi2.cdf(chi_squared, df))
    except ImportError:
        # Fallback approximation for when scipy is unavailable
        # Uses Wilson-Hilferty transformation: z = (x/df)^(1/3)
        import math
        
        if chi_squared <= 0 or df <= 0:
            return 1.0
        
        # Wilson-Hilferty approximation
        z = ((chi_squared / df) ** (1.0/3.0) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
        
        # Standard normal CDF approximation (Abramowitz & Stegun)
        # CDF for z using Hastings approximation
        t = 1 / (1 + 0.2316419 * abs(z))
        poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        cdf = 1 - (1 / math.sqrt(2 * math.pi)) * math.exp(-z*z/2) * poly
        
        # One-tailed p-value
        p = 1 - cdf if z > 0 else cdf
        return max(0.0, min(1.0, p))


def analyze_single_position(numbers: List[int], position: int = 1) -> BenfordAnalysisResult:
    """Analyze Benford distribution at a specific digit position.
    
    Args:
        numbers: List of numbers to analyze
        position: Which digit position (1 = first, 2 = second)
    
    Returns:
        BenfordAnalysisResult with full analysis
    """
    # Get leading digits at this position
    digits = get_leading_digits(numbers, position)
    n = len(digits)
    
    # Check minimum sample size
    if n < 30:
        return BenfordAnalysisResult(
            sample_size=n,
            digit_position=position,
            expected_frequencies=[],
            observed_frequencies=[],
            chi_squared=0.0,
            chi_squared_critical=0.0,
            degrees_of_freedom=0,
            p_value=0.0,
            mad=0.0,
            digit_breakdown=[],
            is_suspicious=False,
            verdict="Insufficient Data",
            explanation=f"Need at least 30 numbers for reliable analysis. Got {n}."
        )
    
    # Get expected and observed frequencies
    expected = get_expected_benford_frequencies(position)
    
    if position == 1:
        digit_range = range(1, 10)
    else:
        digit_range = range(0, 10)
    
    counts = [digits.count(d) for d in digit_range]
    observed = [c / n for c in counts]
    
    # Compute statistics
    chi_sq = compute_chi_squared(expected, observed, n)
    df = len(expected) - 1
    critical = chi_squared_critical_value(df, 0.05)
    p_value = compute_p_value(chi_sq, df)
    mad = compute_mad(expected, observed)
    
    # Determine if suspicious
    is_suspicious = chi_sq > critical
    
    # Per-digit breakdown
    breakdown = []
    for i, digit in enumerate(digit_range):
        exp = expected[i]
        act = observed[i]
        dev = abs(act - exp)
        dev_pct = (dev / exp * 100) if exp > 0 else 0
        breakdown.append(DigitBreakdown(
            digit=digit,
            expected=exp,
            actual=act,
            deviation=dev,
            deviation_pct=dev_pct
        ))
    
    # Generate verdict
    if is_suspicious:
        verdict = "SUSPICIOUS"
    else:
        verdict = "NORMAL"
    
    explanation = (
        f"Analysis of {n} numbers at digit position {position}: "
        f"Chi-squared = {chi_sq:.3f} (critical = {critical:.2f}), "
        f"p-value = {p_value:.3f}, MAD = {mad:.4f}. "
        f"Distribution is {verdict.lower()}."
    )
    
    return BenfordAnalysisResult(
        sample_size=n,
        digit_position=position,
        expected_frequencies=expected,
        observed_frequencies=observed,
        chi_squared=chi_sq,
        chi_squared_critical=critical,
        degrees_of_freedom=df,
        p_value=p_value,
        mad=mad,
        digit_breakdown=breakdown,
        is_suspicious=is_suspicious,
        verdict=verdict,
        explanation=explanation,
        observed_counts=counts
    )


def analyze_benford(numbers: List[int], positions: List[int] = [1, 2]) -> Dict[int, BenfordAnalysisResult]:
    """Perform full Benford analysis on a list of numbers.
    
    Args:
        numbers: List of numbers to analyze
        positions: Which digit positions to analyze (default: [1, 2])
    
    Returns:
        Dictionary mapping position to BenfordAnalysisResult
    """
    results = {}
    
    for pos in positions:
        results[pos] = analyze_single_position(numbers, pos)
    
    return results


def analyze_text(text: str, positions: List[int] = [1, 2]) -> Dict[str, any]:
    """Analyze a text string for Benford compliance.
    
    Extracts all integers from the text and performs Benford analysis.
    
    Args:
        text: Text containing numbers
        positions: Which digit positions to analyze
    
    Returns:
        Dictionary with analysis results and metadata
    """
    import re
    
    # Extract numbers from text
    pattern = r'\b\d{1,15}\b'
    matches = re.findall(pattern, text)
    numbers = [int(m) for m in matches if not m.startswith('0') or m == '0']
    
    if len(numbers) < 30:
        return {
            "error": "Insufficient numbers in text (need at least 30)",
            "numbers_found": len(numbers),
            "numbers_sample": numbers[:10] if numbers else []
        }
    
    # Perform analysis
    results = analyze_benford(numbers, positions)
    
    # Build response
    response = {
        "numbers_found": len(numbers),
        "numbers_sample": numbers[:10],
        "positions_analyzed": positions,
        "results": {}
    }
    
    for pos, result in results.items():
        response["results"][pos] = result.to_dict()
    
    return response


# Convenience function matching the signature in core module
def analyze(numbers: List[int]) -> BenfordAnalysisResult:
    """Convenience function for first-digit Benford analysis.
    
    Args:
        numbers: List of numbers to analyze
    
    Returns:
        BenfordAnalysisResult for first digit position
    """
    return analyze_single_position(numbers, 1)