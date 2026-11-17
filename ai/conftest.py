"""Shared test fixtures. Tests use a synthetic corpus, a hashing embedder and a fake LLM,
so they run offline with no API key and no model downloads."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from ai.config import Settings
from ai.retrieval.embeddings import HashingEmbedder
from ai.retrieval.vector_store import VectorStore
from ai.service import SpectreService

IT_ACT_FIXTURE = """\
Test Information Technology Act (synthetic fixture)

66C. Punishment for identity theft.—Whoever dishonestly uses the password or unique identification feature of another person shall be punished with imprisonment up to three years and fine.

66D. Punishment for cheating by personation using a computer resource.—Whoever cheats by personation using any communication device or computer resource shall be punished with imprisonment up to three years and fine.
"""

CONSUMER_FIXTURE = """\
Test Consumer Protection Act (synthetic fixture)

2. Definitions.—A consumer is a person who buys goods or hires services for consideration, and a defect means any fault in the quality of goods.

35. Manner in which complaint shall be made.—A consumer may file a complaint before the District Commission about defective goods or deficiency in services, and may seek refund or replacement.
"""


class FakeLLM:
    """Returns a canned response and records calls."""

    def __init__(self, response=None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        self.calls.append((system, user))
        if self.error:
            raise self.error
        if callable(self.response):
            return self.response(system, user)
        return self.response if isinstance(self.response, str) else json.dumps(self.response)


@pytest.fixture
def FakeLLMClass():
    return FakeLLM


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    docs = tmp_path / "legal documents"
    (docs / "acts").mkdir(parents=True)
    (docs / "acts" / "it_act_fixture.txt").write_text(IT_ACT_FIXTURE, encoding="utf-8")
    (docs / "acts" / "consumer_fixture.txt").write_text(CONSUMER_FIXTURE, encoding="utf-8")
    return replace(
        Settings(),
        data_dir=docs,
        manifest_path=tmp_path / "manifest.json",
        chroma_dir=tmp_path / "chroma",
        embedding_model="hashing",
        min_similarity=0.1,
        min_top_score=0.15,  # the hashing embedder scores lower than a real semantic model
    )


@pytest.fixture
def store(settings: Settings) -> VectorStore:
    return VectorStore(settings.chroma_dir, settings.collection_name)


@pytest.fixture
def make_service(settings: Settings, store: VectorStore):
    def _make(llm: FakeLLM | None = None, ingest: bool = True) -> SpectreService:
        svc = SpectreService(settings=settings, embedder=HashingEmbedder(), store=store, llm=llm or FakeLLM({}))
        if ingest:
            svc.ingest()
        return svc

    return _make
