"""Statistics API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.stats_service import StatsService
from ..schemas.common import success

router = APIRouter(prefix="/api/stats", tags=["stats"])
stats_service = StatsService()


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    result = stats_service.get_overview(db)
    return success(data=result)


@router.get("/weekly")
def get_weekly(db: Session = Depends(get_db)):
    result = stats_service.get_weekly_trend(db)
    return success(data=result)
