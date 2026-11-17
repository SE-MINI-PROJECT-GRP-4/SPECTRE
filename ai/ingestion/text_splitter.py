"""Legal-structure-aware chunking.

Indian statutes are organised into numbered sections ("66C. Punishment for identity
theft.-..."). Splitting on those boundaries keeps one provision per chunk, which makes
retrieval and citation far more precise than fixed-size windows. Sections longer than
``chunk_size`` are split further (with overlap); documents with no detectable sections
(judgements, rules, prose) fall back to size-based splitting.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass
from typing import Optional

from .document_loader import LoadedDocument

# "66C. Punishment for identity theft.—Whoever ..."  (em/en dash or hyphen after heading)
SECTION_HEADING_RE = re.compile(
    r"^[ \t]*(?P<num>\d{1,3}[A-Z]{0,2})\.[ \t]+"
    r"(?P<heading>[A-Z][^\n]{2,200}?)[.\s]*[—–\-]{1,2}",
    re.MULTILINE,
)


@dataclass
class Chunk:
    chunk_id: str
    text: str  # raw text, stored and shown/cited
    embed_text: str  # text actually embedded (adds document/section context)
    metadata: dict  # flat, scalar-only (ChromaDB requirement)


def _join_pages(doc: LoadedDocument) -> tuple[str, list[int], list[Optional[int]]]:
    """Concatenate pages; return full text plus parallel (offset, page_number) arrays."""
    parts: list[str] = []
    offsets: list[int] = []
    numbers: list[Optional[int]] = []
    pos = 0
    for page in doc.pages:
        offsets.append(pos)
        numbers.append(page.page_number)
        parts.append(page.text)
        pos += len(page.text) + 1  # +1 for the joining newline
    return "\n".join(parts), offsets, numbers


def _page_at(offset: int, offsets: list[int], numbers: list[Optional[int]]) -> Optional[int]:
    idx = max(bisect.bisect_right(offsets, offset) - 1, 0)
    return numbers[idx] if numbers else None


def _split_by_size(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    n = len(text)
    if n <= size:
        return [(0, n)]
    spans: list[tuple[int, int]] = []
    start = 0
    while start < n:
        end = min(start + size, n)
        if end < n:
            lo = start + int(size * 0.6)
            cut = max(text.rfind("\n", lo, end), text.rfind(". ", lo, end), text.rfind("; ", lo, end))
            if cut != -1:
                end = cut + 1
        spans.append((start, end))
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return spans


def split_document(
    doc: LoadedDocument, chunk_size: int = 1200, overlap: int = 150, min_chars: int = 40
) -> list[Chunk]:
    full, offsets, numbers = _join_pages(doc)
    if not full.strip():
        return []

    matches = list(SECTION_HEADING_RE.finditer(full))
    segments: list[tuple[int, int, Optional[str], Optional[str]]] = []
    if matches:
        if matches[0].start() > 0:
            segments.append((0, matches[0].start(), None, None))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(full)
            segments.append((m.start(), end, m.group("num"), m.group("heading").strip()))
    else:
        segments.append((0, len(full), None, None))

    chunks: list[Chunk] = []
    for seg_start, seg_end, num, heading in segments:
        seg = full[seg_start:seg_end]
        for part_idx, (ps, pe) in enumerate(_split_by_size(seg, chunk_size, overlap)):
            raw = seg[ps:pe]
            text = raw.strip()
            if len(text) < min_chars:
                continue
            lead = len(raw) - len(raw.lstrip())
            abs_start = seg_start + ps + lead
            abs_end = seg_start + pe
            p_start = _page_at(abs_start, offsets, numbers)
            p_end = _page_at(max(abs_end - 1, abs_start), offsets, numbers)

            context = doc.short_name
            if num:
                context += f", Section {num}"
                if heading:
                    context += f" ({heading})"
            chunk_id = f"{doc.doc_id}:{len(chunks):05d}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    text=text,
                    embed_text=f"{context}\n{text}",
                    metadata={
                        "doc_id": doc.doc_id,
                        "document": doc.title,
                        "short_name": doc.short_name,
                        "category": doc.category,
                        "section": num or "",
                        "section_heading": heading or "",
                        "page_start": p_start if p_start is not None else -1,
                        "page_end": p_end if p_end is not None else -1,
                        "part": part_idx,
                        "content_hash": doc.content_hash,
                    },
                )
            )
    return chunks
