"""Keeps docs/AI_CONTRACT.md and the code honest with each other."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai.schemas.schemas import AnswerStatus, Citation, ConfidenceLabel, QueryResponse

CONTRACT = (Path(__file__).resolve().parents[1] / "docs" / "AI_CONTRACT.md").read_text(encoding="utf-8")

QUOTE_OK = {"source_id": "S1", "quote": "uses the password or unique identification feature of another person"}
LLM_OK = {"answer": "Dishonest use of a password is punishable [S1].", "citations": [QUOTE_OK], "insufficient_evidence": False}


def test_contract_documents_every_status_and_field():
    for status in AnswerStatus:
        assert f"`{status.value}`" in CONTRACT, status
    for label in ConfidenceLabel:
        assert label.value in CONTRACT
    for name in list(QueryResponse.model_fields) + list(Citation.model_fields):
        assert f"`{name}`" in CONTRACT, name


def test_answered_requires_citations():
    with pytest.raises(ValidationError):
        QueryResponse(status=AnswerStatus.ANSWERED, answer="x")


def test_only_answered_may_carry_citations():
    cite = Citation(source_id="S1", chunk_id="c", document="d", quote="q")
    with pytest.raises(ValidationError):
        QueryResponse(status=AnswerStatus.OUT_OF_SCOPE, answer="x", citations=[cite])


def test_unverified_citation_rejected():
    cite = Citation(source_id="S1", chunk_id="c", document="d", quote="q", verified=False)
    with pytest.raises(ValidationError):
        QueryResponse(status=AnswerStatus.ANSWERED, answer="x", citations=[cite])


def test_ask_never_raises_and_responses_are_json_serialisable(make_service, FakeLLMClass):
    svc = make_service(FakeLLMClass(LLM_OK))
    for q in ["identity theft password law", "", "hello", "how to evade arrest", "zebra quantum", None, 42]:
        r = svc.ask(q)
        assert isinstance(r, QueryResponse) and r.disclaimer
        json.loads(r.model_dump_json())


def test_every_marker_in_answer_has_a_citation(make_service, FakeLLMClass):
    r = make_service(FakeLLMClass(LLM_OK)).ask("identity theft password law")
    assert r.status == AnswerStatus.ANSWERED
    ids = {c.source_id for c in r.citations}
    from ai.safety.citations import extract_markers

    assert set(extract_markers(r.answer)) <= ids
