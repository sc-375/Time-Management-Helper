"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base, SessionLocal
from .services.email_service import EmailService
from .config import REMINDER_SCAN_INTERVAL

from .routers import tasks, calendar, ai, email, settings, stats


def scan_reminders():
    """Scheduled job: scan and send due reminders."""
    db = SessionLocal()
    try:
        EmailService().scan_and_send(db)
    finally:
        db.close()


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and start scheduler
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(scan_reminders, "interval", seconds=REMINDER_SCAN_INTERVAL, id="scan_reminders")
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown(wait=False)


app = FastAPI(title="Time Management API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(calendar.router)
app.include_router(ai.router)
app.include_router(email.router)
app.include_router(settings.router)
app.include_router(stats.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
