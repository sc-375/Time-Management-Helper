# Time Management Platform — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP of a local time management platform with task CRUD, Kanban board, calendar views (month/week), AI assistant (Ollama + third-party API), and QQ email reminders.

**Architecture:** FastAPI backend (Router → Service → SQLAlchemy) on port 8000; Vue 3 + Element Plus frontend on port 5173 with Vite proxy to backend. SQLite database. APScheduler for reminder scanning. Adapter pattern for dual LLM providers.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, APScheduler, smtplib, Vue 3, Element Plus, Vite, Pinia, Axios, SQLite

---

### Task 1: Backend project scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`

- [ ] **Step 1: Create `backend/requirements.txt`**

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
apscheduler==3.10.4
pydantic==2.10.3
pydantic-settings==2.7.0
python-dotenv==1.0.1
httpx==0.28.1
cryptography==44.0.0
```

- [ ] **Step 2: Create `backend/.env.example`**

```env
DATABASE_URL=sqlite:///./data/time_management.db
SECRET_KEY=change-me-to-a-random-string-at-least-32-chars
REMINDER_SCAN_INTERVAL=60
```

- [ ] **Step 3: Create `backend/app/__init__.py`**

```python
# backend/app/__init__.py
```

- [ ] **Step 4: Create `backend/app/config.py`**

```python
"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/time_management.db")
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-string")
REMINDER_SCAN_INTERVAL: int = int(os.getenv("REMINDER_SCAN_INTERVAL", "60"))

# Ensure data directory exists for SQLite
(BASE_DIR / "data").mkdir(exist_ok=True)
```

- [ ] **Step 5: Create `backend/app/database.py`**

```python
"""SQLAlchemy engine and session factory."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 6: Install dependencies and verify**

```bash
cd backend && pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/.env.example backend/app/
git commit -m "feat: backend project scaffolding with config and database"
```

---

### Task 2: Database models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/task.py`
- Create: `backend/app/models/reminder.py`
- Create: `backend/app/models/email_config.py`
- Create: `backend/app/models/llm_config.py`
- Create: `backend/app/models/ai_message.py`

- [ ] **Step 1: Create `backend/app/models/__init__.py`**

```python
from backend.app.models.task import Task
from backend.app.models.reminder import Reminder
from backend.app.models.email_config import EmailConfig
from backend.app.models.llm_config import LLMConfig
from backend.app.models.ai_message import AIChatMessage

__all__ = ["Task", "Reminder", "EmailConfig", "LLMConfig", "AIChatMessage"]
```

- [ ] **Step 2: Create `backend/app/models/task.py`**

```python
"""Task model."""
import enum
from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Text, Enum, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class PriorityEnum(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class StatusEnum(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.todo, nullable=False)
    due_date = Column(Date, nullable=True)
    due_time = Column(Time, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    tags = Column(String(500), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parent = relationship("Task", remote_side=[id], backref="subtasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
```

- [ ] **Step 3: Create `backend/app/models/reminder.py`**

```python
"""Reminder model."""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


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
```

- [ ] **Step 4: Create `backend/app/models/email_config.py`**

```python
"""Email configuration model (single-row table)."""
from sqlalchemy import Column, Integer, String, Boolean
from backend.app.database import Base


class EmailConfig(Base):
    __tablename__ = "email_config"

    id = Column(Integer, primary_key=True, default=1)
    smtp_host = Column(String(200), default="smtp.qq.com", nullable=False)
    smtp_port = Column(Integer, default=465, nullable=False)
    sender_email = Column(String(200), default="", nullable=False)
    auth_code = Column(String(500), default="", nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
```

- [ ] **Step 5: Create `backend/app/models/llm_config.py`**

```python
"""LLM configuration model (single-row table)."""
import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean
from backend.app.database import Base


class LLMProvider(str, enum.Enum):
    ollama = "ollama"
    openai = "openai"
    custom = "custom"


class LLMConfig(Base):
    __tablename__ = "llm_config"

    id = Column(Integer, primary_key=True, default=1)
    provider = Column(Enum(LLMProvider), default=LLMProvider.ollama, nullable=False)
    base_url = Column(String(500), default="http://localhost:11434", nullable=False)
    api_key = Column(String(500), default="", nullable=True)
    model = Column(String(200), default="deepseek-r1:7b", nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
```

- [ ] **Step 6: Create `backend/app/models/ai_message.py`**

```python
"""AI chat message model."""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from backend.app.database import Base


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 7: Write and run a quick create-all test**

```bash
cd backend && python -c "
from backend.app.database import engine, Base
from backend.app.models import Task, Reminder, EmailConfig, LLMConfig, AIChatMessage
Base.metadata.create_all(bind=engine)
print('Tables created successfully')
"
```

Expected: `Tables created successfully`

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add database models (Task, Reminder, EmailConfig, LLMConfig, AIChatMessage)"
```

---

### Task 3: Crypto utility and Pydantic schemas

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/crypto.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/schemas/task.py`
- Create: `backend/app/schemas/reminder.py`
- Create: `backend/app/schemas/email_config.py`
- Create: `backend/app/schemas/llm_config.py`
- Create: `backend/app/schemas/ai.py`

- [ ] **Step 1: Create `backend/app/utils/__init__.py`**

```python
# backend/app/utils/__init__.py
```

- [ ] **Step 2: Write the failing crypto test**

Create `backend/tests/__init__.py` (empty) and `backend/tests/test_crypto.py`:

```python
"""Tests for crypto utility."""
import os
from backend.app.utils.crypto import encrypt, decrypt


def test_encrypt_decrypt_roundtrip():
    os.environ["SECRET_KEY"] = "test-key-32-chars-long!!!!!!"
    plain = "my_auth_code_123"
    cipher = encrypt(plain)
    assert cipher != plain
    assert decrypt(cipher) == plain


def test_decrypt_detects_tampering():
    os.environ["SECRET_KEY"] = "test-key-32-chars-long!!!!!!"
    cipher = encrypt("original")
    result = decrypt(cipher + "tampered")
    assert result is None
```

Run: `cd backend && python -m pytest tests/test_crypto.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create `backend/app/utils/crypto.py`**

```python
"""AES-256-GCM encryption for sensitive config values."""
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from backend.app.config import SECRET_KEY


def _get_key() -> bytes:
    """Derive a 32-byte key from SECRET_KEY."""
    key = SECRET_KEY.encode("utf-8")
    if len(key) < 32:
        key = key.ljust(32, b"\x00")
    return key[:32]


def encrypt(plain_text: str) -> str:
    """Encrypt a string with AES-256-GCM. Returns base64-encoded ciphertext+nonce."""
    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(12)
    cipher_bytes = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    # Prepend nonce to ciphertext for storage
    combined = nonce + cipher_bytes
    return base64.b64encode(combined).decode("utf-8")


def decrypt(cipher_text: str) -> str | None:
    """Decrypt a base64-encoded ciphertext+nonce. Returns None if tampered."""
    try:
        aesgcm = AESGCM(_get_key())
        combined = base64.b64decode(cipher_text.encode("utf-8"))
        nonce, cipher_bytes = combined[:12], combined[12:]
        return aesgcm.decrypt(nonce, cipher_bytes, None).decode("utf-8")
    except Exception:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && python -m pytest tests/test_crypto.py -v
```

Expected: 2 PASSED

- [ ] **Step 5: Create `backend/app/schemas/__init__.py`**

```python
# backend/app/schemas/__init__.py
```

- [ ] **Step 6: Create `backend/app/schemas/common.py`**

```python
"""Common response schema."""
from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int = 0
    data: Any = None
    message: str = "ok"


def success(data: Any = None, message: str = "ok") -> APIResponse:
    return APIResponse(code=0, data=data, message=message)


def error(message: str, code: int = 1) -> APIResponse:
    return APIResponse(code=code, data=None, message=message)
```

- [ ] **Step 7: Create `backend/app/schemas/task.py`**

```python
"""Task request/response schemas."""
from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = "medium"  # high, medium, low
    status: str = "todo"       # todo, in_progress, done
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = None
    tags: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    actual_minutes: Optional[int] = Field(None, ge=0)
    parent_id: Optional[int] = None
    tags: Optional[str] = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$")


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    due_date: Optional[date]
    due_time: Optional[time]
    estimated_minutes: Optional[int]
    actual_minutes: Optional[int]
    parent_id: Optional[int]
    tags: str
    created_at: datetime
    updated_at: datetime
    subtasks: List["TaskOut"] = []

    class Config:
        from_attributes = True


class TaskDetail(TaskOut):
    reminders: List["ReminderOut"] = []


from backend.app.schemas.reminder import ReminderOut  # noqa: E402
TaskOut.model_rebuild()
TaskDetail.model_rebuild()
```

- [ ] **Step 8: Create `backend/app/schemas/reminder.py`**

```python
"""Reminder request/response schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    task_id: int
    remind_at: datetime
    method: str = "email"


