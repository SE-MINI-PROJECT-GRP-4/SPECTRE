"""Legal Domain and Query Intent Classifier for Indian Legal System."""

import re
from typing import Tuple
from app.schemas.query import LegalDomainEnum


DOMAIN_KEYWORDS = {
    LegalDomainEnum.CONSUMER: [
        r"\bconsumer\b", r"\bdefective\b", r"\bwarranty\b", r"\bguarantee\b",
        r"\brefund\b", r"\breplacement\b", r"\be-commerce\b", r"\bunfair trade\b",
        r"\bdeficiency in service\b", r"\bdcdrc\b", r"\bncdrc\b", r"\be-daakhil\b",
        r"\bproduct liability\b", r"\bcpa\b", r"\bconsumer court\b", r"\bflipkart\b", r"\bamazon\b"
    ],
    LegalDomainEnum.CRIMINAL: [
        r"\bfir\b", r"\bpolice\b", r"\barrest\b", r"\bbail\b", r"\bcognizable\b",
        r"\bnon-cognizable\b", r"\btheft\b", r"\bassault\b", r"\bmurder\b",
        r"\bbns\b", r"\bbnss\b", r"\bipc\b", r"\bcrpc\b", r"\bpocso\b",
        r"\bextortion\b", r"\bkidnapping\b", r"\bhomicide\b", r"\bzero fir\b",
        r"\bmagistrate\b", r"\bcharge sheet\b", r"\bsection 173\b"
    ],
    LegalDomainEnum.CYBER: [
        r"\bcyber\b", r"\bhacking\b", r"\bhacked\b", r"\bphishing\b", r"\botp fraud\b",
        r"\bonline fraud\b", r"\bidentity theft\b", r"\bit act\b", r"\bcybercrime\b",
        r"\bdeepfake\b", r"\bdata breach\b", r"\bcyber cell\b", r"\b1930\b"
    ],
    LegalDomainEnum.CONSTITUTIONAL: [
        r"\brti\b", r"\bright to information\b", r"\bfundamental right\b", r"\bwrit\b",
        r"\bhabeas corpus\b", r"\bmandamus\b", r"\barticle 21\b", r"\barticle 19\b",
        r"\barticle 32\b", r"\barticle 226\b", r"\bpublic information officer\b", r"\bpio\b",
        r"\bhigh court\b", r"\bsupreme court\b", r"\bconstitution\b"
    ],
    LegalDomainEnum.CIVIL: [
        r"\bproperty\b", r"\btenant\b", r"\blandlord\b", r"\beviction\b", r"\brent\b",
        r"\bcontract\b", r"\bbreach of contract\b", r"\bsuit\b", r"\binjunction\b",
        r"\bcheque bounce\b", r"\bsection 138\b", r"\bnegotiable instruments\b",
        r"\bmoney recovery\b", r"\bspecific relief\b", r"\bagreement\b"
    ],
    LegalDomainEnum.FAMILY: [
        r"\bdivorce\b", r"\bmaintenance\b", r"\balimony\b", r"\bcustody\b",
        r"\bdomestic violence\b", r"\bdowry\b", r"\bhindu marriage act\b",
        r"\bspecial marriage act\b", r"\bguardianship\b", r"\bsuccession\b", r"\bwill\b"
    ],
    LegalDomainEnum.LABOR: [
        r"\btermination\b", r"\bsalary unpaid\b", r"\bprovident fund\b", r"\bepf\b",
        r"\bgratuity\b", r"\bworkplace\b", r"\blabour court\b", r"\bposh\b",
        r"\bsexual harassment at workplace\b", r"\bindustrial dispute\b"
    ],
}


class LegalDomainClassifier:
    """Classifies natural language user queries into legal domains (REQ-QUERY-03)."""

    @classmethod
    def classify(cls, query: str) -> Tuple[LegalDomainEnum, float]:
        """Returns the most probable legal domain along with a confidence heuristic."""
        text = query.lower()
        domain_scores = {domain: 0 for domain in LegalDomainEnum}

        for domain, patterns in DOMAIN_KEYWORDS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                domain_scores[domain] += len(matches) * 2

        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]

        if max_score == 0:
            return LegalDomainEnum.GENERAL, 0.50

        # Normalized confidence heuristic
        confidence = min(0.95, 0.65 + (max_score * 0.05))
        return best_domain, round(confidence, 2)
