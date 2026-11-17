"""ChromaDB persistence: embeddings, text and metadata (cosine space)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..ingestion.text_splitter import Chunk
from ..schemas.schemas import RetrievedChunk

_BATCH = 500


def _to_chunk(doc: str, meta: dict, score: float, exact: bool = False, cid: str = "") -> RetrievedChunk:
    page_start = meta.get("page_start", -1)
    page_end = meta.get("page_end", -1)
    return RetrievedChunk(
        chunk_id=cid,
        text=doc,
        score=score,
        doc_id=meta.get("doc_id", ""),
        document=meta.get("document", ""),
        short_name=meta.get("short_name", ""),
        category=meta.get("category", ""),
        section=meta.get("section") or None,
        section_heading=meta.get("section_heading") or None,
        page_start=page_start if page_start is not None and page_start >= 0 else None,
        page_end=page_end if page_end is not None and page_end >= 0 else None,
        exact_match=exact,
    )


class VectorStore:
    def __init__(self, persist_dir: Optional[Path], collection_name: str):
        settings = ChromaSettings(anonymized_telemetry=False)
        if persist_dir is None:
            self._client = chromadb.EphemeralClient(settings=settings)
        else:
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(persist_dir), settings=settings)
        self._name = collection_name
        self._collection = self._open()

    def _open(self):
        return self._client.get_or_create_collection(
            name=self._name, metadata={"hnsw:space": "cosine"}
        )

    # ---- writes ---------------------------------------------------------
    def upsert(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        for i in range(0, len(chunks), _BATCH):
            batch = chunks[i : i + _BATCH]
            self._collection.upsert(
                ids=[c.chunk_id for c in batch],
                documents=[c.text for c in batch],
                embeddings=[list(e) for e in embeddings[i : i + _BATCH]],
                metadatas=[c.metadata for c in batch],
            )

    def delete_document(self, doc_id: str) -> None:
        self._collection.delete(where={"doc_id": doc_id})

    def reset(self) -> None:
        self._client.delete_collection(self._name)
        self._collection = self._open()

    # ---- reads ----------------------------------------------------------
    def count(self) -> int:
        return self._collection.count()

    def document_hash(self, doc_id: str) -> Optional[str]:
        res = self._collection.get(where={"doc_id": doc_id}, limit=1, include=["metadatas"])
        metas = res.get("metadatas") or []
        return metas[0].get("content_hash") if metas else None

    def list_documents(self) -> dict[str, str]:
        res = self._collection.get(include=["metadatas"])
        return {m["doc_id"]: m.get("document", "") for m in (res.get("metadatas") or [])}

    def query(
        self, embedding: Sequence[float], top_k: int, where: Optional[dict] = None
    ) -> list[RetrievedChunk]:
        total = self.count()
        if total == 0:
            return []
        res = self._collection.query(
            query_embeddings=[list(embedding)],
            n_results=min(top_k, total),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        out = []
        for cid, doc, meta, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            out.append(_to_chunk(doc, meta, 1.0 - float(dist), cid=cid))
        return out

    def get_by_section(self, section: str, query_embedding: Sequence[float]) -> list[RetrievedChunk]:
        """All chunks for a section number (any document), scored against the query."""
        res = self._collection.get(
            where={"section": section}, include=["documents", "metadatas", "embeddings"]
        )
        out = []
        for cid, doc, meta, emb in zip(
            res["ids"], res["documents"], res["metadatas"], res["embeddings"]
        ):
            score = sum(float(a) * float(b) for a, b in zip(query_embedding, emb))
            out.append(_to_chunk(doc, meta, score, exact=True, cid=cid))
        return out
