"""Statistics service."""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.task import Task


class StatsService:

    def get_overview(self, db: Session) -> dict:
        total = db.query(func.count(Task.id)).scalar()
        done = db.query(func.count(Task.id)).filter(Task.status == "done").scalar()
        in_progress = db.query(func.count(Task.id)).filter(Task.status == "in_progress").scalar()
        todo = db.query(func.count(Task.id)).filter(Task.status == "todo").scalar()

        avg_estimated = db.query(func.avg(Task.estimated_minutes)).filter(Task.estimated_minutes.isnot(None)).scalar()
        avg_actual = db.query(func.avg(Task.actual_minutes)).filter(Task.actual_minutes.isnot(None)).scalar()

        return {
            "total": total or 0,
            "done": done or 0,
            "in_progress": in_progress or 0,
            "todo": todo or 0,
            "completion_rate": round((done / total * 100) if total else 0, 1),
            "avg_estimated_minutes": round(avg_estimated, 0) if avg_estimated else 0,
            "avg_actual_minutes": round(avg_actual, 0) if avg_actual else 0,
        }

    def get_weekly_trend(self, db: Session) -> list[dict]:
        today = date.today()
        weeks = []
        for i in range(3, -1, -1):
            week_end = today - timedelta(days=i * 7)
            week_start = week_end - timedelta(days=6)

            done_count = (
                db.query(func.count(Task.id))
                .filter(Task.status == "done")
                .filter(Task.updated_at >= week_start, Task.updated_at <= week_end)
                .scalar()
            )
            weeks.append({
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "completed": done_count or 0,
            })
        return weeks
