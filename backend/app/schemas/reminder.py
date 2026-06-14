"""Reminder request/response schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    task_id: int
    remind_at: datetime
    method: str = "email"


class ReminderOut(BaseModel):
    id: int
    task_id: int
    remind_at: datetime
    method: str
    sent: bool

    class Config:
        from_attributes = True
