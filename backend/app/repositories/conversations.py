"""Conversation and message repository for data persistence."""

import json
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    """Repository managing conversations and message records."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: str, legal_domain: Optional[str] = None) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            legal_domain=legal_domain,
            status="active",
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        return self.db.scalar(select(Conversation).where(Conversation.id == conversation_id))

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> List[tuple[Conversation, int]]:
        """Returns conversations belonging to user along with message counts."""
        subquery = (
            select(Message.conversation_id, func.count(Message.id).label("count"))
            .group_by(Message.conversation_id)
            .subquery()
        )

        query = (
            select(Conversation, func.coalesce(subquery.c.count, 0))
            .outerjoin(subquery, Conversation.id == subquery.c.conversation_id)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.execute(query).all())

    def update_title_and_domain(self, conversation: Conversation, title: str, legal_domain: str) -> Conversation:
        conversation.title = title
        conversation.legal_domain = legal_domain
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete(self, conversation: Conversation) -> None:
        self.db.delete(conversation)
        self.db.commit()

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        legal_domain: Optional[str] = None,
        citations: Optional[List[dict]] = None,
        procedural_steps: Optional[List[str]] = None,
        confidence: Optional[float] = None,
        disclaimer: Optional[str] = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            legal_domain=legal_domain,
            citations_json=json.dumps(citations) if citations else None,
            procedural_steps_json=json.dumps(procedural_steps) if procedural_steps else None,
            confidence=confidence,
            disclaimer=disclaimer,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, conversation_id: int) -> List[Message]:
        return list(
            self.db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
            ).all()
        )
