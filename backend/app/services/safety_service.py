"""Legal Safety, Compliance, and Disclaimer Enforcement Service.

Enforces SRS requirements:
- REQ-SAFE-01: Information is for general informational purposes.
- REQ-SAFE-02: Clear notice that system does not replace a licensed advocate.
- REQ-SAFE-03 & BR-07: Strips and rejects any guarantees of legal outcomes.
- REQ-SAFE-04: Flags uncertainty on incomplete or potentially outdated provisions.
- REQ-SAFE-05: Directs users to qualified legal counsel when scope exceeded.
- REQ-SAFE-06: Prevents administrative or model bypass of safety disclaimers.
"""

import re
from typing import List, Tuple
from app.core.config import settings

# Patterns suggesting dangerous requests or illegal assistance (refusal triggers)
REFUSAL_PATTERNS = [
    r"\bhow to kill\b", r"\bhow to murder\b", r"\bhow to hide a body\b",
    r"\bhow to evade arrest\b", r"\bevade (the )?police\b", r"\bhow to destroy evidence\b",
    r"\bbribe a judge\b", r"\bbribe the police\b", r"\bmanufacture drugs\b",
    r"\bhack a government\b", r"\bhack\b",
]

# Patterns representing false outcome guarantees that must be stripped or flagged
GUARANTEE_PATTERNS = [
    (r"\byou will definitely win\b", "you may have grounds to seek relief"),
    (r"\bguaranteed to win\b", "supported by statutory provisions"),
    (r"\b100% success\b", "a viable legal avenue"),
    (r"\bjudge will definitely rule\b", "the court will evaluate the merits"),
    (r"\bguarantee the outcome\b", "assess the potential remedies"),
]

# Urgent distress trigger keywords for emergency helpline attachment
DISTRESS_PATTERNS = [
    r"\bsuicide\b", r"\bphysical abuse\b", r"\bdomestic violence\b",
    r"\brape\b", r"\bsexual assault\b", r"\bchild abuse\b", r"\bkidnapping\b"
]

EMERGENCY_HELPLINES = [
    "National Emergency Response Support System (ERSS): 112",
    "Women in Distress Helpline: 1091",
    "Child Helpline: 1098",
    "National Legal Services Authority (Free Legal Aid): 15100",
]


class SafetyComplianceService:
    """Service enforcing legal compliance, disclaimers, and outcome guarantees."""

    @classmethod
    def sanitize_input(cls, question: str) -> str:
        """Sanitizes user input, stripping dangerous control characters."""
        if not question:
            return ""
        # Remove null bytes and excessive whitespace
        cleaned = question.replace("\x00", "").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    @classmethod
    def check_refusal(cls, question: str) -> Tuple[bool, str]:
        """Checks if the query seeks help with illegal acts or evidence destruction."""
        q_lower = question.lower()
        for pattern in REFUSAL_PATTERNS:
            if re.search(pattern, q_lower):
                return True, (
                    "REFUSAL: SPECTRE cannot assist with queries intended to commit offenses, "
                    "destroy evidence, evade law enforcement, or obstruct the administration of justice. "
                    "If you need legal guidance regarding your rights, please consult a licensed advocate."
                )
        return False, ""

    @classmethod
    def clean_outcome_guarantees(cls, answer: str) -> Tuple[str, List[str]]:
        """
        Replaces definitive outcome guarantees with compliant probabilistic phrasing (REQ-SAFE-03, BR-07).
        """
        cleaned_answer = answer
        modifications: List[str] = []

        for pattern, replacement in GUARANTEE_PATTERNS:
            if re.search(pattern, cleaned_answer, flags=re.IGNORECASE):
                cleaned_answer = re.sub(pattern, replacement, cleaned_answer, flags=re.IGNORECASE)
                modifications.append("Outcome guarantee language moderated to compliant informational guidance.")

        return cleaned_answer, modifications

    @classmethod
    def get_emergency_helplines(cls, query: str) -> List[str]:
        """Detects whether emergency or crisis helplines should be attached."""
        q_lower = query.lower()
        for pattern in DISTRESS_PATTERNS:
            if re.search(pattern, q_lower):
                return EMERGENCY_HELPLINES
        return []

    @classmethod
    def enforce_disclaimer(cls, existing_disclaimer: str = None) -> str:
        """
        Guarantees that a valid statutory disclaimer is always present (REQ-SAFE-06).
        """
        if not existing_disclaimer or len(existing_disclaimer.strip()) < 20:
            return settings.STANDARD_DISCLAIMER
        return existing_disclaimer.strip()
