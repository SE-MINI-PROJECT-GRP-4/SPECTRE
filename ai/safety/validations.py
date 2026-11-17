"""Input and output validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Sequence

from ..config import Settings
from ..schemas.schemas import Citation

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_INJECTION_RE = re.compile(
    r"ignore (all |any |the )?(previous|prior|above) (instructions|rules)|"
    r"disregard (the )?(system|previous) (prompt|instructions)|"
    r"reveal (your|the) (system )?prompt|you are now ",
    re.IGNORECASE,
)


@dataclass
class QuestionCheck:
    question: str
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


def validate_question(question: object, settings: Settings) -> QuestionCheck:
    if not isinstance(question, str):
        return QuestionCheck("", error="Question must be text.")
    cleaned = re.sub(r"\s+", " ", _CONTROL_RE.sub(" ", question)).strip()
    if not cleaned:
        return QuestionCheck("", error="Please enter a question.")
    if len(cleaned) > settings.max_question_chars:
        return QuestionCheck(
            cleaned[: settings.max_question_chars],
            error=f"Question is too long (limit {settings.max_question_chars} characters).",
        )
    warnings = []
    if _INJECTION_RE.search(cleaned):
        warnings.append("Instruction-like text in the question was ignored.")
    return QuestionCheck(cleaned, warnings=warnings)


def validate_answer(answer: str, citations: Sequence[Citation]) -> Optional[str]:
    """Return a reason string if the answer is unacceptable, else None."""
    if not answer.strip():
        return "Model produced an empty answer."
    if not citations:
        return "No citation could be verified against the source documents."
    return None
