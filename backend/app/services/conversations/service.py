from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Conversation, Message
from app.repositories.conversations import (
    add_message,
    create_conversation,
    get_conversation_by_id,
    get_conversation_messages,
    get_user_conversations,
)


def create_user_conversation(
    db: Session,
    user_id: int,
    title: str | None = None,
) -> Conversation:
    """
    Create a conversation belonging to the authenticated user.
    """

    return create_conversation(
        db=db,
        user_id=user_id,
        title=title,
    )


def get_user_conversation(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> Conversation:
    """
    Retrieve a conversation only if it belongs to the user.
    """

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this conversation.",
        )

    return conversation


def list_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    """
    Retrieve only conversations belonging to the authenticated user.
    """

    return get_user_conversations(
        db=db,
        user_id=user_id,
    )


def add_user_message(
    db: Session,
    conversation_id: int,
    user_id: int,
    role: str,
    content: str,
) -> Message:
    """
    Add a message only to a conversation owned by the user.
    """

    get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    return add_message(
        db=db,
        conversation_id=conversation_id,
        role=role,
        content=content,
    )


def get_user_messages(
    db: Session,
    conversation_id: int,
    user_id: int,
) -> list[Message]:
    """
    Retrieve messages only from a conversation owned by the user.
    """

    get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    return get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )