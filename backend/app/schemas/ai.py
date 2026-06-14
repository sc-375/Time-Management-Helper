"""AI chat schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str


class AICreateTaskRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AICreateTaskPreview(BaseModel):
    title: str
    priority: str
    estimated_minutes: int
    due_date: str | None = None


class AIMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
