"""Task CRUD API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.task_service import TaskService
from ..schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate
from ..schemas.common import success

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
task_service = TaskService()


@router.get("")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    tasks = task_service.list_tasks(db, status=status, priority=priority, tag=tag, search=search)
    return success(data=[_task_to_out(t) for t in tasks])


@router.post("")
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = task_service.create(db, data)
    return success(data=_task_to_out(task), message="任务创建成功")


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return success(data=_task_to_detail(task))


@router.put("/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = task_service.update(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return success(data=_task_to_out(task), message="任务更新成功")


@router.patch("/{task_id}/status")
def patch_status(task_id: int, data: TaskStatusUpdate, db: Session = Depends(get_db)):
    task = task_service.update_status(db, task_id, data.status)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return success(data=_task_to_out(task), message="状态更新成功")


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    ok = task_service.delete(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="任务未找到")
    return success(message="任务已删除")


def _task_to_out(t) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "priority": t.priority.value if hasattr(t.priority, "value") else t.priority,
        "status": t.status.value if hasattr(t.status, "value") else t.status,
        "due_date": str(t.due_date) if t.due_date else None,
        "due_time": str(t.due_time) if t.due_time else None,
        "estimated_minutes": t.estimated_minutes,
        "actual_minutes": t.actual_minutes,
        "parent_id": t.parent_id,
        "tags": t.tags,
        "created_at": str(t.created_at),
        "updated_at": str(t.updated_at),
        "subtasks": [_task_to_out(s) for s in (t.subtasks or [])],
    }


def _task_to_detail(t) -> dict:
    d = _task_to_out(t)
    d["reminders"] = [
        {
            "id": r.id,
            "task_id": r.task_id,
            "remind_at": str(r.remind_at),
            "method": r.method.value if hasattr(r.method, "value") else r.method,
            "sent": r.sent,
        }
        for r in (t.reminders or [])
    ]
    return d
