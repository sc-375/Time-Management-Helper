"""Email and reminder API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.email_config import EmailConfig
from ..models.reminder import Reminder
from ..services.email_service import EmailService
from ..schemas.email_config import EmailConfigUpdate
from ..schemas.reminder import ReminderCreate
from ..schemas.common import success, error
from ..utils.crypto import encrypt

router = APIRouter(prefix="/api", tags=["email"])
email_service = EmailService()


@router.get("/email/config")
def get_config(db: Session = Depends(get_db)):
    config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
    if not config:
        config = EmailConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)

    masked = config.auth_code[:4] + "****" if len(config.auth_code) > 4 else "****"
    return success(data={
        "id": config.id,
        "smtp_host": config.smtp_host,
        "smtp_port": config.smtp_port,
        "sender_email": config.sender_email,
        "auth_code": masked,
        "enabled": config.enabled,
    })


@router.put("/email/config")
def update_config(data: EmailConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
    if not config:
        config = EmailConfig(id=1)
        db.add(config)

    config.smtp_host = data.smtp_host
    config.smtp_port = data.smtp_port
    config.sender_email = data.sender_email
    config.auth_code = encrypt(data.auth_code)
    config.enabled = data.enabled
    db.commit()
    db.refresh(config)
    return success(message="邮件配置已更新")


@router.post("/email/test")
def test_email(db: Session = Depends(get_db)):
    ok, msg = email_service.send_test(db)
    if ok:
        return success(message=msg)
    return error(message=msg)


@router.get("/reminders")
def list_reminders(task_id: int, db: Session = Depends(get_db)):
    reminders = db.query(Reminder).filter(Reminder.task_id == task_id).all()
    return success(data=[
        {"id": r.id, "task_id": r.task_id, "remind_at": str(r.remind_at),
         "method": str(r.method) if hasattr(r.method, "value") else r.method,
         "sent": r.sent}
        for r in reminders
    ])


@router.post("/reminders")
def create_reminder(data: ReminderCreate, db: Session = Depends(get_db)):
    reminder = Reminder(task_id=data.task_id, remind_at=data.remind_at, method=data.method)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return success(data={"id": reminder.id}, message="提醒已创建")


@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="提醒未找到")
    db.delete(r)
    db.commit()
    return success(message="提醒已删除")