class ReminderOut(BaseModel):
    id: int
    task_id: int
    remind_at: datetime
    method: str
    sent: bool

    class Config:
        from_attributes = True
```

- [ ] **Step 9: Create `backend/app/schemas/email_config.py`**

```python
"""Email config schemas."""
from pydantic import BaseModel, Field


class EmailConfigUpdate(BaseModel):
    smtp_host: str = Field(..., min_length=1)
    smtp_port: int = Field(..., ge=1, le=65535)
    sender_email: str = Field(..., min_length=1)
    auth_code: str = Field(..., min_length=1)
    enabled: bool = False


class EmailConfigOut(BaseModel):
    id: int
    smtp_host: str
    smtp_port: int
    sender_email: str
    auth_code: str  # Will be masked in router
    enabled: bool

    class Config:
        from_attributes = True
```

- [ ] **Step 10: Create `backend/app/schemas/llm_config.py`**

```python
"""LLM config schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class LLMConfigUpdate(BaseModel):
    provider: str = Field(..., pattern="^(ollama|openai|custom)$")
    base_url: str = Field(..., min_length=1)
    api_key: Optional[str] = None
    model: str = Field(..., min_length=1)
    enabled: bool = False


class LLMConfigOut(BaseModel):
    id: int
    provider: str
    base_url: str
    api_key: Optional[str]  # Will be masked in router
    model: str
    enabled: bool

    class Config:
        from_attributes = True
```

- [ ] **Step 11: Create `backend/app/schemas/ai.py`**

```python
"""AI chat schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    reply: str


class AICreateTaskRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AICreateTaskPreview(BaseModel):
    title: str
    priority: str
    estimated_minutes: int
    due_date: str | None = None


class AIMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 12: Commit**

```bash
git add backend/app/utils/ backend/app/schemas/ backend/tests/
git commit -m "feat: add crypto utility, Pydantic schemas, and crypto tests"
```

---

### Task 4: Task Service (CRUD business logic)

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/task_service.py`

- [ ] **Step 1: Create `backend/app/services/__init__.py`**

```python
# backend/app/services/__init__.py
```

- [ ] **Step 2: Write the failing task service tests**

Create `backend/tests/test_task_service.py`:

```python
"""Tests for TaskService."""
from datetime import date
from backend.app.services.task_service import TaskService
from backend.app.schemas.task import TaskCreate


class FakeDB:
    """In-memory list-based fake for testing service logic in isolation."""
    def __init__(self):
        self.tasks = {}
        self.reminders = {}
        self._next_id = 1

    def add(self, obj):
        obj.id = self._next_id
        self.tasks[obj.id] = obj
        self._next_id += 1
        return obj

    def query(self, model):
        return FakeQuery(self)


class FakeQuery:
    def __init__(self, fake_db):
        self.db = fake_db
        self._filters = []

    def filter(self, *args):
        return self

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return list(self.db.tasks.values())

    def get(self, id):
        return self.db.tasks.get(id)


def test_create_task_sets_defaults():
    db = FakeDB()
    svc = TaskService()
    data = TaskCreate(title="Test task")
    task = svc.create(db, data)
    assert task.title == "Test task"
    assert task.priority == "medium"
    assert task.status == "todo"


def test_list_tasks_returns_all():
    db = FakeDB()
    svc = TaskService()
    svc.create(db, TaskCreate(title="Task 1"))
    svc.create(db, TaskCreate(title="Task 2"))
    tasks = svc.list_tasks(db)
    assert len(tasks) == 2
```

Run: `cd backend && python -m pytest tests/test_task_service.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create `backend/app/services/task_service.py`**

```python
"""Task business logic."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.models.task import Task, PriorityEnum, StatusEnum
from backend.app.schemas.task import TaskCreate, TaskUpdate


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
```

- [ ] **Step 4: Run tests to verify logic**

```bash
cd backend && python -m pytest tests/test_task_service.py -v
```

Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/task_service.py backend/app/services/__init__.py backend/tests/test_task_service.py
git commit -m "feat: add TaskService with CRUD operations and tests"
```

---

### Task 5: Calendar Service + Email Service + Stats Service

**Files:**
- Create: `backend/app/services/calendar_service.py`
- Create: `backend/app/services/email_service.py`
- Create: `backend/app/services/stats_service.py`

- [ ] **Step 1: Create `backend/app/services/calendar_service.py`**

```python
"""Calendar query service."""
from datetime import date, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.task import Task


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
                "priority": t.priority,
                "status": t.status,
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
                "priority": t.priority,
                "status": t.status,
                "due_time": str(t.due_time) if t.due_time else None,
                "estimated_minutes": t.estimated_minutes,
            })
        return result
```

- [ ] **Step 2: Create `backend/app/services/email_service.py`**

```python
"""Email service for sending reminders via SMTP."""
import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.email_config import EmailConfig
from backend.app.models.reminder import Reminder
from backend.app.utils.crypto import decrypt

logger = logging.getLogger(__name__)


class EmailService:

    def send_reminder(self, db: Session, reminder: Reminder) -> bool:
        """Send a single reminder email. Returns True on success."""
        config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
        if not config or not config.enabled:
            logger.warning("Email not configured or disabled, skipping reminder")
            return False

        auth = decrypt(config.auth_code)
        if not auth:
            logger.error("Failed to decrypt email auth_code")
            return False

        task = reminder.task
        subject = f"任务提醒：{task.title}"
        body = f"任务「{task.title}」的提醒。\n截止日期：{task.due_date or '未设定'}\n优先级：{task.priority}"

        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = config.sender_email
            msg["To"] = config.sender_email  # Send to self in single-user mode

            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
                server.login(config.sender_email, auth)
                server.sendmail(config.sender_email, [config.sender_email], msg.as_string())

            logger.info(f"Reminder sent for task {task.id}: {task.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reminder for task {task.id}: {e}")
            return False

    def send_test(self, db: Session) -> tuple[bool, str]:
        """Send a test email to verify configuration."""
        config = db.query(EmailConfig).filter(EmailConfig.id == 1).first()
        if not config:
            return False, "邮件配置未找到"

        auth = decrypt(config.auth_code)
        if not auth:
            return False, "授权码解密失败，请重新填写"

        try:
            msg = MIMEText("这是一封来自时间管理平台的测试邮件。配置正确！", "plain", "utf-8")
            msg["Subject"] = "测试邮件 - 时间管理平台"
            msg["From"] = config.sender_email
            msg["To"] = config.sender_email

            with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as server:
                server.login(config.sender_email, auth)
                server.sendmail(config.sender_email, [config.sender_email], msg.as_string())

            return True, "测试邮件发送成功"
        except Exception as e:
            return False, f"发送失败：{str(e)}"

    def scan_and_send(self, db: Session):
        """Called by APScheduler. Scans for due reminders and sends them."""
        now = datetime.utcnow()
        reminders = (
            db.query(Reminder)
            .filter(Reminder.remind_at <= now, Reminder.sent == False, Reminder.fail_count < 3)
            .all()
        )
        for r in reminders:
            success = self.send_reminder(db, r)
            if success:
                r.sent = True
                r.fail_count = 0
            else:
                r.fail_count += 1
            db.commit()
```

- [ ] **Step 3: Create `backend/app/services/stats_service.py`**

```python
"""Statistics service."""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.task import Task


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
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/calendar_service.py backend/app/services/email_service.py backend/app/services/stats_service.py
git commit -m "feat: add CalendarService, EmailService, and StatsService"
```

---

### Task 6: AI Adapters (Ollama + OpenAI)

**Files:**
- Create: `backend/app/adapters/__init__.py`
- Create: `backend/app/adapters/base.py`
- Create: `backend/app/adapters/ollama.py`
- Create: `backend/app/adapters/openai.py`

- [ ] **Step 1: Create `backend/app/adapters/__init__.py`**

```python
from backend.app.adapters.base import BaseAdapter
from backend.app.adapters.ollama import OllamaAdapter
from backend.app.adapters.openai import OpenAIAdapter

__all__ = ["BaseAdapter", "OllamaAdapter", "OpenAIAdapter"]
```

- [ ] **Step 2: Create `backend/app/adapters/base.py`**

```python
"""Abstract base adapter for LLM providers."""
from abc import ABC, abstractmethod


