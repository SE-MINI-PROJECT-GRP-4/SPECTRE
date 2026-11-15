from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message


def get_conversation_by_id(
    db: Session,
    conversation_id: int,
) -> Conversation | None:
    """
    Retrieve a conversation by ID.
    """

    return db.scalar(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id
        )
    )


def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:
    """
    Retrieve all conversations belonging to a user.
    """

    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
    )


def create_conversation(
    db: Session,
    user_id: int,
    title: str | None = None,
) -> Conversation:
    """
    Create a new conversation for a user.
    """

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    """
    Add a message to a conversation.
    """

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:
    """
    Retrieve all messages belonging to a conversation.
    """

    return list(
        db.scalars(
            select(Message)
            .where(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.created_at.asc())
        )
    )