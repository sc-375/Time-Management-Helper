"""Reminder model."""
import enum
from sqlalchemy import Column, Integer, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ReminderMethod(str, enum.Enum):
    email = "email"


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    method = Column(Enum(ReminderMethod), default=ReminderMethod.email, nullable=False)
    sent = Column(Boolean, default=False, nullable=False)
    fail_count = Column(Integer, default=0, nullable=False)

    task = relationship("Task", back_populates="reminders")
