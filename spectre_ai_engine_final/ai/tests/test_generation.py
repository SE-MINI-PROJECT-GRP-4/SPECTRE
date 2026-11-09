import pytest

from ai.config import Settings
from ai.generation.generator import GenerationError, Generator, parse_llm_json
from ai.generation.prompts import SYSTEM_PROMPT, format_sources
from ai.schemas.schemas import RetrievedChunk


def chunk(i: int, text: str = "Some provision text that is long enough.") -> RetrievedChunk:
    return RetrievedChunk(chunk_id=f"c{i}", text=text, score=0.7, document="Doc", section=str(i))


def test_parse_plain_and_fenced_json():
    assert parse_llm_json('{"answer": "x"}')["answer"] == "x"
    assert parse_llm_json('```json\n{"answer": "x"}\n```')["answer"] == "x"


def test_parse_strips_reasoning_block():
    text = '<think>maybe {"answer": "wrong"} hmm</think>{"answer": "right"}'
    assert parse_llm_json(text)["answer"] == "right"


@pytest.mark.parametrize("bad", ["no json here", "{not valid}", "[1, 2]"])
def test_parse_rejects_garbage(bad):
    with pytest.raises(GenerationError):
        parse_llm_json(bad)


def test_prompt_numbers_sources_and_demands_verbatim_quotes():
    out = format_sources([chunk(1), chunk(2)], 10_000)
    assert 'id="S1"' in out and 'id="S2"' in out
    assert "VERBATIM" in SYSTEM_PROMPT


def test_generator_returns_chunks_actually_shown(FakeLLMClass):
    llm = FakeLLMClass({"answer": "a [S1]", "citations": [{"source_id": "S1", "quote": "x"}]})
    settings = Settings(max_context_chars=400)
    big = [chunk(i, "word " * 60) for i in range(1, 6)]
    raw, shown = Generator(llm, settings).generate("q?", big)
    assert 1 <= len(shown) < len(big)  # context budget respected
    assert raw.answer == "a [S1]"


def test_llm_failure_becomes_generation_error(FakeLLMClass):
    gen = Generator(FakeLLMClass(error=RuntimeError("boom")), Settings())
    with pytest.raises(GenerationError):
        gen.generate("q?", [chunk(1)])


def test_ollama_adapter_builds_request_and_parses_reply(monkeypatch):
    import io
    import json as _json

    from ai.generation.generator import OllamaLLM, get_llm

    seen = {}

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["body"] = _json.loads(req.data)
        return FakeResp(_json.dumps({"message": {"content": '{"answer": "ok"}'}}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    llm = OllamaLLM("llama3.1:8b", "http://localhost:11434/", 8192, 30)
    assert llm.complete("sys", "usr", 500) == '{"answer": "ok"}'
    assert seen["url"] == "http://localhost:11434/api/chat"
    assert seen["body"]["format"] == "json" and seen["body"]["options"]["num_ctx"] == 8192
    assert seen["body"]["think"] is False
    assert isinstance(get_llm(Settings()), OllamaLLM)


def test_unknown_provider_is_rejected():
    from dataclasses import replace

    from ai.generation.generator import get_llm

    with pytest.raises(ValueError):
        get_llm(replace(Settings(), llm_provider="nope"))
