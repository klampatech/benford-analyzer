"""Verdict generation - human-readable interpretation of Benford analysis."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DigitFlag:
    """Flag for a specific digit anomaly."""
    digit: int
    digit_position: int  # 1 = first digit, 2 = second digit
    expected_pct: float
    actual_pct: float
    interpretation: str


@dataclass
class VerdictResult:
    """Human-readable verdict from Benford analysis."""
    verdict: str  # "Likely Natural", "Suspicious", "Highly Suspicious"
    verdict_code: str  # "natural", "suspicious", "highly_suspicious", "insufficient_data"
    authenticity_score: int  # 0-100
    confidence_percent: int  # 0-100
    confidence_band: str  # "High", "Medium", "Low"
    flags: List[DigitFlag] = field(default_factory=list)
    explanation: str = ""
    raw_chi_squared: Optional[float] = None
    raw_p_value: Optional[float] = None
    raw_mad: Optional[float] = None
    sample_size: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "verdict": self.verdict,
            "verdict_code": self.verdict_code,
            "authenticity_score": self.authenticity_score,
            "confidence_percent": self.confidence_percent,
            "confidence_band": self.confidence_band,
            "flags": [
                {
                    "digit": f.digit,
                    "digit_position": f.digit_position,
                    "expected_pct": round(f.expected_pct, 2),
                    "actual_pct": round(f.actual_pct, 2),
                    "interpretation": f.interpretation
                }
                for f in self.flags
            ],
            "explanation": self.explanation,
            "raw_chi_squared": self.raw_chi_squared,
            "raw_p_value": self.raw_p_value,
            "raw_mad": self.raw_mad,
            "sample_size": self.sample_size
        }


def compute_mad(expected: List[float], observed: List[float]) -> float:
    """Compute Mean Absolute Deviation between expected and observed frequencies."""
    if len(expected) != len(observed) or len(expected) == 0:
        return 0.0
    return sum(abs(o - e) for o, e in zip(observed, expected)) / len(expected)


def authenticity_score_from_mad(mad: float) -> int:
    """Convert MAD to 0-100 authenticity score.
    
    MAD of 0 = perfect Benford match = 100 score
    MAD of ~0.06 (random uniform) = 0 score
    We scale linearly in the typical range.
    """
    # Maximum reasonable MAD is about 0.06 for uniform distribution vs Benford
    # We use a sigmoid-like scale to emphasize the middle range
    max_mad = 0.06
    clamped_mad = min(mad, max_mad)
    # Linear scale: 0 MAD = 100, max_mad = 0
    score = int(100 * (1 - clamped_mad / max_mad))
    return max(0, min(100, score))


def confidence_from_p_value(p_value: float) -> tuple:
    """Convert p-value to confidence percentage and band.
    
    Returns (confidence_percent, band_name)
    """
    if p_value >= 0.10:
        return 85, "High"
    elif p_value >= 0.05:
        return 70, "Medium"
    elif p_value >= 0.01:
        return 50, "Low"
    else:
        return 30, "Very Low"


def p_value_to_verdict(p_value: float) -> tuple:
    """Convert p-value to verdict string and code."""
    if p_value >= 0.05:
        return "Likely Natural", "natural"
    elif p_value >= 0.01:
        return "Suspicious", "suspicious"
    else:
        return "Highly Suspicious", "highly_suspicious"


def generate_verdict(
    expected: List[float],
    observed: List[float],
    chi_squared: float,
    p_value: float,
    sample_size: int,
    digit_position: int = 1
) -> VerdictResult:
    """Generate a human-readable verdict from statistical analysis.
    
    Args:
        expected: Expected Benford frequencies
        observed: Observed frequencies from data
        chi_squared: Chi-squared test statistic
        p_value: P-value from statistical test
        sample_size: Number of numbers analyzed
        digit_position: Which digit was analyzed (1 or 2)
    
    Returns:
        VerdictResult with verdict, score, and flags
    """
    # Handle insufficient data
    if sample_size < 30:
        return VerdictResult(
            verdict="Insufficient Data",
            verdict_code="insufficient_data",
            authenticity_score=0,
            confidence_percent=0,
            confidence_band="None",
            explanation=f"Need at least 30 numbers for reliable analysis. Got {sample_size}.",
            sample_size=sample_size
        )
    
    # Compute MAD
    mad = compute_mad(expected, observed)
    
    # Generate verdict components
    verdict_str, verdict_code = p_value_to_verdict(p_value)
    auth_score = authenticity_score_from_mad(mad)
    conf_pct, conf_band = confidence_from_p_value(p_value)
    
    # Generate flags for anomalous digits
    flags = []
    digits = range(1, 10) if digit_position == 1 else range(0, 10)
    
    for i, digit in enumerate(digits):
        if i >= len(expected) or i >= len(observed):
            continue
        
        exp_pct = expected[i] * 100
        act_pct = observed[i] * 100

        # Flag if actual is more than 2x expected OR significantly above uniform
        threshold = exp_pct * 2
        if act_pct > threshold:
            if digit == 7:
                interp = (
                    f"Digit {digit} appears {act_pct:.1f}% of the time "
                    f"(expected: {exp_pct:.1f}%). "
                    f"This pattern may indicate guessed or fabricated data."
                )
            elif digit == 1:
                interp = (
                    f"Digit {digit} appears {act_pct:.1f}% of the time "
                    f"(expected: {exp_pct:.1f}%). "
                    f"An unusually high frequency of leading 1s can indicate "
                    f"artificially inflated or rounded numbers."
                )
            elif act_pct < exp_pct * 0.5:
                interp = (
                    f"Digit {digit} appears {act_pct:.1f}% of the time "
                    f"(expected: {exp_pct:.1f}%). "
                    f"This unusually low frequency is atypical for organic data."
                )
            else:
                interp = (
                    f"Digit {digit} appears {act_pct:.1f}% of the time "
                    f"(expected: {exp_pct:.1f}%). "
                    f"This deviation from expected distribution warrants review."
                )
            
            flags.append(DigitFlag(
                digit=digit,
                digit_position=digit_position,
                expected_pct=exp_pct,
                actual_pct=act_pct,
                interpretation=interp
            ))
    
    # Generate overall explanation
    if verdict_code == "natural":
        explanation = (
            f"The leading digit distribution appears consistent with what would "
            f"naturally occur in real-world data. There's a {conf_pct}% probability "
            f"this pattern could arise by chance."
        )
    elif verdict_code == "suspicious":
        explanation = (
            f"The distribution shows some deviation from expected Benford patterns. "
            f"This may indicate data quality issues, rounding patterns, or "
            f"other anomalies worth investigating. "
            f"There's approximately a {100 - conf_pct}% chance this pattern "
            f"is not due to natural variation."
        )
    else:
        flag_details = []
        for f in flags[:3]:  # Limit to top 3 flags
            flag_details.append(f"digit {f.digit} appears {f.actual_pct:.1f}% vs expected {f.expected_pct:.1f}%")
        
        flag_text = "; ".join(flag_details) if flag_details else "significant deviation from expected distribution"
        explanation = (
            f"The data shows substantial deviation from expected Benford distribution: "
            f"{flag_text}. "
            f"This pattern suggests these numbers warrant a second look. "
            f"Note: This is a statistical signal, not proof of manipulation — "
            f"legitimate exceptions exist for certain data types."
        )
    
    return VerdictResult(
        verdict=verdict_str,
        verdict_code=verdict_code,
        authenticity_score=auth_score,
        confidence_percent=conf_pct,
        confidence_band=conf_band,
        flags=flags,
        explanation=explanation,
        raw_chi_squared=chi_squared,
        raw_p_value=p_value,
        raw_mad=mad,
        sample_size=sample_size
    )


def generate_combined_verdict(first_digit_result: dict, second_digit_result: dict = None) -> dict:
    """Generate a combined verdict from first and second digit analysis.
    
    Args:
        first_digit_result: Dictionary with 'expected', 'observed', 'chi_squared', 'p_value', 'sample_size'
        second_digit_result: Optional second digit analysis dictionary
    
    Returns:
        Dictionary with combined verdict information
    """
    # Use first digit as primary
    verdict = generate_verdict(
        expected=first_digit_result["expected"],
        observed=first_digit_result["observed"],
        chi_squared=first_digit_result["chi_squared"],
        p_value=first_digit_result["p_value"],
        sample_size=first_digit_result["sample_size"],
        digit_position=1
    )
    
    result = verdict.to_dict()
    
    # Add second digit analysis if available
    if second_digit_result and "error" not in second_digit_result:
        second_verdict = generate_verdict(
            expected=second_digit_result["expected"],
            observed=second_digit_result["observed"],
            chi_squared=second_digit_result["chi_squared"],
            p_value=second_digit_result["p_value"],
            sample_size=second_digit_result["sample_size"],
            digit_position=2
        )
        result["second_digit_verdict"] = second_verdict.to_dict()
        
        # Adjust primary verdict if second digit also suspicious
        if second_verdict.verdict_code in ("suspicious", "highly_suspicious"):
            if verdict.verdict_code == "natural":
                result["verdict"] = "Suspicious"
                result["verdict_code"] = "suspicious"
                result["explanation"] = (
                    "While first-digit distribution appears normal, second-digit analysis "
                    "shows suspicious patterns. This combined signal suggests the data "
                    "may benefit from additional review."
                )
    
    return result