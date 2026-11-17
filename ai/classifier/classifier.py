"""Lightweight, deterministic query classifier.

It only gates obvious cases (greetings, clearly harmful requests) and tags a likely legal
topic. It deliberately never blocks a real legal question: anything unclear is passed to
retrieval, and the evidence gate decides whether SPECTRE can answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from ..safety.safety import is_harmful_request


class QueryCategory(str, Enum):
    LEGAL = "legal"
    SMALL_TALK = "small_talk"
    HARMFUL = "harmful"
    UNCLEAR = "unclear"


@dataclass
class Classification:
    category: QueryCategory
    topics: list[str] = field(default_factory=list)


_SMALL_TALK_RE = re.compile(
    r"^\s*(hi|hello|hey|namaste|good (morning|afternoon|evening)|thanks?( you)?|thank you|bye)\W*$",
    re.IGNORECASE,
)

_TOPICS: dict[str, re.Pattern] = {
    "consumer": re.compile(r"consumer|refund|defective|warranty|e-?commerce|seller|product liability|deficiency", re.I),
    "cyber": re.compile(r"cyber|hack|phishing|online|data breach|identity theft|it act|intermediar|social media", re.I),
    "criminal_law": re.compile(r"murder|theft|robbery|assault|cheating|fraud|defamation|bns|nyaya|offence|punishment", re.I),
    "criminal_procedure": re.compile(r"fir|arrest|bail|police|custody|remand|bnss|nagarik|investigation|summons", re.I),
    "evidence": re.compile(r"evidence|witness|admissib|confession|sakshya|electronic record", re.I),
    "constitution": re.compile(r"constitution|fundamental right|article \d+|directive principle|writ|freedom of", re.I),
    "child_protection": re.compile(r"child|minor|pocso|juvenile", re.I),
    "workplace": re.compile(r"workplace|sexual harassment|internal committee|posh|employer", re.I),
}

_GENERAL_LEGAL_RE = re.compile(
    r"\b(law|legal|act|section|article|rights?|court|complaint|lawyer|advocate|illegal|crime|"
    r"penalt(y|ies)|fine|imprisonment|sue|liable|liability|notice|tribunal|petition)\b",
    re.IGNORECASE,
)


class QueryClassifier:
    def classify(self, question: str) -> Classification:
        if _SMALL_TALK_RE.match(question):
            return Classification(QueryCategory.SMALL_TALK)
        if is_harmful_request(question):
            return Classification(QueryCategory.HARMFUL)
        topics = [name for name, pat in _TOPICS.items() if pat.search(question)]
        if topics or _GENERAL_LEGAL_RE.search(question):
            return Classification(QueryCategory.LEGAL, topics)
        return Classification(QueryCategory.UNCLEAR)
