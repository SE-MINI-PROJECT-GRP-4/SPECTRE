"""Hybrid retrieval: semantic search plus exact "Section 66C" / "Article 21" lookups.

Pure semantic search is weak at statute numbers, which is how lawyers and the public
often phrase questions. When the query names a section or article we also fetch chunks
carrying that number and boost them (re-scored against the query, so the right Act wins
when several share a section number).
"""

from __future__ import annotations

import re
from typing import Optional

from ..config import Settings
from ..schemas.schemas import RetrievedChunk
from .embeddings import Embedder
from .vector_store import VectorStore

SECTION_REF_RE = re.compile(
    r"\b(?:sections?|sec\.?|s\.|articles?|art\.?)\s*(\d{1,3}[A-Za-z]{0,2})\b", re.IGNORECASE
)


def extract_section_refs(query: str) -> list[str]:
    seen: list[str] = []
    for m in SECTION_REF_RE.finditer(query):
        ref = m.group(1).upper()
        if ref not in seen:
            seen.append(ref)
    return seen


class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder, settings: Settings):
        self.store = store
        self.embedder = embedder
        self.settings = settings

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[RetrievedChunk]:
        k = top_k or self.settings.top_k
        q_emb = self.embedder.embed_query(query)

        candidates: dict[str, RetrievedChunk] = {}
        for chunk in self.store.query(q_emb, top_k=k * 2):
            if chunk.score >= self.settings.min_similarity:
                candidates[chunk.chunk_id] = chunk

        for ref in extract_section_refs(query):
            for chunk in self.store.get_by_section(ref, q_emb):
                boosted = min(chunk.score + self.settings.exact_ref_bonus, 1.0)
                existing = candidates.get(chunk.chunk_id)
                if existing is None or boosted > existing.score:
                    candidates[chunk.chunk_id] = chunk.model_copy(
                        update={"score": boosted, "exact_match": True}
                    )

        ranked = sorted(candidates.values(), key=lambda c: c.score, reverse=True)
        return ranked[:k]
