"""Calendar query service."""
from datetime import date
from typing import Dict, List
from sqlalchemy.orm import Session
from ..models.task import Task


class CalendarService:

    def get_month(self, db: Session, year: int, month: int) -> Dict[str, List[dict]]:
        """Return a dict mapping date string -> list of task summaries for that month."""
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        tasks = (
            db.query(Task)
            .filter(Task.due_date.isnot(None))
            .filter(Task.due_date >= start, Task.due_date < end)
            .order_by(Task.due_date, Task.priority)
            .all()
        )

        result: Dict[str, List[dict]] = {}
        for t in tasks:
            key = t.due_date.isoformat()
            if key not in result:
                result[key] = []
            result[key].append({
                "id": t.id,
                "title": t.title,
                "priority": str(t.priority) if hasattr(t.priority, "value") else t.priority,
                "status": str(t.status) if hasattr(t.status, "value") else t.status,
                "due_time": str(t.due_time) if t.due_time else None,
            })
        return result

    def get_week(self, db: Session, start_str: str, end_str: str) -> Dict[str, List[dict]]:
        """Return tasks for a given week range."""
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)

        tasks = (
            db.query(Task)
            .filter(Task.due_date.isnot(None))
            .filter(Task.due_date >= start, Task.due_date <= end)
            .order_by(Task.due_date, Task.due_time, Task.priority)
            .all()
        )

        result: Dict[str, List[dict]] = {}
        for t in tasks:
            key = t.due_date.isoformat()
            if key not in result:
                result[key] = []
            result[key].append({
                "id": t.id,
                "title": t.title,
                "priority": str(t.priority) if hasattr(t.priority, "value") else t.priority,
                "status": str(t.status) if hasattr(t.status, "value") else t.status,
                "due_time": str(t.due_time) if t.due_time else None,
                "estimated_minutes": t.estimated_minutes,
            })
        return result
