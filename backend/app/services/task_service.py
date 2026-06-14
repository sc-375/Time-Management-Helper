"""Task business logic."""
from datetime import date as date_type, datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def list_tasks(
        self,
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Task]:
        q = db.query(Task).options(joinedload(Task.subtasks))
        if status:
            q = q.filter(Task.status == status)
        if priority:
            q = q.filter(Task.priority == priority)
        if due_before:
            q = q.filter(Task.due_date <= date_type.fromisoformat(due_before))
        if due_after:
            q = q.filter(Task.due_date >= date_type.fromisoformat(due_after))
        if search:
            q = q.filter(Task.title.ilike(f"%{search}%"))
        if tag:
            q = q.filter(Task.tags.contains(tag))
        return q.order_by(Task.created_at.desc()).all()

    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        return (
            db.query(Task)
            .options(joinedload(Task.subtasks), joinedload(Task.reminders))
            .filter(Task.id == task_id)
            .first()
        )

    def create(self, db: Session, data: TaskCreate) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=data.status,
            due_date=data.due_date,
            due_time=data.due_time,
            estimated_minutes=data.estimated_minutes,
            parent_id=data.parent_id,
            tags=data.tags,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update(self, db: Session, task_id: int, data: TaskUpdate) -> Optional[Task]:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    def update_status(self, db: Session, task_id: int, new_status: str) -> Optional[Task]:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        task.status = new_status
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task_id: int) -> bool:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True
