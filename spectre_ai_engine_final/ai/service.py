"""SpectreService: the single entry point the rest of SPECTRE calls.

Pipeline: validate -> classify -> retrieve -> evidence gate -> generate ->
verify citations -> validate -> score confidence -> respond.
"""

from __future__ import annotations

import logging
from typing import Optional, Union

from .classifier.classifier import QueryCategory, QueryClassifier
from .config import Settings
from .generation.generator import GenerationError, Generator, LLMClient, get_llm
from .ingestion.ingest import IngestReport, ingest_directory
from .retrieval.embeddings import Embedder, get_embedder
from .retrieval.retriever import Retriever
from .retrieval.vector_store import VectorStore
from .safety import safety
from .safety.citations import strip_unverified_markers, verify_citations
from .safety.uncertainty import evidence_is_sufficient, score_confidence
from .safety.validations import validate_answer, validate_question
from .schemas.schemas import AnswerStatus, ConfidenceLabel, QueryRequest, QueryResponse

logger = logging.getLogger("spectre.service")


class SpectreService:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        embedder: Optional[Embedder] = None,
        store: Optional[VectorStore] = None,
        llm: Optional[LLMClient] = None,
        classifier: Optional[QueryClassifier] = None,
    ):
        self.settings = settings or Settings.from_env()
        self.embedder = embedder or get_embedder(self.settings)
        self.store = store or VectorStore(self.settings.chroma_dir, self.settings.collection_name)
        self.llm = llm or get_llm(self.settings)
        self.classifier = classifier or QueryClassifier()
        self.retriever = Retriever(self.store, self.embedder, self.settings)
        self.generator = Generator(self.llm, self.settings)

    # ---- ingestion ------------------------------------------------------
    def ingest(self, reset: bool = False) -> IngestReport:
        return ingest_directory(self.settings, self.embedder, self.store, reset=reset)

    def health(self) -> dict:
        return {"indexed_chunks": self.store.count(), "documents": len(self.store.list_documents())}

    # ---- querying -------------------------------------------------------
    def ask(self, request: Union[str, dict, QueryRequest]) -> QueryResponse:
        """Answer a question. Never raises: failures become an ERROR/INVALID_INPUT response."""
        try:
            return self._ask(request)
        except Exception:  # last-resort guard; the contract promises no exceptions
            logger.exception("Unhandled error in SpectreService.ask")
            return self._respond(AnswerStatus.ERROR, safety.ERROR_MESSAGE)

    def _ask(self, request: Union[str, dict, QueryRequest]) -> QueryResponse:
        top_k: Optional[int] = None
        if isinstance(request, str):
            raw_question: object = request
        elif isinstance(request, dict):
            raw_question, top_k = request.get("question"), request.get("top_k")
        else:
            raw_question, top_k = request.question, request.top_k

        check = validate_question(raw_question, self.settings)
        if check.error:
            return self._respond(AnswerStatus.INVALID_INPUT, check.error)
        question, warnings = check.question, list(check.warnings)

        cls = self.classifier.classify(question)
        if cls.category == QueryCategory.SMALL_TALK:
            return self._respond(AnswerStatus.OUT_OF_SCOPE, safety.SMALL_TALK_MESSAGE)
        if cls.category == QueryCategory.HARMFUL:
            return self._respond(AnswerStatus.REFUSED, safety.REFUSAL_MESSAGE)

        helplines = safety.helplines_for(question)

        try:
            chunks = self.retriever.retrieve(question, top_k=top_k)
        except Exception:
            logger.exception("Retrieval failed")
            return self._respond(AnswerStatus.ERROR, safety.ERROR_MESSAGE)

        if not evidence_is_sufficient(chunks, self.settings):
            if cls.category == QueryCategory.UNCLEAR:
                return self._respond(AnswerStatus.OUT_OF_SCOPE, safety.OUT_OF_SCOPE_MESSAGE, helplines=helplines)
            return self._respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE, safety.INSUFFICIENT_MESSAGE, warnings=warnings, helplines=helplines
            )

        try:
            raw, shown = self.generator.generate(question, chunks)
        except GenerationError as exc:
            logger.error("Generation failed: %s", exc)
            return self._respond(AnswerStatus.ERROR, safety.ERROR_MESSAGE, helplines=helplines)

        if raw.insufficient_evidence:
            return self._respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE, safety.INSUFFICIENT_MESSAGE, warnings=warnings, helplines=helplines
            )

        citations, problems = verify_citations(raw.citations, shown)
        answer, marker_warnings = strip_unverified_markers(raw.answer, citations)
        warnings += problems + marker_warnings

        reason = validate_answer(answer, citations)
        if reason:
            logger.warning("Answer rejected: %s", reason)
            return self._respond(
                AnswerStatus.INSUFFICIENT_EVIDENCE, safety.INSUFFICIENT_MESSAGE, warnings=warnings, helplines=helplines
            )

        confidence, label = score_confidence(answer, citations, shown)
        if label == ConfidenceLabel.LOW:
            warnings.append("Low confidence: please verify against the cited sources.")

        return QueryResponse(
            status=AnswerStatus.ANSWERED,
            answer=answer,
            citations=citations,
            confidence=confidence,
            confidence_label=label,
            disclaimer=safety.DISCLAIMER,
            warnings=warnings,
            helplines=helplines,
        )

    @staticmethod
    def _respond(
        status: AnswerStatus,
        message: str,
        warnings: Optional[list[str]] = None,
        helplines: Optional[list[str]] = None,
    ) -> QueryResponse:
        return QueryResponse(
            status=status,
            answer=message,
            disclaimer=safety.DISCLAIMER,
            warnings=warnings or [],
            helplines=helplines or [],
        )
