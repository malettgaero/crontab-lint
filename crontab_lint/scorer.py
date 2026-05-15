"""Complexity and quality scorer for crontab expressions."""

from dataclasses import dataclass, field
from typing import List

from .validator import validate
from .parser import parse


@dataclass
class ScoreResult:
    expression: str
    score: int  # 0-100, higher is better (simpler, safer)
    grade: str
    penalties: List[str] = field(default_factory=list)
    is_valid: bool = True

    def __bool__(self) -> bool:
        return self.is_valid


_GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (55, "C"),
    (35, "D"),
    (0,  "F"),
]


def _assign_grade(score: int) -> str:
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def score(expression: str) -> ScoreResult:
    """Score a crontab expression for complexity and quality.

    Returns a ScoreResult with a 0-100 score and letter grade.
    Higher scores indicate simpler, more readable expressions.
    """
    result = validate(expression)
    if not result:
        return ScoreResult(
            expression=expression,
            score=0,
            grade="F",
            penalties=[f"Invalid expression: {'; '.join(result.errors)}"],
            is_valid=False,
        )

    parsed = parse(expression)
    penalties: List[str] = []
    deductions = 0

    fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]

    # Penalise each non-wildcard field
    non_wildcard = sum(1 for f in fields if f != "*")
    if non_wildcard >= 4:
        deductions += 15
        penalties.append("Very specific schedule (4+ constrained fields)")
    elif non_wildcard >= 3:
        deductions += 8
        penalties.append("Specific schedule (3 constrained fields)")

    # Penalise lists (comma-separated values)
    list_fields = [f for f in fields if "," in f]
    if list_fields:
        deductions += len(list_fields) * 5
        penalties.append(f"{len(list_fields)} field(s) use comma lists")

    # Penalise nested ranges with steps
    complex_fields = [f for f in fields if "/" in f and "-" in f]
    if complex_fields:
        deductions += len(complex_fields) * 8
        penalties.append(f"{len(complex_fields)} field(s) combine range and step")

    # Penalise both DOM and DOW being set (ambiguous semantics)
    if parsed.day_of_month != "*" and parsed.day_of_week != "*":
        deductions += 10
        penalties.append("Both day-of-month and day-of-week are set (ambiguous)")

    # Reward alias usage (expression was an alias before parsing)
    if expression.strip().startswith("@"):
        deductions -= 5  # bonus

    final_score = max(0, min(100, 100 - deductions))
    return ScoreResult(
        expression=expression,
        score=final_score,
        grade=_assign_grade(final_score),
        penalties=penalties,
        is_valid=True,
    )
