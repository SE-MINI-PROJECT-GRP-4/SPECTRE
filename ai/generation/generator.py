"""LLM generation. The LLM sits behind a small protocol so it is swappable and mockable."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Protocol, Sequence

from ..config import Settings
from ..schemas.schemas import RetrievedChunk
from .prompts import SYSTEM_PROMPT, build_user_prompt, format_sources


class GenerationError(Exception):
    """The LLM call failed or returned something unusable."""


class LLMClient(Protocol):
    def complete(self, system: str, user: str, max_tokens: int) -> str: ...


class AnthropicLLM:
    """Claude via the Anthropic API. Reads ANTHROPIC_API_KEY from the environment."""

    def __init__(self, model: str):
        self.model = model
        self._client = None

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic()
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


class OllamaLLM:
    """Local open-source models via Ollama's HTTP API (no extra dependency)."""

    def __init__(self, model: str, base_url: str, num_ctx: int, timeout_s: float, think: bool = False):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.num_ctx = num_ctx
        self.timeout_s = timeout_s
        self.think = think

    def complete(self, system: str, user: str, max_tokens: int) -> str:
        import urllib.request

        payload = {
            "model": self.model,
            "stream": False,
            "think": self.think,  # ignored by models without a thinking mode
            "format": "json",  # constrains output to valid JSON
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0, "num_ctx": self.num_ctx, "num_predict": max_tokens},
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body.get("message", {}).get("content", "")


def get_llm(settings: Settings) -> "LLMClient":
    if settings.llm_provider == "ollama":
        return OllamaLLM(
            settings.llm_model,
            settings.ollama_base_url,
            settings.ollama_num_ctx,
            settings.llm_timeout_s,
            settings.ollama_think,
        )
    if settings.llm_provider == "anthropic":
        return AnthropicLLM(settings.llm_model)
    raise ValueError(f"Unknown llm_provider: {settings.llm_provider!r}")


@dataclass
class RawAnswer:
    answer: str
    citations: list[dict] = field(default_factory=list)
    insufficient_evidence: bool = False
    raw: str = ""


_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_llm_json(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)  # reasoning models
    cleaned = _FENCE_RE.sub("", text.strip())
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise GenerationError("LLM response contained no JSON object.")
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise GenerationError(f"LLM response was not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise GenerationError("LLM JSON was not an object.")
    return data


class Generator:
    def __init__(self, llm: LLMClient, settings: Settings):
        self.llm = llm
        self.settings = settings

    def generate(self, question: str, chunks: Sequence[RetrievedChunk]) -> tuple[RawAnswer, list[RetrievedChunk]]:
        """Return the parsed answer and the chunks actually shown to the model.

        Source ids (S1, S2, ...) index into the returned chunk list, so citation
        verification must use that list, not the original retrieval result.
        """
        shown = _chunks_within_budget(chunks, self.settings.max_context_chars)
        user = build_user_prompt(question, shown, self.settings.max_context_chars)
        try:
            text = self.llm.complete(SYSTEM_PROMPT, user, self.settings.llm_max_tokens)
        except Exception as exc:  # network, auth, rate limit...
            raise GenerationError(f"LLM call failed: {exc}") from exc

        data = parse_llm_json(text)
        citations = data.get("citations") or []
        if not isinstance(citations, list):
            raise GenerationError("'citations' must be a list.")
        return (
            RawAnswer(
                answer=str(data.get("answer") or "").strip(),
                citations=[c for c in citations if isinstance(c, dict)],
                insufficient_evidence=bool(data.get("insufficient_evidence", False)),
                raw=text,
            ),
            shown,
        )


def _chunks_within_budget(chunks: Sequence[RetrievedChunk], max_chars: int) -> list[RetrievedChunk]:
    kept: list[RetrievedChunk] = []
    for i in range(1, len(chunks) + 1):
        candidate = list(chunks[:i])
        if kept and len(format_sources(candidate, 10**9)) > max_chars:
            break
        kept = candidate
    return kept