class BaseAdapter(ABC):

    def __init__(self, base_url: str, model: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def chat(self, messages: list[dict], system_prompt: str) -> str:
        """Send messages and return the assistant's reply."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the LLM service is reachable."""
        ...
```

- [ ] **Step 3: Create `backend/app/adapters/ollama.py`**

```python
"""Ollama adapter using the /api/generate endpoint."""
import httpx
from backend.app.adapters.base import BaseAdapter


class OllamaAdapter(BaseAdapter):

    def _build_prompt(self, messages: list[dict], system_prompt: str) -> str:
        parts = [system_prompt]
        for m in messages:
            role_label = "用户" if m["role"] == "user" else "助手"
            parts.append(f"{role_label}: {m['content']}")
        parts.append("助手: ")
        return "\n\n".join(parts)

    def chat(self, messages: list[dict], system_prompt: str) -> str:
        prompt = self._build_prompt(messages, system_prompt)
        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                return resp.json()["response"]
        except Exception as e:
            return f"[错误] Ollama 请求失败：{e}"

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
```

- [ ] **Step 4: Create `backend/app/adapters/openai.py`**

```python
"""OpenAI-compatible adapter using /chat/completions endpoint."""
import httpx
from backend.app.adapters.base import BaseAdapter


class OpenAIAdapter(BaseAdapter):

    def chat(self, messages: list[dict], system_prompt: str) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body = {"model": self.model, "messages": full_messages, "stream": False}

        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=body,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[错误] API 请求失败：{e}"

    def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code == 200
        except Exception:
            return False
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/adapters/
git commit -m "feat: add AI adapters for Ollama and OpenAI-compatible APIs"
```

---

### Task 7: AI Service (system prompt + orchestration)

**Files:**
- Create: `backend/app/utils/system_prompt.py`
- Create: `backend/app/services/ai_service.py`

- [ ] **Step 1: Create `backend/app/utils/system_prompt.py`**

```python
"""Build system prompt with dynamic context injection."""
from datetime import date
import json
from sqlalchemy.orm import Session
from backend.app.models.task import Task

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]


def build_system_prompt(db: Session) -> str:
    today = date.today()
    weekday = WEEKDAYS[today.weekday()]
    tasks = db.query(Task).filter(Task.status != "done").order_by(Task.priority).all()
    tasks_json = json.dumps(
        [{"id": t.id, "title": t.title, "priority": t.priority, "due_date": str(t.due_date) if t.due_date else None} for t in tasks],
        ensure_ascii=False,
    )

    return f"""# 时间上下文
今天是 {today.isoformat()}，星期{weekday}。

# 任务管理准则
- 优先级：🔴高（今天必须完成） > 🟡中（本周完成） > 🟢低
- 任务分解：超过4小时的任务须拆为≤2小时的子任务
- 时间估算：默认每任务45分钟，基于历史数据微调

# 任务拆解规范
- 标题：动词+名词，≤15字
- 预估耗时：精确到15分钟
- 超过2小时的主任务必须分解子任务

# 交互风格
- 称呼用户"你"，以助理口吻对话
- 回复默认 Markdown 格式
- 生成任务后主动询问："需要我将这些任务添加到待办列表吗？"

# 当前任务数据
待办任务：{tasks_json}"""
```

- [ ] **Step 2: Create `backend/app/services/ai_service.py`**

```python
"""AI service that orchestrates LLM adapters with system prompt."""
import re
import json
import logging
from sqlalchemy.orm import Session
from backend.app.models.llm_config import LLMConfig
from backend.app.models.ai_message import AIChatMessage, MessageRole
from backend.app.adapters.ollama import OllamaAdapter
from backend.app.adapters.openai import OpenAIAdapter
from backend.app.utils.system_prompt import build_system_prompt
from backend.app.utils.crypto import decrypt

logger = logging.getLogger(__name__)


class AIService:

    def _get_adapter(self, db: Session):
        config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
        if not config or not config.enabled:
            raise ValueError("AI 服务未配置或未启用")

        api_key = None
        if config.api_key:
            api_key = decrypt(config.api_key) or config.api_key

        if config.provider == "ollama":
            return OllamaAdapter(base_url=config.base_url, model=config.model)
        else:
            return OpenAIAdapter(base_url=config.base_url, model=config.model, api_key=api_key)

    def chat(self, db: Session, user_message: str) -> str:
        adapter = self._get_adapter(db)
        system_prompt = build_system_prompt(db)

        history = (
            db.query(AIChatMessage)
            .order_by(AIChatMessage.created_at.asc())
            .limit(20)
            .all()
        )
        messages = [{"role": m.role, "content": m.content} for m in history]

        # Save user message
        db.add(AIChatMessage(role=MessageRole.user, content=user_message))
        db.commit()

        try:
            reply = adapter.chat(messages + [{"role": "user", "content": user_message}], system_prompt)
        except Exception as e:
            reply = f"[错误] {e}"

        # Save assistant reply
        db.add(AIChatMessage(role=MessageRole.assistant, content=reply))
        db.commit()

        return reply

    def parse_task_from_text(self, text: str) -> list[dict]:
        """Parse natural language text and return task previews using AI."""
        # This calls the LLM with a specific prompt to extract structured tasks
        previews = []
        # Try to extract ```task JSON blocks first (for when chat already produced them)
        task_pattern = r"```task\s*\n(.*?)\n```"
        matches = re.findall(task_pattern, text, re.DOTALL)
        for m in matches:
            try:
                task_data = json.loads(m.strip())
                previews.append(task_data)
            except json.JSONDecodeError:
                pass
        return previews

    def create_task_from_nl(self, db: Session, text: str) -> list[dict]:
        """Ask the LLM to parse natural language into structured task previews."""
        adapter = self._get_adapter(db)
        prompt = f"""从以下用户输入中提取任务信息，以 JSON 数组格式返回（只返回 JSON，不要其他文字）。

用户输入：{text}

每个任务对象格式：
{{"title": "任务标题（动词+名词，≤15字）", "priority": "high|medium|low", "estimated_minutes": 45, "due_date": "YYYY-MM-DD 或 null"}}

只返回 JSON 数组。"""

        try:
            raw = adapter.chat([{"role": "user", "content": prompt}], "你是一个任务解析助手。仅返回 JSON。")
            # Extract JSON array from response
            json_match = re.search(r"\[.*\]", raw, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Failed to parse NL task: {e}")
        return []

    def get_history(self, db: Session) -> list[AIChatMessage]:
        return db.query(AIChatMessage).order_by(AIChatMessage.created_at.asc()).all()

    def clear_history(self, db: Session) -> int:
        count = db.query(AIChatMessage).delete()
        db.commit()
        return count

    def health_check(self, db: Session) -> bool:
        try:
            adapter = self._get_adapter(db)
            return adapter.health_check()
        except Exception:
            return False
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/utils/system_prompt.py backend/app/services/ai_service.py
git commit -m "feat: add AI service with system prompt, dual adapters, and NL task parsing"
```

---

### Task 8: Tasks Router

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/tasks.py`

- [ ] **Step 1: Create `backend/app/routers/__init__.py`**

```python
# backend/app/routers/__init__.py
```

- [ ] **Step 2: Create `backend/app/routers/tasks.py`**

```python
"""Task CRUD API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.task_service import TaskService
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskOut, TaskDetail
from backend.app.schemas.common import success, error

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
        "priority": str(t.priority) if hasattr(t.priority, "value") else t.priority,
        "status": str(t.status) if hasattr(t.status, "value") else t.status,
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
            "method": str(r.method) if hasattr(r.method, "value") else r.method,
            "sent": r.sent,
        }
        for r in (t.reminders or [])
    ]
    return d
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/__init__.py backend/app/routers/tasks.py
git commit -m "feat: add Tasks CRUD API router"
```

---

### Task 9: Calendar, Email, Settings, Stats Routers

**Files:**
- Create: `backend/app/routers/calendar.py`
- Create: `backend/app/routers/email.py`
- Create: `backend/app/routers/settings.py`
- Create: `backend/app/routers/stats.py`

- [ ] **Step 1: Create `backend/app/routers/calendar.py`**

```python
"""Calendar API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.calendar_service import CalendarService
from backend.app.schemas.common import success

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
```

- [ ] **Step 2: Create `backend/app/routers/email.py`**

```python
"""Email and reminder API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.email_config import EmailConfig
from backend.app.models.reminder import Reminder
from backend.app.services.email_service import EmailService
from backend.app.schemas.email_config import EmailConfigUpdate, EmailConfigOut
from backend.app.schemas.reminder import ReminderCreate, ReminderOut
from backend.app.schemas.common import success, error
from backend.app.utils.crypto import encrypt

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
        {"id": r.id, "task_id": r.task_id, "remind_at": str(r.remind_at), "method": str(r.method.value), "sent": r.sent}
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
```

- [ ] **Step 3: Create `backend/app/routers/settings.py`**

```python
"""Settings API routes (LLM config)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.llm_config import LLMConfig
from backend.app.services.ai_service import AIService
from backend.app.schemas.llm_config import LLMConfigUpdate
from backend.app.schemas.common import success, error
from backend.app.utils.crypto import encrypt

router = APIRouter(prefix="/api/settings", tags=["settings"])
ai_service = AIService()


@router.get("/llm")
def get_llm_config(db: Session = Depends(get_db)):
    config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)

    masked_key = ""
    if config.api_key:
        masked_key = config.api_key[:4] + "****" if len(config.api_key) > 4 else "****"

    return success(data={
        "id": config.id,
        "provider": str(config.provider.value) if hasattr(config.provider, "value") else config.provider,
        "base_url": config.base_url,
        "api_key": masked_key,
        "model": config.model,
        "enabled": config.enabled,
    })


@router.put("/llm")
def update_llm_config(data: LLMConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)

    config.provider = data.provider
    config.base_url = data.base_url
    if data.api_key:
        config.api_key = encrypt(data.api_key)
    elif data.api_key == "":
        config.api_key = ""
    config.model = data.model
    config.enabled = data.enabled
    db.commit()
    db.refresh(config)
    return success(message="LLM 配置已更新")


@router.post("/llm/test")
def test_llm(db: Session = Depends(get_db)):
    try:
        ok = ai_service.health_check(db)
        if ok:
            return success(message="LLM 连接成功")
        return error(message="LLM 连接失败，请检查配置")
    except ValueError as e:
        return error(message=str(e))
```

- [ ] **Step 4: Create `backend/app/routers/stats.py`**

```python
"""Statistics API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.stats_service import StatsService
from backend.app.schemas.common import success

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
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/calendar.py backend/app/routers/email.py backend/app/routers/settings.py backend/app/routers/stats.py
git commit -m "feat: add Calendar, Email, Settings, and Stats API routers"
```

---

### Task 10: AI Router

**Files:**
- Create: `backend/app/routers/ai.py`

- [ ] **Step 1: Create `backend/app/routers/ai.py`**

```python
"""AI chat API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.ai_service import AIService
from backend.app.schemas.ai import ChatRequest, AICreateTaskRequest
from backend.app.schemas.common import success, error

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
            "role": str(m.role.value) if hasattr(m.role, "value") else m.role,
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/routers/ai.py
git commit -m "feat: add AI chat router with NL task parsing"
```

---

### Task 11: FastAPI main app + startup

**Files:**
- Create: `backend/app/main.py`

- [ ] **Step 1: Create `backend/app/main.py`**

```python
"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.email_service import EmailService
from backend.app.config import REMINDER_SCAN_INTERVAL

from backend.app.routers import tasks, calendar, ai, email, settings, stats


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
```

- [ ] **Step 2: Start backend and verify**

```bash
cd backend && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000/api/health` → Expected: `{"status":"ok"}`

Test `http://localhost:8000/api/tasks` → Expected: `{"code":0,"data":[],"message":"ok"}`

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat: add FastAPI main app with APScheduler and CORS"
```

---

### Task 12: Frontend project scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "time-management-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "pinia": "^2.3.0",
    "axios": "^1.7.9",
    "element-plus": "^2.9.1",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "typescript": "^5.7.2",
    "vite": "^6.0.5",
    "vue-tsc": "^2.2.0"
  }
}
```

- [ ] **Step 2: Create `frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "noEmit": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "src/env.d.ts"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: Create `frontend/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: Create `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>时间管理平台</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 6: Create `frontend/src/env.d.ts`**

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 7: Create `frontend/src/main.ts`**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

- [ ] **Step 8: Create `frontend/src/App.vue`**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
```

- [ ] **Step 9: Install and verify frontend**

```bash
cd frontend && npm install && npm run dev
```

Expected: dev server starts on http://localhost:5173

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: frontend project scaffolding with Vue 3, Element Plus, Vite"
```

---

### Task 13: Vue Router + API client + Pinia stores

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/tasks.ts`
- Create: `frontend/src/api/calendar.ts`
- Create: `frontend/src/api/ai.ts`
- Create: `frontend/src/api/email.ts`
- Create: `frontend/src/api/settings.ts`
- Create: `frontend/src/stores/task.ts`
- Create: `frontend/src/stores/ai.ts`

- [ ] **Step 1: Create `frontend/src/router/index.ts`**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/tasks' },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('@/views/TaskBoard.vue'),
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
    },
    {
      path: '/ai-chat',
      name: 'ai-chat',
      component: () => import('@/views/AIChat.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/Settings.vue'),
    },
  ],
})

