from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=255,
    )


class ConversationResponse(BaseModel):
    conversation_id: int
    user_id: int
    title: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str = Field(
        min_length=1,
        max_length=20,
    )
    content: str = Field(
        min_length=1,
    )


class MessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True