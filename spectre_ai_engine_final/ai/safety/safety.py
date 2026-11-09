"""User-facing safety messaging: disclaimer, refusals, and emergency helplines."""

from __future__ import annotations

import re

DISCLAIMER = (
    "This is general legal information based on the cited documents, not legal advice. "
    "Laws change and facts matter - consult a qualified advocate for your situation."
)

REFUSAL_MESSAGE = (
    "I can't help with evading the law, concealing or fabricating evidence, or committing an "
    "offence. I can explain what the law says about an act and its consequences if that helps."
)
OUT_OF_SCOPE_MESSAGE = (
    "I can only answer questions about Indian law using the legal documents I have been given, "
    "and I couldn't find anything relevant to that question. Try rephrasing it, or mention the "
    "Act or topic (for example consumer rights, cyber offences, or fundamental rights)."
)
INSUFFICIENT_MESSAGE = (
    "I couldn't find enough reliable support in my legal documents to answer that confidently, "
    "so I'd rather not guess. Please rephrase with more detail, or consult a qualified advocate."
)
SMALL_TALK_MESSAGE = (
    "Hello! I'm SPECTRE, an assistant for questions about Indian law. Ask me about a right, "
    "an offence, or a legal procedure and I'll answer from the cited legal texts."
)
ERROR_MESSAGE = "Something went wrong while preparing your answer. Please try again."

# Verify these numbers against official sources before release; they change occasionally.
_HELPLINE_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(danger|attacked|threat(en|s)? (to )?(my )?life|kill me)\b", re.I),
     "Emergency (police/fire/ambulance): 112"),
    (re.compile(r"\b(domestic violence|dowry|stalk|molest|rape|sexual (assault|harass)|eve.?teas)", re.I),
     "Women Helpline: 181"),
    (re.compile(r"\b(child|minor|pocso|underage)\b", re.I),
     "Childline: 1098"),
    (re.compile(r"\b(cyber ?crime|online fraud|scam|phishing|hacked|upi fraud|sextortion)\b", re.I),
     "National Cyber Crime Helpline: 1930 (cybercrime.gov.in)"),
]

_HARMFUL_RE = re.compile(
    r"how (do|can|to) (i |we )?(get away with|avoid (getting )?caught|evade (arrest|police|the law)|"
    r"hide (the )?(body|evidence)|destroy evidence|forge|fabricate evidence|bribe)|"
    r"help me (forge|fabricate|hide evidence|destroy evidence|cheat the court)",
    re.IGNORECASE,
)


def is_harmful_request(question: str) -> bool:
    return bool(_HARMFUL_RE.search(question))


def helplines_for(question: str) -> list[str]:
    return [text for pattern, text in _HELPLINE_RULES if pattern.search(question)]