export default router
```

- [ ] **Step 2: Create `frontend/src/api/client.ts`**

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

client.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body.code && body.code !== 0) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message))
    }
    return res
  },
  (err) => {
    ElMessage.error(err.response?.data?.detail || err.message || '网络错误')
    return Promise.reject(err)
  }
)

export default client
```

- [ ] **Step 3: Create `frontend/src/api/tasks.ts`**

```typescript
import client from './client'

export interface TaskData {
  id?: number
  title: string
  description?: string
  priority: string
  status: string
  due_date?: string | null
  due_time?: string | null
  estimated_minutes?: number | null
  actual_minutes?: number | null
  parent_id?: number | null
  tags: string
  created_at?: string
  updated_at?: string
  subtasks?: TaskData[]
}

export const taskApi = {
  list(params?: Record<string, string>) {
    return client.get('/tasks', { params }).then(r => r.data.data)
  },
  create(data: Partial<TaskData>) {
    return client.post('/tasks', data).then(r => r.data.data)
  },
  get(id: number) {
    return client.get(`/tasks/${id}`).then(r => r.data.data)
  },
  update(id: number, data: Partial<TaskData>) {
    return client.put(`/tasks/${id}`, data).then(r => r.data.data)
  },
  delete(id: number) {
    return client.delete(`/tasks/${id}`).then(r => r.data)
  },
  updateStatus(id: number, status: string) {
    return client.patch(`/tasks/${id}/status`, { status }).then(r => r.data.data)
  },
}
```

- [ ] **Step 4: Create `frontend/src/api/calendar.ts`**

```typescript
import client from './client'

export const calendarApi = {
  getMonth(year: number, month: number) {
    return client.get('/calendar', { params: { year, month } }).then(r => r.data.data)
  },
  getWeek(start: string, end: string) {
    return client.get('/calendar/week', { params: { start, end } }).then(r => r.data.data)
  },
}
```

- [ ] **Step 5: Create `frontend/src/api/ai.ts`**

```typescript
import client from './client'

export const aiApi = {
  chat(message: string) {
    return client.post('/ai/chat', { message }).then(r => r.data.data)
  },
  getHistory() {
    return client.get('/ai/history').then(r => r.data.data)
  },
  clearHistory() {
    return client.delete('/ai/history').then(r => r.data)
  },
  createTaskFromNL(text: string) {
    return client.post('/ai/create-task', { text }).then(r => r.data.data)
  },
}
```

- [ ] **Step 6: Create `frontend/src/api/email.ts`**

```typescript
import client from './client'

export const emailApi = {
  getConfig() {
    return client.get('/email/config').then(r => r.data.data)
  },
  updateConfig(data: any) {
    return client.put('/email/config', data).then(r => r.data)
  },
  test() {
    return client.post('/email/test').then(r => r.data)
  },
  listReminders(taskId: number) {
    return client.get('/reminders', { params: { task_id: taskId } }).then(r => r.data.data)
  },
  createReminder(data: { task_id: number; remind_at: string; method: string }) {
    return client.post('/reminders', data).then(r => r.data.data)
  },
  deleteReminder(id: number) {
    return client.delete(`/reminders/${id}`).then(r => r.data)
  },
}
```

- [ ] **Step 7: Create `frontend/src/api/settings.ts`**

```typescript
import client from './client'

export const settingsApi = {
  getLLMConfig() {
    return client.get('/settings/llm').then(r => r.data.data)
  },
  updateLLMConfig(data: any) {
    return client.put('/settings/llm', data).then(r => r.data)
  },
  testLLM() {
    return client.post('/settings/llm/test').then(r => r.data)
  },
}
```

- [ ] **Step 8: Create `frontend/src/stores/task.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskApi, type TaskData } from '@/api/tasks'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskData[]>([])
  const loading = ref(false)

  async function fetchTasks(params?: Record<string, string>) {
    loading.value = true
    try {
      tasks.value = await taskApi.list(params)
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: Partial<TaskData>) {
    const task = await taskApi.create(data)
    await fetchTasks()
    return task
  }

  async function updateTask(id: number, data: Partial<TaskData>) {
    const task = await taskApi.update(id, data)
    await fetchTasks()
    return task
  }

  async function deleteTask(id: number) {
    await taskApi.delete(id)
    await fetchTasks()
  }

  async function updateStatus(id: number, status: string) {
    await taskApi.updateStatus(id, status)
    await fetchTasks()
  }

  return { tasks, loading, fetchTasks, createTask, updateTask, deleteTask, updateStatus }
})
```

- [ ] **Step 9: Create `frontend/src/stores/ai.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { aiApi } from '@/api/ai'

export interface ChatMessage {
  id?: number
  role: string
  content: string
  task_previews?: any[]
}

export const useAiStore = defineStore('ai', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function sendMessage(text: string) {
    messages.value.push({ role: 'user', content: text })
    loading.value = true
    try {
      const result = await aiApi.chat(text)
      messages.value.push({
        role: 'assistant',
        content: result.reply,
        task_previews: result.task_previews,
      })
    } finally {
      loading.value = false
    }
  }

  async function loadHistory() {
    messages.value = await aiApi.getHistory()
  }

  async function clearHistory() {
    await aiApi.clearHistory()
    messages.value = []
  }

  return { messages, loading, sendMessage, loadHistory, clearHistory }
})
```

