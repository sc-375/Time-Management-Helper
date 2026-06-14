"""Calendar API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.calendar_service import CalendarService
from ..schemas.common import success

router = APIRouter(prefix="/api/calendar", tags=["calendar"])
calendar_service = CalendarService()


@router.get("")
def get_month(year: int, month: int, db: Session = Depends(get_db)):
    result = calendar_service.get_month(db, year, month)
    return success(data=result)


@router.get("/week")
def get_week(start: str, end: str, db: Session = Depends(get_db)):
    result = calendar_service.get_week(db, start, end)
    return success(data=result)
