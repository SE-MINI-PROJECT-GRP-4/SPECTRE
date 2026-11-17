from ai.safety.citations import quote_in_text, strip_unverified_markers, verify_citations
from ai.schemas.schemas import RetrievedChunk

CHUNK = RetrievedChunk(
    chunk_id="doc:00001",
    text="66C. Punishment for identity theft.—Whoever dishonestly uses the password of another person shall be punished.",
    score=0.8,
    document="Test IT Act",
    section="66C",
    page_start=3,
    page_end=3,
)


def test_verbatim_quote_is_verified():
    cites, problems = verify_citations(
        [{"source_id": "S1", "quote": "dishonestly uses the password of another person"}], [CHUNK]
    )
    assert len(cites) == 1 and not problems
    assert cites[0].section == "66C" and cites[0].page_start == 3


def test_quote_tolerates_whitespace_and_dash_differences():
    assert quote_in_text("identity theft. - Whoever   dishonestly uses", CHUNK.text)


def test_fabricated_quote_is_rejected():
    cites, problems = verify_citations(
        [{"source_id": "S1", "quote": "shall be punished with death and a fine of one crore"}], [CHUNK]
    )
    assert cites == [] and problems


def test_unknown_source_id_is_rejected():
    cites, problems = verify_citations([{"source_id": "S9", "quote": "dishonestly uses the password"}], [CHUNK])
    assert cites == [] and problems


def test_duplicate_citations_collapse():
    raw = [{"source_id": "S1", "quote": "dishonestly uses the password"}] * 2
    cites, _ = verify_citations(raw, [CHUNK])
    assert len(cites) == 1


def test_unverified_markers_are_stripped():
    cites, _ = verify_citations([{"source_id": "S1", "quote": "dishonestly uses the password"}], [CHUNK])
    text, warnings = strip_unverified_markers("It is an offence [S1]. Penalty is huge [S2].", cites)
    assert "[S1]" in text and "[S2]" not in text and warnings
