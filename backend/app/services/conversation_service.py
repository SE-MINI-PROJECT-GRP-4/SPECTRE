"""Conversation Orchestration Service managing multi-turn legal dialogues."""

import json
import time
from datetime import datetime, timezone
from typing import List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.repositories.conversations import ConversationRepository
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationResponse,
    FrontendAnswer,
    FrontendQueryRequest,
    FrontendQueryResponse,
    FrontendUserMessage,
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

    def process_frontend_query(
        self,
        payload: FrontendQueryRequest,
        current_user: Optional[User] = None,
    ) -> FrontendQueryResponse:
        """
        Unified frontend query orchestration endpoint (REQ-QUERY-01 through REQ-QUERY-12):
        - Supports authenticated persistent conversations and anonymous inquiries
        - Formats response according to frontend expectations (ResponseView & Chat.jsx)
        """
        cleaned_question = SafetyComplianceService.sanitize_input(payload.text)
        if len(cleaned_question) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question is too short or empty.")

        now_iso = datetime.now(timezone.utc).isoformat()
        user_msg_id = f"m-{int(time.time() * 1000)}"

        # 1. Resolve conversation if user is authenticated
        conversation = None
        if current_user:
            if payload.conversationId:
                conv_id_clean = None
                try:
                    conv_id_clean = int(str(payload.conversationId).replace("c-", "").replace("conv-", ""))
                except ValueError:
                    pass
                if conv_id_clean:
                    existing_conv = self.repo.get_by_id(conv_id_clean)
                    if existing_conv and existing_conv.user_id == current_user.id:
                        conversation = existing_conv
            if not conversation:
                conversation = self.repo.create(
                    user_id=current_user.id,
                    title=cleaned_question[:60],
                    legal_domain="general",
                )

        # 2. Safety refusal check
        is_refusal, refusal_msg = SafetyComplianceService.check_refusal(cleaned_question)
        if is_refusal:
            disclaimer = SafetyComplianceService.enforce_disclaimer()
            if conversation:
                u_m = self.repo.add_message(conversation_id=conversation.id, role="user", content=cleaned_question)
                a_m = self.repo.add_message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=refusal_msg,
                    disclaimer=disclaimer,
                )
                user_msg_id = str(u_m.id)
                ans_id = str(a_m.id)
            else:
                ans_id = f"m-{int(time.time() * 1000) + 1}"

            return FrontendQueryResponse(
                conversationId=conversation.id if conversation else None,
                userMessage=FrontendUserMessage(id=user_msg_id, role="user", text=cleaned_question, createdAt=now_iso),
                answer=FrontendAnswer(
                    id=ans_id,
                    role="assistant",
                    text=refusal_msg,
                    domain="General",
                    confidence="insufficient",
                    procedure=None,
                    sources=[],
                    notes=["Request identified as contrary to safety and compliance policies."],
                    template=None,
                    disclaimer=disclaimer,
                    createdAt=now_iso,
                ),
            )

        # 3. AI Retrieval and Generation
        ai_result = self.ai_client.ask(question=cleaned_question)

        # 4. Moderation & Safety
        moderated_answer, mods = SafetyComplianceService.clean_outcome_guarantees(ai_result.answer)
        mandatory_disclaimer = SafetyComplianceService.enforce_disclaimer(ai_result.disclaimer)
        emergency_helplines = SafetyComplianceService.get_emergency_helplines(cleaned_question)

        combined_helplines = list(dict.fromkeys(ai_result.helplines + emergency_helplines))
        combined_warnings = list(dict.fromkeys(ai_result.warnings + mods))

        # 5. Persist to DB if conversation exists
        if conversation:
            u_m = self.repo.add_message(conversation_id=conversation.id, role="user", content=cleaned_question)
            citations_dict = [c.model_dump() for c in ai_result.citations]
            a_m = self.repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=moderated_answer,
                legal_domain=ai_result.legal_domain.value,
                citations=citations_dict,
                procedural_steps=ai_result.procedural_steps,
                confidence=ai_result.confidence,
                disclaimer=mandatory_disclaimer,
            )
            user_msg_id = str(u_m.id)
            ans_id = str(a_m.id)

            domain_val = ai_result.legal_domain.value
            self.repo.update_title_and_domain(
                conversation=conversation,
                title=conversation.title or cleaned_question[:60],
                legal_domain=domain_val,
            )
        else:
            ans_id = f"m-{int(time.time() * 1000) + 1}"

        # 6. Format Sources
        sources_list = []
        for i, c in enumerate(ai_result.citations):
            title = c.document
            if c.section:
                title = f"{c.document} ({c.section})"
            sources_list.append({
                "id": f"ref-{i+1}",
                "title": title,
                "source": "Statutory Gazette / India Code",
                "domain": ai_result.legal_domain.value.title(),
                "status": "active",
                "link": "https://www.indiacode.nic.in",
            })

        # 7. Procedure
        procedure_obj = None
        if ai_result.procedural_steps:
            procedure_obj = {
                "prerequisites": [
                    "Invoice / transaction records / written communications",
                    "Valid government identity proof",
                    "Chronological record of events and notices exchanged",
                ],
                "steps": ai_result.procedural_steps,
            }

        # 8. Related Template
        template_obj = None
        domain_name = ai_result.legal_domain.value.title()
        if "Consumer" in domain_name:
            template_obj = {"id": 1, "name": "Legal notice for consumer complaint"}
        elif "Cyber" in domain_name:
            template_obj = {"id": 5, "name": "Cyber crime complaint"}
        elif "Constitutional" in domain_name or "Rti" in domain_name:
            template_obj = {"id": 4, "name": "RTI application"}
        elif "Criminal" in domain_name:
            template_obj = {"id": 6, "name": "Formal Police Complaint / Zero FIR"}
        elif "Civil" in domain_name or "Tenancy" in domain_name or "Property" in domain_name:
            template_obj = {"id": 2, "name": "Rental agreement"}
        elif "Labor" in domain_name or "Employment" in domain_name:
            template_obj = {"id": 3, "name": "Unpaid wages demand letter"}

        # 9. Confidence Label
        if ai_result.confidence >= 0.75 and sources_list:
            conf_str = "medium"
        elif ai_result.confidence >= 0.4:
            conf_str = "low"
        else:
            conf_str = "insufficient"

        # 10. Notes
        notes_list = combined_warnings.copy()
        if procedure_obj:
            notes_list.append("Procedures can vary by state, jurisdiction and facts (REQ-PROC-04).")
        for h in combined_helplines:
            notes_list.append(f"Helpline: {h}")

        return FrontendQueryResponse(
            conversationId=conversation.id if conversation else None,
            userMessage=FrontendUserMessage(
                id=user_msg_id,
                role="user",
                text=cleaned_question,
                createdAt=now_iso,
            ),
            answer=FrontendAnswer(
                id=ans_id,
                role="assistant",
                text=moderated_answer,
                domain=domain_name,
                confidence=conf_str,
                procedure=procedure_obj,
                sources=sources_list,
                notes=notes_list,
                template=template_obj,
                disclaimer=mandatory_disclaimer,
                createdAt=now_iso,
            ),
        )