- [ ] **Step 10: Commit**

```bash
git add frontend/src/router/ frontend/src/api/ frontend/src/stores/
git commit -m "feat: add Vue Router, Axios API client, and Pinia stores"
```

---

### Task 14: TaskBoard view + KanbanColumn + TaskCard components

**Files:**
- Create: `frontend/src/views/TaskBoard.vue`
- Create: `frontend/src/components/KanbanColumn.vue`
- Create: `frontend/src/components/TaskCard.vue`

- [ ] **Step 1: Create `frontend/src/components/TaskCard.vue`**

```vue
<template>
  <el-card
    class="task-card"
    :class="`priority-${task.priority}`"
    shadow="hover"
    @click="$emit('click', task)"
  >
    <div class="card-header">
      <span class="priority-dot" :class="task.priority"></span>
      <span class="title">{{ task.title }}</span>
    </div>
    <div class="card-meta" v-if="task.due_date || task.tags">
      <el-tag v-if="task.due_date" size="small" type="info">{{ task.due_date }}</el-tag>
      <el-tag v-if="task.tags" v-for="tag in tagList" :key="tag" size="small" class="tag-item">{{ tag }}</el-tag>
    </div>
    <div class="card-footer" v-if="task.subtasks?.length">
      <span class="subtask-count">子任务: {{ task.subtasks.length }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TaskData } from '@/api/tasks'

const props = defineProps<{ task: TaskData }>()
defineEmits<{ click: [task: TaskData] }>()

const tagList = computed(() => {
  return props.task.tags ? props.task.tags.split(',').filter(Boolean) : []
})
</script>

<style scoped>
.task-card {
  margin-bottom: 8px;
  cursor: pointer;
  border-left: 3px solid #ddd;
  transition: transform 0.2s;
}
.task-card:hover { transform: translateY(-1px); }
.priority-high { border-left-color: #f56c6c; }
.priority-medium { border-left-color: #e6a23c; }
.priority-low { border-left-color: #67c23a; }
.card-header { display: flex; align-items: center; gap: 8px; }
.priority-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.priority-dot.high { background: #f56c6c; }
.priority-dot.medium { background: #e6a23c; }
.priority-dot.low { background: #67c23a; }
.title { font-size: 14px; font-weight: 500; }
.card-meta { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.card-footer { margin-top: 8px; }
.subtask-count { font-size: 12px; color: #909399; }
</style>
```

- [ ] **Step 2: Create `frontend/src/components/KanbanColumn.vue`**

```vue
<template>
  <div class="kanban-column">
    <div class="column-header">
      <span class="column-title">{{ title }}</span>
      <el-tag size="small" type="info">{{ tasks.length }}</el-tag>
    </div>
    <div class="column-body" @dragover.prevent @drop="onDrop">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @click="$emit('task-click', task)"
        draggable="true"
        @dragstart="onDragStart($event, task)"
      />
      <div v-if="tasks.length === 0" class="empty-hint">暂无任务</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import TaskCard from './TaskCard.vue'
import type { TaskData } from '@/api/tasks'

defineProps<{ title: string; tasks: TaskData[] }>()
const emit = defineEmits<{
  'task-click': [task: TaskData]
  'drop-task': [taskId: number, newStatus: string]
}>()

function onDragStart(e: DragEvent, task: TaskData) {
  e.dataTransfer!.setData('taskId', String(task.id))
}

function onDrop(e: DragEvent) {
  const taskId = Number(e.dataTransfer!.getData('taskId'))
  const statusMap: Record<string, string> = {
    '待办': 'todo',
    '进行中': 'in_progress',
    '已完成': 'done',
  }
  const colTitle = (e.currentTarget as HTMLElement).closest('.kanban-column')?.querySelector('.column-title')?.textContent
  const newStatus = statusMap[colTitle || ''] || 'todo'
  if (taskId) emit('drop-task', taskId, newStatus)
}
</script>

<style scoped>
.kanban-column {
  flex: 1; min-width: 280px; max-width: 400px;
  background: #f5f7fa; border-radius: 8px; padding: 12px;
  display: flex; flex-direction: column;
}
.column-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e4e7ed;
}
.column-title { font-size: 15px; font-weight: 600; }
.column-body { flex: 1; overflow-y: auto; min-height: 200px; }
.empty-hint { text-align: center; color: #c0c4cc; padding: 40px 0; font-size: 14px; }
</style>
```

- [ ] **Step 3: Create `frontend/src/views/TaskBoard.vue`**

```vue
<template>
  <div class="task-board-page">
    <el-header class="board-header">
      <h2>任务看板</h2>
      <div class="header-actions">
        <el-input
          v-model="searchText"
          placeholder="搜索任务..."
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @input="onSearch"
        />
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 创建任务
        </el-button>
        <el-button @click="showAICreateDialog = true">
          <el-icon><MagicStick /></el-icon> AI 快速创建
        </el-button>
      </div>
    </el-header>

    <div class="kanban-container">
      <KanbanColumn
        title="待办"
        :tasks="todoTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
      <KanbanColumn
        title="进行中"
        :tasks="inProgressTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
      <KanbanColumn
        title="已完成"
        :tasks="doneTasks"
        @task-click="openDetail"
        @drop-task="onDrop"
      />
    </div>

    <!-- Task Create/Edit Dialog -->
    <TaskForm
      v-model:visible="showCreateDialog"
      @saved="onTaskSaved"
    />
    <TaskForm
      v-if="editingTask"
      v-model:visible="showEditDialog"
      :task="editingTask"
      @saved="onTaskSaved"
    />

    <!-- AI Quick Create Dialog -->
    <el-dialog v-model="showAICreateDialog" title="AI 快速创建任务" width="500px">
      <el-input
        v-model="aiText"
        type="textarea"
        :rows="3"
        placeholder="描述你想创建的任务，例如：明天下午3点和王经理开会讨论Q3预算"
      />
      <div v-if="aiPreviews.length" style="margin-top: 16px">
        <el-card v-for="(p, i) in aiPreviews" :key="i" style="margin-bottom: 8px">
          <div>{{ p.title }} — {{ p.priority }} — {{ p.estimated_minutes }}分钟</div>
          <el-button size="small" type="primary" @click="confirmAITask(p)">添加</el-button>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="showAICreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="aiLoading" @click="doAIParse">解析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TaskForm from '@/components/TaskForm.vue'
import { useTaskStore } from '@/stores/task'
import { aiApi } from '@/api/ai'
import { taskApi, type TaskData } from '@/api/tasks'
import type { TaskData } from '@/api/tasks'

const store = useTaskStore()
const searchText = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showAICreateDialog = ref(false)
const editingTask = ref<TaskData | null>(null)
const aiText = ref('')
const aiPreviews = ref<any[]>([])
const aiLoading = ref(false)

const todoTasks = computed(() => store.tasks.filter(t => t.status === 'todo'))
const inProgressTasks = computed(() => store.tasks.filter(t => t.status === 'in_progress'))
const doneTasks = computed(() => store.tasks.filter(t => t.status === 'done'))

onMounted(() => store.fetchTasks())

function onSearch() {
  store.fetchTasks(searchText.value ? { search: searchText.value } : undefined)
}

function onDrop(taskId: number, newStatus: string) {
  store.updateStatus(taskId, newStatus)
}

function openDetail(task: TaskData) {
  editingTask.value = task
  showEditDialog.value = true
}

function onTaskSaved() {
  showCreateDialog.value = false
  showEditDialog.value = false
  editingTask.value = null
  store.fetchTasks()
}

async function doAIParse() {
  if (!aiText.value.trim()) return
  aiLoading.value = true
  try {
    aiPreviews.value = await aiApi.createTaskFromNL(aiText.value)
  } finally {
    aiLoading.value = false
  }
}

async function confirmAITask(preview: any) {
  await store.createTask(preview)
  ElMessage.success('任务已添加')
  aiPreviews.value = aiPreviews.value.filter(p => p !== preview)
}
</script>

<style scoped>
.task-board-page { height: 100vh; display: flex; flex-direction: column; }
.board-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed; height: auto;
}
.board-header h2 { margin: 0; font-size: 20px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.kanban-container {
  flex: 1; display: flex; gap: 16px; padding: 24px; overflow-x: auto;
}
</style>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/TaskBoard.vue frontend/src/components/TaskCard.vue frontend/src/components/KanbanColumn.vue
git commit -m "feat: add TaskBoard view with Kanban columns, drag-drop, and AI quick create"
```

---

### Task 15: TaskForm component

