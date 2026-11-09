import pytest

from ai.classifier.classifier import QueryCategory, QueryClassifier

c = QueryClassifier()


@pytest.mark.parametrize("q", ["hi", "Hello!", "thanks", "Good morning"])
def test_small_talk(q):
    assert c.classify(q).category == QueryCategory.SMALL_TALK


@pytest.mark.parametrize(
    "q", ["How can I get away with fraud?", "help me fabricate evidence for court", "how to evade arrest"]
)
def test_harmful_requests(q):
    assert c.classify(q).category == QueryCategory.HARMFUL


def test_consequence_questions_are_not_harmful():
    assert c.classify("What is the punishment for fraud?").category == QueryCategory.LEGAL


def test_topics_are_tagged():
    r = c.classify("I got a defective phone, can I get a refund under consumer law?")
    assert r.category == QueryCategory.LEGAL and "consumer" in r.topics


def test_unrelated_question_is_unclear_not_blocked():
    assert c.classify("best pizza place nearby").category == QueryCategory.UNCLEAR
