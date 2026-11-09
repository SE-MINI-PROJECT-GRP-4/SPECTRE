# SPECTRE AI Contract

The agreement between the AI engine (`ai/`) and anything that calls it (backend, UI).
Enforced by `tests/test_contract.py`.

## Entry point

```python
from ai.service import SpectreService

service = SpectreService()        # reads SPECTRE_* env vars; needs ANTHROPIC_API_KEY
service.ingest()                  # build/refresh the index (also: python -m ai.ingest)
response = service.ask("What can I do about a defective product?")   # -> QueryResponse
```

`ask()` accepts a string, a `{"question": ..., "top_k": ...}` dict, or a `QueryRequest`.
**`ask()` never raises.** Failures are reported through `status`.

## Request

| Field      | Type        | Rules                                             |
|------------|-------------|---------------------------------------------------|
| `question` | string      | Required. 1 to 2000 characters after cleaning.    |
| `top_k`    | int, 1-20   | Optional. Number of source chunks to retrieve.    |

## Response (`QueryResponse`)

| Field              | Type             | Meaning                                                          |
|--------------------|------------------|------------------------------------------------------------------|
| `status`           | enum (below)     | Outcome of the request.                                          |
| `answer`           | string           | Answer text with `[S1]`-style markers, or an explanatory message.|
| `citations`        | list[Citation]   | Verified sources. Non-empty only when `status == "answered"`.    |
| `confidence`       | float 0-1        | Heuristic score (not a calibrated probability).                  |
| `confidence_label` | enum             | `high`, `medium`, `low`, `none`.                                 |
| `disclaimer`       | string           | Always present; UIs must display it with answers.                |
| `warnings`         | list[string]     | Non-fatal notes (e.g. dropped unverifiable references).          |
| `helplines`        | list[string]     | Relevant emergency/helpline numbers, if the question suggests need.|

### Citation

| Field        | Type          | Meaning                                              |
|--------------|---------------|------------------------------------------------------|
| `source_id`  | string        | Matches a marker in `answer`, e.g. `S1`.             |
| `chunk_id`   | string        | Stable id of the stored chunk.                       |
| `document`   | string        | Title of the source document.                        |
| `section`    | string/null   | Section or Article number when detected.             |
| `page_start` | int/null      | First page (PDF only; null for DOCX/TXT).            |
| `page_end`   | int/null      | Last page.                                           |
| `quote`      | string        | Verbatim excerpt found in the source text.           |
| `verified`   | bool          | Always `true` in returned citations.                 |

## Status values

| `status`                | When                                                                 | `citations` |
|-------------------------|----------------------------------------------------------------------|-------------|
| `answered`              | Evidence found and at least one citation verified.                   | 1 or more   |
| `insufficient_evidence` | Relevant area but not enough support, or no citation could be verified. | none     |
| `out_of_scope`          | Not an Indian-law question we can answer, or small talk/greeting.    | none        |
| `refused`               | Request seeks help committing or concealing an offence.              | none        |
| `invalid_input`         | Empty, non-text, or over-length question.                            | none        |
| `error`                 | Internal or LLM failure. Safe to retry.                              | none        |

## Guarantees

1. Every `answered` response has at least one citation, each with `verified: true`.
2. A citation's `quote` appears (after whitespace/quote-style normalisation) in the stored
   source chunk it points to. Fabricated references are dropped, never returned.
3. Every `[S#]` marker left in `answer` corresponds to an entry in `citations`.
4. Non-`answered` responses carry no citations and never present guesses as legal fact.
5. The engine answers only from ingested documents; it adds no outside legal knowledge.
6. Output is information, not legal advice; `disclaimer` is always populated.

## Out of scope for the engine

Authentication, rate limiting, conversation history and HTTP transport belong to the backend.
