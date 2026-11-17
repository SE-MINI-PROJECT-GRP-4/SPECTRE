"""CLI: build or refresh the SPECTRE vector index.

    python -m ai.ingest            # incremental (skips unchanged files)
    python -m ai.ingest --reset    # rebuild from scratch
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import replace
from pathlib import Path

from .config import Settings
from .retrieval.embeddings import get_embedder
from .retrieval.vector_store import VectorStore
from .ingestion.ingest import ingest_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest legal documents into ChromaDB.")
    parser.add_argument("--reset", action="store_true", help="Rebuild the index from scratch.")
    parser.add_argument("--data-dir", type=Path, help="Override the legal documents folder.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    if args.data_dir:
        settings = replace(settings, data_dir=args.data_dir)

    store = VectorStore(settings.chroma_dir, settings.collection_name)
    report = ingest_directory(settings, get_embedder(settings), store, reset=args.reset)
    print(report.summary())
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
