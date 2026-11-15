"""Conversation Orchestration Service managing multi-turn legal dialogues."""

import json
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversations import ConversationRepository
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
    QuerySubmitRequest,
)
from app.schemas.query import CitationSchema, QueryResultDTO
from app.services.ai_client import AIServiceClient
from app.services.safety_service import SafetyComplianceService


class ConversationService:
    """Core backend orchestration service integrating DB, AI client, and safety layer."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ConversationRepository(db)
        self.ai_client = AIServiceClient()

    def _to_message_dto(self, message: Message) -> MessageResponse:
        citations_data = []
        if message.citations_json:
            try:
                raw_list = json.loads(message.citations_json)
                citations_data = [CitationSchema(**c) for c in raw_list]
            except Exception:
                citations_data = []

        steps_data = []
        if message.procedural_steps_json:
            try:
                steps_data = json.loads(message.procedural_steps_json)
            except Exception:
                steps_data = []

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            legal_domain=message.legal_domain,
            citations=citations_data,
            procedural_steps=steps_data,
            confidence=message.confidence,
            disclaimer=message.disclaimer,
            created_at=message.created_at,
        )

    def create_conversation(self, user_id: int, title: str = None, legal_domain: str = None) -> ConversationResponse:
        title = title.strip() if title else "New Legal Query"
        conversation = self.repo.create(user_id=user_id, title=title, legal_domain=legal_domain)
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            legal_domain=conversation.legal_domain,
            status=conversation.status,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
        )

    def list_conversations(self, user_id: int, skip: int = 0, limit: int = 50) -> List[ConversationResponse]:
        """Lists user's conversations, strictly isolated to the authenticated user (REQ-HIST-02, REQ-HIST-04)."""
        rows = self.repo.list_by_user(user_id=user_id, skip=skip, limit=limit)
        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                legal_domain=conv.legal_domain,
                status=conv.status,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=count,
            )
            for conv, count in rows
        ]

    def get_conversation_detail(self, conversation_id: int, user_id: int) -> ConversationDetailResponse:
        """Retrieves conversation and messages, enforcing user access security (REQ-HIST-04)."""
        conversation = self.repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this conversation.",
            )

        messages = self.repo.get_messages(conversation_id)
        dtos = [self._to_message_dto(m) for m in messages]

        return ConversationDetailResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            legal_domain=conversation.legal_domain,
            status=conversation.status,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(dtos),
            messages=dtos,
        )

    def delete_conversation(self, conversation_id: int, user_id: int) -> None:
        """Deletes a conversation owned by the authenticated user (REQ-HIST-05)."""
        conversation = self.repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
        if conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        self.repo.delete(conversation)

    def process_query(self, conversation_id: int, user_id: int, payload: QuerySubmitRequest) -> QueryResultDTO:
        """
        Executes complete multi-turn query orchestration:
        1. Validates ownership and input.
        2. Checks safety refusal triggers.
        3. Persists user query message.
        4. Invokes AI client adapter.
        5. Moderates outcome guarantees and enforces disclaimer.
        6. Persists assistant response and citations.
        7. Updates conversation title and domain if initial query.
        """
        conversation = self.repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
        if conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        cleaned_question = SafetyComplianceService.sanitize_input(payload.question)
        if len(cleaned_question) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question is too short or empty.")

        # Check refusal triggers (solicitation of crime, evidence tampering)
        is_refusal, refusal_msg = SafetyComplianceService.check_refusal(cleaned_question)
        if is_refusal:
            # Persist user question
            self.repo.add_message(conversation_id=conversation_id, role="user", content=cleaned_question)
            # Persist refusal message
            self.repo.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=refusal_msg,
                disclaimer=SafetyComplianceService.enforce_disclaimer(),
            )
            return QueryResultDTO(
                status="refused",
                legal_domain=conversation.legal_domain or "general",
                answer=refusal_msg,
                procedural_steps=[],
                citations=[],
                confidence=0.0,
                confidence_label="none",
                disclaimer=SafetyComplianceService.enforce_disclaimer(),
                warnings=["Query was identified as outside acceptable legal assistance guidelines."],
                helplines=[],
            )

        # 1. Save user query message
        self.repo.add_message(conversation_id=conversation_id, role="user", content=cleaned_question)

        # 2. Call AI module adapter
        ai_result = self.ai_client.ask(question=cleaned_question, top_k=payload.top_k)

        # 3. Post-process response through Safety Compliance layer
        moderated_answer, mods = SafetyComplianceService.clean_outcome_guarantees(ai_result.answer)
        mandatory_disclaimer = SafetyComplianceService.enforce_disclaimer(ai_result.disclaimer)
        emergency_helplines = SafetyComplianceService.get_emergency_helplines(cleaned_question)

        combined_helplines = list(dict.fromkeys(ai_result.helplines + emergency_helplines))
        combined_warnings = list(dict.fromkeys(ai_result.warnings + mods))

        citations_dict_list = [c.model_dump() for c in ai_result.citations]

        # 4. Save assistant response message
        self.repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=moderated_answer,
            legal_domain=ai_result.legal_domain.value,
            citations=citations_dict_list,
            procedural_steps=ai_result.procedural_steps,
            confidence=ai_result.confidence,
            disclaimer=mandatory_disclaimer,
        )

        # 5. Update conversation metadata if title is default
        if conversation.title == "New Legal Query":
            auto_title = cleaned_question[:60] + ("..." if len(cleaned_question) > 60 else "")
            self.repo.update_title_and_domain(
                conversation=conversation,
                title=auto_title,
                legal_domain=ai_result.legal_domain.value,
            )

        return QueryResultDTO(
            status=ai_result.status,
            legal_domain=ai_result.legal_domain,
            answer=moderated_answer,
            procedural_steps=ai_result.procedural_steps,
            citations=ai_result.citations,
            confidence=ai_result.confidence,
            confidence_label=ai_result.confidence_label,
            disclaimer=mandatory_disclaimer,
            warnings=combined_warnings,
            helplines=combined_helplines,
        )
