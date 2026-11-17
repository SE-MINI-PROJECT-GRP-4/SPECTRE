"""Citation verification: every citation must trace to retrieved text, verbatim.

The LLM proposes ``{"source_id": "S2", "quote": "..."}``. We keep a citation only if
S2 exists in the context we gave the model AND the quote really appears in that chunk.
Anything else is dropped, so clients never receive a fabricated reference.
"""

from __future__ import annotations

import re
from typing import Sequence

from ..schemas.schemas import Citation, RetrievedChunk

MARKER_RE = re.compile(r"\[S(\d+)\]")
_QUOTE_TRANSLATION = str.maketrans(
    {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "}
)
MAX_QUOTE_CHARS = 400


def normalize(text: str) -> str:
    text = text.translate(_QUOTE_TRANSLATION).lower()
    return re.sub(r"\s+", " ", text).strip()


def _squash(text: str) -> str:
    """Lowercase alphanumerics only: ignores spacing, dashes, quotes and punctuation noise."""
    return re.sub(r"[^a-z0-9]+", "", normalize(text))


def quote_in_text(quote: str, text: str) -> bool:
    """True if the quote appears contiguously in the text (wording must match exactly;
    only whitespace/punctuation differences from PDF extraction are tolerated)."""
    q = _squash(quote)
    if len(q) < 12:
        return False
    return q in _squash(text)


def extract_markers(answer: str) -> list[str]:
    return [f"S{n}" for n in MARKER_RE.findall(answer)]


def verify_citations(
    raw_citations: Sequence[dict], chunks: Sequence[RetrievedChunk]
) -> tuple[list[Citation], list[str]]:
    """Return (verified citations, human-readable problems)."""
    verified: list[Citation] = []
    problems: list[str] = []
    seen: set[str] = set()

    for raw in raw_citations:
        sid = str(raw.get("source_id", "")).strip()
        quote = str(raw.get("quote", "")).strip()
        m = re.fullmatch(r"S(\d+)", sid)
        if not m or not (1 <= int(m.group(1)) <= len(chunks)):
            problems.append(f"Citation {sid or '?'} does not match any retrieved source.")
            continue
        chunk = chunks[int(m.group(1)) - 1]
        if not quote or len(quote) > MAX_QUOTE_CHARS or not quote_in_text(quote, chunk.text):
            problems.append(f"Citation {sid} quote could not be verified against the source text.")
            continue
        if sid in seen:
            continue
        seen.add(sid)
        verified.append(
            Citation(
                source_id=sid,
                chunk_id=chunk.chunk_id,
                document=chunk.document,
                section=chunk.section,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                quote=quote,
                verified=True,
            )
        )
    return verified, problems


def strip_unverified_markers(answer: str, verified: Sequence[Citation]) -> tuple[str, list[str]]:
    """Remove [S#] markers that have no verified citation; return cleaned text + warnings."""
    ok = {c.source_id for c in verified}
    removed: list[str] = []

    def _sub(m: re.Match) -> str:
        sid = f"S{m.group(1)}"
        if sid in ok:
            return m.group(0)
        removed.append(sid)
        return ""

    cleaned = MARKER_RE.sub(_sub, answer)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    warnings = (
        [f"Removed unverifiable reference(s): {', '.join(sorted(set(removed)))}."] if removed else []
    )
    return cleaned, warnings