**Files:**
- Create: `frontend/src/components/TaskForm.vue`

- [ ] **Step 1: Create `frontend/src/components/TaskForm.vue`**

```vue
<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="isEditing ? '编辑任务' : '创建任务'"
    width="560px"
    @close="resetForm"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="任务标题" maxlength="200" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="详细描述（可选）" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="优先级">
            <el-select v-model="form.priority">
              <el-option label="🔴 高" value="high" />
              <el-option label="🟡 中" value="medium" />
              <el-option label="🟢 低" value="low" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="done" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="截止日期">
            <el-date-picker v-model="form.due_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="截止时间">
            <el-time-picker v-model="form.due_time" placeholder="选择时间" value-format="HH:mm:ss" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="预估耗时">
        <el-input-number v-model="form.estimated_minutes" :min="0" :step="15" placeholder="分钟" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" placeholder="用逗号分隔，如：项目,紧急" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { TaskData } from '@/api/tasks'
import { useTaskStore } from '@/stores/task'

const props = defineProps<{
  visible: boolean
  task?: TaskData | null
}>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: []
}>()

const store = useTaskStore()
const formRef = ref()
const isEditing = ref(false)

const form = reactive({
  title: '',
  description: '',
  priority: 'medium',
  status: 'todo',
  due_date: null as string | null,
  due_time: null as string | null,
  estimated_minutes: null as number | null,
  tags: '',
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
}

watch(() => props.visible, (val) => {
  if (val && props.task) {
    isEditing.value = true
    Object.assign(form, {
      title: props.task.title,
      description: props.task.description || '',
      priority: props.task.priority,
      status: props.task.status,
      due_date: props.task.due_date || null,
      due_time: props.task.due_time || null,
      estimated_minutes: props.task.estimated_minutes || null,
      tags: props.task.tags || '',
    })
  } else if (val) {
    isEditing.value = false
    resetForm()
  }
})

function resetForm() {
  isEditing.value = false
  form.title = ''
  form.description = ''
  form.priority = 'medium'
  form.status = 'todo'
  form.due_date = null
  form.due_time = null
  form.estimated_minutes = null
  form.tags = ''
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    if (isEditing.value && props.task?.id) {
      await store.updateTask(props.task.id, { ...form })
      ElMessage.success('任务已更新')
    } else {
      await store.createTask({ ...form })
      ElMessage.success('任务已创建')
    }
    emit('saved')
  } catch { /* error handled by interceptor */ }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/TaskForm.vue
git commit -m "feat: add TaskForm component for create/edit"
```

---

### Task 16: CalendarView + MonthCalendar + WeekCalendar

**Files:**
- Create: `frontend/src/views/CalendarView.vue`
- Create: `frontend/src/components/MonthCalendar.vue`
- Create: `frontend/src/components/WeekCalendar.vue`

- [ ] **Step 1: Create `frontend/src/components/MonthCalendar.vue`**

```vue
<template>
  <div class="month-calendar">
    <div class="calendar-nav">
      <el-button @click="prevMonth" :icon="ArrowLeft" circle size="small" />
      <span class="month-label">{{ year }}年 {{ month }}月</span>
      <el-button @click="nextMonth" :icon="ArrowRight" circle size="small" />
    </div>
    <div class="weekday-header">
      <span v-for="d in weekdays" :key="d" class="weekday">{{ d }}</span>
    </div>
    <div class="days-grid">
      <div
        v-for="(day, idx) in calendarDays"
        :key="idx"
        class="day-cell"
        :class="{ 'other-month': !day.currentMonth, 'has-tasks': day.tasks?.length }"
        @click="day.currentMonth && $emit('day-click', day.date)"
      >
        <span class="day-num">{{ day.day }}</span>
        <div class="day-dots" v-if="day.tasks?.length">
          <span
            v-for="t in day.tasks.slice(0, 3)"
            :key="t.id"
            class="dot"
            :class="t.priority"
          ></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  year: number
  month: number
  tasks: Record<string, any[]>
}>()
const emit = defineEmits<{
  'prev': []
  'next': []
  'day-click': [date: string]
}>()

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const calendarDays = computed(() => {
  const firstDay = new Date(props.year, props.month - 1, 1)
  const lastDay = new Date(props.year, props.month, 0)
  const startDayOfWeek = firstDay.getDay()

  const days: any[] = []

  // Previous month padding
  const prevLastDay = new Date(props.year, props.month - 1, 0).getDate()
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const d = prevLastDay - i
    const dateStr = `${props.year}-${String(props.month - 1 || 12).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ day: d, currentMonth: false, date: dateStr, tasks: [] })
  }

  // Current month
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${props.year}-${String(props.month).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      day: d,
      currentMonth: true,
      date: dateStr,
      tasks: props.tasks[dateStr] || [],
    })
  }

  // Next month padding
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ day: d, currentMonth: false, date: '', tasks: [] })
  }

  return days
})

function prevMonth() { emit('prev') }
function nextMonth() { emit('next') }
</script>

