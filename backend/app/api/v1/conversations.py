from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.conversations.service import (
    add_user_message,
    create_user_conversation,
    get_user_conversation,
    get_user_messages,
    list_user_conversations,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_endpoint(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new conversation for the authenticated user.
    """

    return create_user_conversation(
        db=db,
        user_id=current_user.user_id,
        title=request.title,
    )


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return only conversations belonging to the authenticated user.
    """

    return list_user_conversations(
        db=db,
        user_id=current_user.user_id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a conversation only if it belongs to the authenticated user.
    """

    return get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_message_endpoint(
    conversation_id: int,
    request: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a message to a conversation owned by the authenticated user.
    """

    return add_user_message(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        role=request.role,
        content=request.content,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve messages from a conversation owned by the authenticated user.
    """

    return get_user_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
    )