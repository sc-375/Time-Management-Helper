"""AI chat API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.ai_service import AIService
from ..schemas.ai import ChatRequest, AICreateTaskRequest
from ..schemas.common import success, error

router = APIRouter(prefix="/api/ai", tags=["ai"])
ai_service = AIService()


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply = ai_service.chat(db, request.message)
        task_previews = ai_service.parse_task_from_text(reply)
        return success(data={"reply": reply, "task_previews": task_previews})
    except ValueError as e:
        return error(message=str(e))


@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    messages = ai_service.get_history(db)
    return success(data=[
        {
            "id": m.id,
            "role": m.role.value if hasattr(m.role, "value") else m.role,
            "content": m.content,
            "created_at": str(m.created_at),
        }
        for m in messages
    ])


@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    count = ai_service.clear_history(db)
    return success(message=f"已清除 {count} 条对话记录")


@router.post("/create-task")
def create_task_from_nl(request: AICreateTaskRequest, db: Session = Depends(get_db)):
    try:
        previews = ai_service.create_task_from_nl(db, request.text)
        return success(data=previews)
    except ValueError as e:
        return error(message=str(e))