<style scoped>
.month-calendar { user-select: none; }
.calendar-nav {
  display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;
}
.month-label { font-size: 16px; font-weight: 600; }
.weekday-header { display: grid; grid-template-columns: repeat(7, 1fr); margin-bottom: 4px; }
.weekday { text-align: center; font-size: 13px; color: #909399; padding: 8px 0; }
.days-grid { display: grid; grid-template-columns: repeat(7, 1fr); }
.day-cell {
  aspect-ratio: 1; border: 1px solid #ebeef5; padding: 4px;
  display: flex; flex-direction: column; cursor: pointer;
}
.day-cell.other-month { background: #fafafa; cursor: default; }
.day-cell.has-tasks { background: #ecf5ff; }
.day-num { font-size: 14px; color: #303133; }
.day-dots { display: flex; gap: 2px; margin-top: 4px; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.high { background: #f56c6c; }
.dot.medium { background: #e6a23c; }
.dot.low { background: #67c23a; }
</style>
```

- [ ] **Step 2: Create `frontend/src/components/WeekCalendar.vue`**

```vue
<template>
  <div class="week-calendar">
    <div class="calendar-nav">
      <el-button @click="$emit('prev')" :icon="ArrowLeft" circle size="small" />
      <span class="week-label">{{ weekLabel }}</span>
      <el-button @click="$emit('next')" :icon="ArrowRight" circle size="small" />
    </div>
    <div class="week-grid">
      <div v-for="day in weekDays" :key="day.date" class="week-day-col">
        <div class="day-header">
          <span class="day-name">{{ day.name }}</span>
          <span class="day-date">{{ day.label }}</span>
        </div>
        <div class="day-tasks">
          <div
            v-for="task in day.tasks"
            :key="task.id"
            class="week-task-item"
            :class="task.priority"
            @click="$emit('task-click', task)"
          >
            <span class="task-title">{{ task.title }}</span>
            <span class="task-time" v-if="task.due_time">{{ task.due_time.slice(0, 5) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  startDate: string
  tasks: Record<string, any[]>
}>()
defineEmits<{
  'prev': []
  'next': []
  'task-click': [task: any]
}>()

const dayNames = ['日', '一', '二', '三', '四', '五', '六']

const weekDays = computed(() => {
  const start = new Date(props.startDate + 'T00:00:00')
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    const dateStr = d.toISOString().slice(0, 10)
    days.push({
      name: dayNames[d.getDay()],
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      date: dateStr,
      tasks: props.tasks[dateStr] || [],
    })
  }
  return days
})

const weekLabel = computed(() => {
  if (weekDays.value.length) {
    return `${weekDays.value[0].date} ~ ${weekDays.value[6].date}`
  }
  return ''
})
</script>

<style scoped>
.week-calendar { }
.calendar-nav {
  display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 16px;
}
.week-label { font-size: 16px; font-weight: 600; }
.week-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.week-day-col { border: 1px solid #ebeef5; min-height: 400px; }
.day-header {
  text-align: center; padding: 8px; background: #f5f7fa; border-bottom: 1px solid #ebeef5;
}
.day-name { font-size: 12px; color: #909399; }
.day-date { font-size: 16px; font-weight: 600; margin-left: 4px; }
.day-tasks { padding: 4px; }
.week-task-item {
  padding: 6px 8px; margin-bottom: 4px; border-radius: 4px;
  font-size: 12px; cursor: pointer; background: #ecf5ff;
  border-left: 3px solid #409eff;
}
.week-task-item.high { background: #fef0f0; border-left-color: #f56c6c; }
.week-task-item.medium { background: #fdf6ec; border-left-color: #e6a23c; }
.week-task-item.low { background: #f0f9eb; border-left-color: #67c23a; }
.task-title { display: block; }
.task-time { color: #909399; font-size: 11px; }
</style>
```

- [ ] **Step 3: Create `frontend/src/views/CalendarView.vue`**

```vue
<template>
  <div class="calendar-page">
    <el-header class="page-header">
      <h2>日历视图</h2>
      <el-radio-group v-model="viewMode">
        <el-radio-button value="month">月视图</el-radio-button>
        <el-radio-button value="week">周视图</el-radio-button>
      </el-radio-group>
    </el-header>

    <div class="calendar-content">
      <MonthCalendar
        v-if="viewMode === 'month'"
        :year="currentYear"
        :month="currentMonth"
        :tasks="tasksByDate"
        @prev="changeMonth(-1)"
        @next="changeMonth(1)"
        @day-click="onDayClick"
      />
      <WeekCalendar
        v-else
        :start-date="weekStart"
        :tasks="tasksByDate"
        @prev="changeWeek(-1)"
        @next="changeWeek(1)"
        @task-click="openTask"
      />
    </div>

    <!-- Day detail dialog -->
    <el-dialog v-model="showDayDialog" :title="selectedDate" width="480px">
      <div v-for="task in selectedTasks" :key="task.id" style="margin-bottom: 8px">
        <el-card>
          <strong>{{ task.title }}</strong>
          <el-tag size="small" :type="priorityType(task.priority)" style="margin-left: 8px">{{ task.priority }}</el-tag>
          <el-tag size="small" style="margin-left: 4px">{{ task.status }}</el-tag>
        </el-card>
      </div>
      <div v-if="!selectedTasks.length">当天无任务</div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MonthCalendar from '@/components/MonthCalendar.vue'
import WeekCalendar from '@/components/WeekCalendar.vue'
import { calendarApi } from '@/api/calendar'

const viewMode = ref<'month' | 'week'>('month')
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const tasksByDate = ref<Record<string, any[]>>({})
const weekStart = ref('')
const showDayDialog = ref(false)
const selectedDate = ref('')
const selectedTasks = ref<any[]>([])

onMounted(async () => {
  await loadMonth()
  setWeekStart()
})

async function loadMonth() {
  tasksByDate.value = await calendarApi.getMonth(currentYear.value, currentMonth.value)
}

async function loadWeek() {
  const end = new Date(weekStart.value + 'T00:00:00')
  end.setDate(end.getDate() + 6)
  const endStr = end.toISOString().slice(0, 10)
  tasksByDate.value = await calendarApi.getWeek(weekStart.value, endStr)
}

function changeMonth(delta: number) {
  currentMonth.value += delta
  if (currentMonth.value > 12) { currentMonth.value = 1; currentYear.value++ }
  if (currentMonth.value < 1) { currentMonth.value = 12; currentYear.value-- }
  loadMonth()
}

function setWeekStart() {
  const today = new Date()
  const day = today.getDay()
  const diff = today.getDate() - day
  weekStart.value = new Date(today.setDate(diff)).toISOString().slice(0, 10)
}

function changeWeek(delta: number) {
  const d = new Date(weekStart.value + 'T00:00:00')
  d.setDate(d.getDate() + delta * 7)
  weekStart.value = d.toISOString().slice(0, 10)
  loadWeek()
}

function onDayClick(dateStr: string) {
  selectedDate.value = dateStr
  selectedTasks.value = tasksByDate.value[dateStr] || []
  showDayDialog.value = true
}

function openTask(task: any) { /* navigate or open detail */ }

function priorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'success'
}
</script>

<style scoped>
.calendar-page { height: 100vh; display: flex; flex-direction: column; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed; height: auto;
}
.page-header h2 { margin: 0; }
.calendar-content { flex: 1; padding: 24px; overflow-y: auto; }
</style>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/CalendarView.vue frontend/src/components/MonthCalendar.vue frontend/src/components/WeekCalendar.vue
git commit -m "feat: add Calendar view with month/week toggle"
```

---

### Task 17: AIChat view + ChatMessage + TaskPreviewCard

**Files:**
- Create: `frontend/src/views/AIChat.vue`
- Create: `frontend/src/components/ChatMessage.vue`
- Create: `frontend/src/components/TaskPreviewCard.vue`

- [ ] **Step 1: Create `frontend/src/components/TaskPreviewCard.vue`**

```vue
<template>
  <el-card class="task-preview" shadow="never">
    <div class="preview-content">
      <strong>{{ task.title }}</strong>
      <el-tag size="small" :type="priorityType(task.priority)" style="margin-left: 8px">{{ task.priority }}</el-tag>
      <span style="margin-left: 8px; color: #909399; font-size: 13px">{{ task.estimated_minutes }}分钟</span>
      <span v-if="task.due_date" style="margin-left: 8px; color: #909399; font-size: 13px">{{ task.due_date }}</span>
    </div>
    <el-button type="primary" size="small" @click="$emit('add', task)">添加到待办</el-button>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ task: { title: string; priority: string; estimated_minutes: number; due_date?: string } }>()
defineEmits<{ add: [task: any] }>()

function priorityType(p: string) {
  return p === 'high' ? 'danger' : p === 'medium' ? 'warning' : 'success'
}
</script>

<style scoped>
.task-preview {
  margin: 8px 0; display: flex; justify-content: space-between; align-items: center;
}
.preview-content { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
</style>
```

- [ ] **Step 2: Create `frontend/src/components/ChatMessage.vue`**

```vue
<template>
  <div class="chat-msg" :class="role">
    <div class="msg-avatar">
      <el-avatar :size="32" :icon="role === 'user' ? UserFilled : Service" />
    </div>
    <div class="msg-body">
      <div class="msg-content" v-html="renderedContent"></div>
      <TaskPreviewCard
        v-for="(task, i) in taskPreviews"
        :key="i"
        :task="task"
        @add="$emit('add-task', task)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserFilled, Service } from '@element-plus/icons-vue'
import { marked } from 'marked'

const props = defineProps<{
  role: string
  content: string
  taskPreviews?: any[]
}>()
defineEmits<{ 'add-task': [task: any] }>()

const renderedContent = computed(() => {
  // Remove ```task blocks from rendered markdown
  const cleaned = props.content.replace(/```task[\s\S]*?```/g, '')
  return marked(cleaned)
})
</script>

<style scoped>
.chat-msg { display: flex; gap: 12px; margin-bottom: 16px; }
.chat-msg.assistant { flex-direction: row; }
.chat-msg.user { flex-direction: row-reverse; }
.msg-body { max-width: 70%; }
.msg-content {
  background: #f5f7fa; padding: 12px 16px; border-radius: 8px;
  font-size: 14px; line-height: 1.6;
}
.chat-msg.user .msg-content { background: #409eff; color: #fff; }
</style>
```

- [ ] **Step 3: Create `frontend/src/views/AIChat.vue`**

```vue
<template>
  <div class="ai-chat-page">
    <el-header class="chat-header">
      <h2>AI 助手</h2>
      <div class="header-right">
        <el-tag :type="llmConnected ? 'success' : 'danger'" size="small">
          {{ llmConnected ? '已连接' : '未连接' }} — {{ llmModel }}
        </el-tag>
        <el-button @click="store.clearHistory()" size="small">清空对话</el-button>
      </div>
    </el-header>

    <div class="chat-body" ref="chatBodyRef">
      <ChatMessage
        v-for="msg in store.messages"
        :key="msg.id || Math.random()"
        :role="msg.role"
        :content="msg.content"
        :task-previews="msg.task_previews"
        @add-task="addTask"
      />
      <div v-if="store.loading" class="typing-hint">AI 正在思考...</div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入消息，例如：帮我规划明天的任务..."
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" @click="send" :loading="store.loading" style="margin-left: 8px">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import ChatMessage from '@/components/ChatMessage.vue'
import { useAiStore } from '@/stores/ai'
import { useTaskStore } from '@/stores/task'
import { settingsApi } from '@/api/settings'

const store = useAiStore()
const taskStore = useTaskStore()
const inputText = ref('')
const chatBodyRef = ref<HTMLElement>()
const llmConnected = ref(false)
const llmModel = ref('')

onMounted(async () => {
  await store.loadHistory()
  try {
    const config = await settingsApi.getLLMConfig()
    llmModel.value = config.model
    const test = await settingsApi.testLLM()
    llmConnected.value = test.code === 0
  } catch { llmConnected.value = false }
})

async function send() {
  const text = inputText.value.trim()
  if (!text) return
  inputText.value = ''
  await store.sendMessage(text)
  await nextTick()
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

async function addTask(task: any) {
  try {
    await taskStore.createTask(task)
    ElMessage.success(`任务「${task.title}」已添加到待办列表`)
  } catch { /* handled by interceptor */ }
}
</script>

<style scoped>
.ai-chat-page { height: 100vh; display: flex; flex-direction: column; }
.chat-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 24px; border-bottom: 1px solid #e4e7ed; height: auto;
}
.chat-header h2 { margin: 0; }
.header-right { display: flex; align-items: center; gap: 12px; }
.chat-body { flex: 1; overflow-y: auto; padding: 24px; }
.typing-hint { color: #909399; font-size: 13px; padding: 12px; }
.chat-input {
  display: flex; align-items: flex-end; padding: 16px 24px;
  border-top: 1px solid #e4e7ed; background: #fff;
}
</style>
```

- [ ] **Step 4: Install `marked` dependency**

```bash
cd frontend && npm install marked
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/AIChat.vue frontend/src/components/ChatMessage.vue frontend/src/components/TaskPreviewCard.vue frontend/package.json
git commit -m "feat: add AI Chat view with markdown rendering and task preview cards"
```

---

### Task 18: Settings view

**Files:**
- Create: `frontend/src/views/Settings.vue`

- [ ] **Step 1: Create `frontend/src/views/Settings.vue`**

```vue
<template>
  <div class="settings-page">
    <el-header class="page-header">
      <h2>设置</h2>
    </el-header>

    <div class="settings-content">
      <!-- LLM Config Card -->
      <el-card class="config-card">
        <template #header>
          <span class="card-title">🤖 大模型配置</span>
          <el-button size="small" :loading="llmTesting" @click="testLLM" style="float: right">测试连接</el-button>
        </template>
        <el-form :model="llmForm" label-width="100px">
          <el-form-item label="Provider">
            <el-select v-model="llmForm.provider">
              <el-option label="Ollama (本地)" value="ollama" />
              <el-option label="OpenAI" value="openai" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="llmForm.base_url" placeholder="http://localhost:11434" />
          </el-form-item>
          <el-form-item label="API Key" v-if="llmForm.provider !== 'ollama'">
            <el-input v-model="llmForm.api_key" type="password" show-password placeholder="sk-..." />
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="llmForm.model" placeholder="deepseek-r1:7b" />
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="llmForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveLLM">保存 LLM 配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Email Config Card -->
      <el-card class="config-card">
        <template #header>
          <span class="card-title">📧 邮件配置</span>
          <el-button size="small" :loading="emailTesting" @click="testEmail" style="float: right">发送测试邮件</el-button>
        </template>
        <el-form :model="emailForm" label-width="120px">
          <el-form-item label="SMTP 服务器">
            <el-input v-model="emailForm.smtp_host" placeholder="smtp.qq.com" />
          </el-form-item>
          <el-form-item label="SMTP 端口">
            <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="发件邮箱">
            <el-input v-model="emailForm.sender_email" placeholder="your@qq.com" />
          </el-form-item>
          <el-form-item label="授权码">
            <el-input v-model="emailForm.auth_code" type="password" show-password placeholder="QQ邮箱16位授权码" />
          </el-form-item>
          <el-form-item label="启用">
            <el-switch v-model="emailForm.enabled" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveEmail">保存邮件配置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi } from '@/api/settings'
import { emailApi } from '@/api/email'

const llmTesting = ref(false)
const emailTesting = ref(false)

const llmForm = reactive({
  provider: 'ollama',
  base_url: 'http://localhost:11434',
  api_key: '',
  model: 'deepseek-r1:7b',
  enabled: false,
})

const emailForm = reactive({
  smtp_host: 'smtp.qq.com',
  smtp_port: 465,
  sender_email: '',
  auth_code: '',
  enabled: false,
})

onMounted(async () => {
  try {
    const llm = await settingsApi.getLLMConfig()
    Object.assign(llmForm, { ...llm, api_key: '' })
  } catch { /* use defaults */ }

  try {
    const email = await emailApi.getConfig()
    Object.assign(emailForm, { ...email, auth_code: '' })
  } catch { /* use defaults */ }
})

async function saveLLM() {
  await settingsApi.updateLLMConfig({ ...llmForm, api_key: llmForm.api_key || undefined })
  ElMessage.success('LLM 配置已保存')
}

async function testLLM() {
  llmTesting.value = true
  try {
    const res = await settingsApi.testLLM()
    ElMessage({ type: res.code === 0 ? 'success' : 'error', message: res.message })
  } finally { llmTesting.value = false }
}

async function saveEmail() {
  await emailApi.updateConfig({ ...emailForm })
  ElMessage.success('邮件配置已保存')
}

async function testEmail() {
  emailTesting.value = true
  try {
    const res = await emailApi.test()
    ElMessage({ type: res.code === 0 ? 'success' : 'error', message: res.message })
  } finally { emailTesting.value = false }
}
</script>

<style scoped>
.settings-page { height: 100vh; display: flex; flex-direction: column; }
.page-header {
  display: flex; align-items: center; padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed; height: auto;
}
.page-header h2 { margin: 0; }
.settings-content {
  flex: 1; overflow-y: auto; padding: 24px;
  display: flex; flex-direction: column; gap: 24px; max-width: 800px;
}
.config-card { }
.card-title { font-size: 16px; font-weight: 600; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/Settings.vue
git commit -m "feat: add Settings view with LLM and email configuration"
```

---

### Task 19: App layout with navigation sidebar

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Update `frontend/src/App.vue` with layout**

```vue
<template>
  <el-container class="app-container">
    <el-aside width="64px" class="app-sidebar">
      <div class="nav-items">
        <router-link to="/tasks" class="nav-item" :class="{ active: $route.path.startsWith('/tasks') }">
          <el-icon :size="22"><List /></el-icon>
          <span class="nav-label">任务</span>
        </router-link>
        <router-link to="/calendar" class="nav-item" :class="{ active: $route.path === '/calendar' }">
          <el-icon :size="22"><Calendar /></el-icon>
          <span class="nav-label">日历</span>
        </router-link>
        <router-link to="/ai-chat" class="nav-item" :class="{ active: $route.path === '/ai-chat' }">
          <el-icon :size="22"><ChatDotRound /></el-icon>
          <span class="nav-label">AI</span>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
          <el-icon :size="22"><Setting /></el-icon>
          <span class="nav-label">设置</span>
        </router-link>
      </div>
    </el-aside>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { List, Calendar, ChatDotRound, Setting } from '@element-plus/icons-vue'
</script>

<style>
body { margin: 0; }
#app { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }
</style>

<style scoped>
.app-container { height: 100vh; }
.app-sidebar {
  background: #2c2c2c; display: flex; flex-direction: column;
  align-items: center; padding-top: 16px;
}
.nav-items { display: flex; flex-direction: column; gap: 8px; }
.nav-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 10px 0; width: 64px; color: #999; text-decoration: none;
  border-radius: 8px; transition: background 0.2s;
}
.nav-item:hover { background: #3a3a3a; color: #fff; }
.nav-item.active { color: #409eff; background: #3a3a3a; }
.nav-label { font-size: 10px; }
.app-main { padding: 0; overflow: hidden; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: add sidebar navigation layout"
```

---

### Task 20: End-to-end verification

- [ ] **Step 1: Start backend**

```bash
cd backend && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- [ ] **Step 2: Start frontend (separate terminal)**

```bash
cd frontend && npm run dev
```

- [ ] **Step 3: Verify full flow**

1. Open `http://localhost:5173` — should show task board with sidebar
2. Create a task via "创建任务" button → fill form → save → appears in Kanban
3. Drag a task from "待办" to "进行中" → status updates
4. Switch to Calendar view → see the task on its due date
5. Switch to week view → verify week navigation works
6. Go to Settings → configure email (optional) → test connection
7. Go to AI Chat → send a message → verify response (requires Ollama or API key)
8. Try "AI 快速创建" from task board → enter natural language description

- [ ] **Step 4: Run backend tests**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit (if any final adjustments were made)**

```bash
git add -A
git commit -m "chore: final adjustments after e2e verification"
```

---

## Summary

| Task | Component | Files |
|------|-----------|-------|
| 1 | Backend scaffolding | config, database, requirements |
| 2 | Database models | Task, Reminder, EmailConfig, LLMConfig, AIChatMessage |
| 3 | Crypto + Schemas | AES-256-GCM crypto, all Pydantic schemas |
| 4 | TaskService | CRUD business logic |
| 5 | Calendar/Email/Stats Services | Calendar queries, SMTP sender, stats |
| 6 | AI Adapters | Ollama + OpenAI adapters |
| 7 | AI Service | System prompt, chat orchestration, NL parsing |
| 8 | Tasks Router | CRUD API endpoints |
| 9 | Calendar/Email/Settings/Stats Routers | All remaining API endpoints |
| 10 | AI Router | Chat, history, NL task creation |
| 11 | Main app | FastAPI entry, CORS, APScheduler |
| 12 | Frontend scaffolding | Vue + Vite + Element Plus setup |
| 13 | Router + API + Stores | Vue Router, Axios client, Pinia stores |
| 14 | TaskBoard + Kanban + TaskCard | Kanban view with drag-drop |
| 15 | TaskForm | Create/edit dialog |
| 16 | CalendarView + Calendars | Month + week views |
| 17 | AIChat + Messages | Chat UI with task previews |
| 18 | Settings | LLM + email configuration |
| 19 | App Layout | Sidebar navigation |
| 20 | E2E Verification | Full flow test |
