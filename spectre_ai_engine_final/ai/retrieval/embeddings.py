"""Embedding backends.

* ``SentenceTransformerEmbedder`` - production (Sentence Transformers, per the pipeline diagram).
* ``HashingEmbedder`` - deterministic, dependency-free bag-of-words vectors. Lexical only, NOT
  semantic. For offline development and automated tests.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, Sequence

_STOPWORDS = frozenset(
    "a an and are as at be by for from has have how i if in is it its of on or that the "
    "this to was were what when where which who will with can do does my me you your".split()
)


class Embedder(Protocol):
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str, query_prefix: str = "", batch_size: int = 32):
        self.model_name = model_name
        self.query_prefix = query_prefix
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = self._load().encode(
            list(texts),
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        vec = self._load().encode(
            self.query_prefix + text, normalize_embeddings=True, show_progress_bar=False
        )
        return vec.tolist()


class HashingEmbedder:
    def __init__(self, dimension: int = 512):
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            if token in _STOPWORDS:
                continue
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            vec[h % self.dimension] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm else vec

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_embedder(settings) -> Embedder:
    if settings.embedding_model == "hashing":
        return HashingEmbedder()
    return SentenceTransformerEmbedder(settings.embedding_model, settings.query_prefix)
