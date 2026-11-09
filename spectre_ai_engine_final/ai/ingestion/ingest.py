"""Ingestion pipeline: documents -> extraction -> chunking -> embeddings -> ChromaDB."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..config import Settings
from ..retrieval.embeddings import Embedder
from ..retrieval.vector_store import VectorStore
from .document_loader import (
    DocumentLoadError,
    discover_documents,
    load_document,
    load_manifest,
)
from .text_splitter import split_document

logger = logging.getLogger("spectre.ingestion")


@dataclass
class IngestReport:
    ingested: dict[str, int] = field(default_factory=dict)  # file -> chunk count
    skipped_unchanged: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)  # file -> reason
    warnings: dict[str, list[str]] = field(default_factory=dict)

    @property
    def total_chunks(self) -> int:
        return sum(self.ingested.values())

    def summary(self) -> str:
        lines = [
            f"Ingested {len(self.ingested)} document(s), {self.total_chunks} chunk(s); "
            f"{len(self.skipped_unchanged)} unchanged; {len(self.failed)} failed."
        ]
        lines += [f"  FAILED {f}: {why}" for f, why in self.failed.items()]
        lines += [f"  WARN   {f}: {'; '.join(w)}" for f, w in self.warnings.items()]
        return "\n".join(lines)


def ingest_directory(
    settings: Settings, embedder: Embedder, store: VectorStore, reset: bool = False
) -> IngestReport:
    """Ingest every supported file under ``settings.data_dir``.

    Incremental by default: files whose content hash is unchanged are skipped, changed
    files are replaced. ``reset=True`` rebuilds the collection from scratch.
    """
    report = IngestReport()
    if reset:
        store.reset()

    manifest = load_manifest(settings.manifest_path)
    files = discover_documents(settings.data_dir, settings.supported_extensions)
    if not files:
        logger.warning("No documents found under %s", settings.data_dir)

    for path in files:
        try:
            doc = load_document(path, root=settings.data_dir, manifest_entry=manifest.get(path.name.lower()))
        except DocumentLoadError as exc:
            report.failed[path.name] = str(exc)
            logger.error("%s", exc)
            continue

        if store.document_hash(doc.doc_id) == doc.content_hash:
            report.skipped_unchanged.append(path.name)
            continue

        chunks = split_document(
            doc, settings.chunk_size, settings.chunk_overlap, settings.min_chunk_chars
        )
        if not chunks:
                        report.failed[path.name] = (
                "No text could be extracted (likely a scanned PDF: install Tesseract OCR, "
                "or use a text-based copy of the document)."
            )
        continue

        store.delete_document(doc.doc_id)  # replace any previous version
        store.upsert(chunks, embedder.embed_documents([c.embed_text for c in chunks]))
        report.ingested[path.name] = len(chunks)
        if doc.warnings:
            report.warnings[path.name] = doc.warnings
        logger.info("Ingested %s -> %d chunks", path.name, len(chunks))

    return report
