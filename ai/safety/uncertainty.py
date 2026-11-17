"""Evidence sufficiency and confidence scoring.

Confidence is a transparent heuristic, not a calibrated probability. It combines how well
retrieval matched, how much of the answer is backed by verified citations, and how many
distinct sources agree.
"""

from __future__ import annotations

import re
from typing import Sequence

from ..config import Settings
from ..schemas.schemas import Citation, ConfidenceLabel, RetrievedChunk
from .citations import MARKER_RE


def evidence_is_sufficient(chunks: Sequence[RetrievedChunk], settings: Settings) -> bool:
    """Gate run BEFORE calling the LLM: is there anything worth answering from?"""
    if not chunks:
        return False
    return any(c.exact_match for c in chunks) or max(c.score for c in chunks) >= settings.min_top_score


def _citation_coverage(answer: str, verified_ids: set[str]) -> float:
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer) if len(s.strip()) > 20]
    if not sentences:
        return 0.0
    backed = sum(1 for s in sentences if any(f"S{n}" in verified_ids for n in MARKER_RE.findall(s)))
    return backed / len(sentences)


def score_confidence(
    answer: str, citations: Sequence[Citation], chunks: Sequence[RetrievedChunk]
) -> tuple[float, ConfidenceLabel]:
    if not citations or not chunks:
        return 0.0, ConfidenceLabel.NONE
    top = max(0.0, min(1.0, max(c.score for c in chunks)))
    coverage = _citation_coverage(answer, {c.source_id for c in citations})
    breadth = min(len(citations), 3) / 3
    score = round(0.4 * top + 0.4 * coverage + 0.2 * breadth, 3)
    label = (
        ConfidenceLabel.HIGH if score >= 0.75 else ConfidenceLabel.MEDIUM if score >= 0.5 else ConfidenceLabel.LOW
    )
    return score, label
