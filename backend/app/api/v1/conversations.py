"""Conversation and Query Orchestration API v1 Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
    QuerySubmitRequest,
)
from app.schemas.query import QueryResultDTO
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations & Legal Queries"])


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation thread",
    description="Initiates a new conversation thread for legal inquiries.",
)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    service = ConversationService(db)
    return service.create_conversation(
        user_id=current_user.id,
        title=payload.title,
        legal_domain=payload.legal_domain.value if payload.legal_domain else None,
    )


@router.get(
    "",
    response_model=List[ConversationResponse],
    status_code=status.HTTP_200_OK,
    summary="List user conversations",
    description="Retrieves a list of previous conversations for the authenticated user with timestamps (REQ-HIST-01, REQ-HIST-03).",
)
def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ConversationResponse]:
    service = ConversationService(db)
    return service.list_conversations(user_id=current_user.id, skip=skip, limit=limit)


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation detail and history",
    description="Retrieves full chronological message history with citations, enforcing strict user access authorization (REQ-HIST-04).",
)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationDetailResponse:
    service = ConversationService(db)
    return service.get_conversation_detail(conversation_id=conversation_id, user_id=current_user.id)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete conversation",
    description="Deletes a conversation record gracefully (REQ-HIST-05).",
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    service.delete_conversation(conversation_id=conversation_id, user_id=current_user.id)
    return {"status": "success", "message": "Conversation successfully deleted."}


@router.post(
    "/{conversation_id}/query",
    response_model=QueryResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Submit query to legal AI assistant",
    description="Core backend orchestration endpoint. Validates query, integrates AI engine, attaches verified citations, checks safety constraints, and persists conversation context (REQ-QUERY-01 through REQ-QUERY-12).",
)
def submit_query(
    conversation_id: int,
    payload: QuerySubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResultDTO:
    service = ConversationService(db)
    return service.process_query(
        conversation_id=conversation_id,
        user_id=current_user.id,
        payload=payload,
    )
