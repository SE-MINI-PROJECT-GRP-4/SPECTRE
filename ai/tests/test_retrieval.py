from ai.ingestion.document_loader import LoadedDocument, PageText
from ai.ingestion.text_splitter import split_document
from ai.retrieval.embeddings import HashingEmbedder
from ai.retrieval.retriever import Retriever, extract_section_refs
from pathlib import Path


def make_doc(text: str) -> LoadedDocument:
    return LoadedDocument("d1", Path("d.txt"), "Doc", "Doc", "acts", None, "h", [PageText(1, text)])


def test_splitter_splits_on_section_boundaries():
    text = (
        "Preamble text that is long enough to keep around.\n"
        "1. Short title.—This Act may be called the Test Act and applies everywhere.\n"
        "2. Definitions.—In this Act, a thing means any thing at all, unless context requires."
    )
    chunks = split_document(make_doc(text))
    assert [c.metadata["section"] for c in chunks] == ["", "1", "2"]
    assert chunks[2].metadata["section_heading"] == "Definitions"
    assert chunks[1].metadata["page_start"] == 1


def test_splitter_falls_back_to_size_windows_with_overlap():
    text = ("This sentence repeats to build a long unstructured judgement. " * 80).strip()
    chunks = split_document(make_doc(text), chunk_size=500, overlap=50)
    assert len(chunks) > 3 and all(len(c.text) <= 500 for c in chunks)


def test_extract_section_refs():
    assert extract_section_refs("what does Section 66C say and Article 21?") == ["66C", "21"]


def test_ingestion_is_incremental(make_service):
    svc = make_service()
    first = svc.store.count()
    assert first > 0
    report = svc.ingest()
    assert report.ingested == {} and len(report.skipped_unchanged) == 2
    assert svc.store.count() == first


def test_semantic_retrieval_finds_right_provision(make_service):
    svc = make_service()
    top = svc.retriever.retrieve("someone used my password to steal my identity")[0]
    assert top.section == "66C"


def test_exact_section_reference_is_boosted(make_service):
    svc = make_service()
    results = svc.retriever.retrieve("explain section 35")
    assert results[0].section == "35" and results[0].exact_match


def test_irrelevant_query_returns_nothing(make_service):
    svc = make_service()
    assert Retriever(svc.store, HashingEmbedder(), svc.settings).retrieve("zebra giraffe quantum") == []
