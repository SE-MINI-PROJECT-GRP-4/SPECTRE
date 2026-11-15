import pytest

from app.models import User
from app.models.user import UserRole
from app.services.conversations.service import (
    get_user_conversation,
)


class FakeConversation:
    def __init__(self, conversation_id, user_id):
        self.conversation_id = conversation_id
        self.user_id = user_id


def test_user_can_access_own_conversation(monkeypatch):
    conversation = FakeConversation(
        conversation_id=1,
        user_id=10,
    )

    def fake_get_conversation_by_id(
        db,
        conversation_id,
    ):
        return conversation

    monkeypatch.setattr(
        "app.services.conversations.service.get_conversation_by_id",
        fake_get_conversation_by_id,
    )

    result = get_user_conversation(
        db=None,
        conversation_id=1,
        user_id=10,
    )

    assert result.conversation_id == 1
    assert result.user_id == 10


def test_user_cannot_access_another_users_conversation(monkeypatch):
    conversation = FakeConversation(
        conversation_id=1,
        user_id=10,
    )

    def fake_get_conversation_by_id(
        db,
        conversation_id,
    ):
        return conversation

    monkeypatch.setattr(
        "app.services.conversations.service.get_conversation_by_id",
        fake_get_conversation_by_id,
    )

    with pytest.raises(Exception) as exc_info:
        get_user_conversation(
            db=None,
            conversation_id=1,
            user_id=20,
        )

    assert exc_info.value.status_code == 403


def test_missing_conversation_returns_not_found(monkeypatch):
    def fake_get_conversation_by_id(
        db,
        conversation_id,
    ):
        return None

    monkeypatch.setattr(
        "app.services.conversations.service.get_conversation_by_id",
        fake_get_conversation_by_id,
    )

    with pytest.raises(Exception) as exc_info:
        get_user_conversation(
            db=None,
            conversation_id=999,
            user_id=10,
        )

    assert exc_info.value.status_code == 404