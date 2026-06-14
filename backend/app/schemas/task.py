"""Task request/response schemas."""
from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = None
    tags: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    actual_minutes: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = None
    tags: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$")


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    due_time: Optional[time]
    estimated_minutes: Optional[int]
    actual_minutes: Optional[int]
    parent_id: Optional[int]
    tags: str
    created_at: datetime
    updated_at: datetime
    subtasks: List["TaskOut"] = []

    class Config:
        from_attributes = True


class TaskDetail(TaskOut):
    reminders: List["ReminderOut"] = []


from .reminder import ReminderOut
TaskOut.model_rebuild()
TaskDetail.model_rebuild()
