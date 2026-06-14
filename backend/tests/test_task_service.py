"""Tests for TaskService."""
"""Tests for TaskService."""
import os
import sys
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Setup test database
os.environ["SECRET_KEY"] = "test-key-32-chars-long!!!!!!"
os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base
from app.models import Task, Reminder, EmailConfig, LLMConfig, AIChatMessage
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    session = TestSession()
    yield session
    session.close()
    # Clean up all data between tests to ensure isolation
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
        conn.execute(text("PRAGMA foreign_keys = ON"))


@pytest.fixture
def svc():
    return TaskService()


def _enum_val(field):
    """Extract plain string from an enum field, passing through plain strings."""
    return field.value if hasattr(field, "value") else field


def test_create_task_sets_defaults(db, svc):
    data = TaskCreate(title="Test task")
    task = svc.create(db, data)
    assert task.id is not None
    assert task.title == "Test task"
    assert _enum_val(task.priority) == "medium"
    assert _enum_val(task.status) == "todo"


def test_list_tasks_returns_all(db, svc):
    svc.create(db, TaskCreate(title="Task 1"))
    svc.create(db, TaskCreate(title="Task 2"))
    tasks = svc.list_tasks(db)
    assert len(tasks) == 2


def test_list_tasks_filters_by_status(db, svc):
    svc.create(db, TaskCreate(title="Todo task", status="todo"))
    svc.create(db, TaskCreate(title="Done task", status="done"))
    tasks = svc.list_tasks(db, status="done")
    assert len(tasks) == 1
    assert tasks[0].title == "Done task"


def test_get_task_returns_correct(db, svc):
    t = svc.create(db, TaskCreate(title="Find me"))
    found = svc.get_task(db, t.id)
    assert found is not None
    assert found.title == "Find me"


def test_get_task_nonexistent(db, svc):
    assert svc.get_task(db, 999) is None


def test_update_task(db, svc):
    t = svc.create(db, TaskCreate(title="Original"))
    updated = svc.update(db, t.id, TaskUpdate(title="Updated"))
    assert updated.title == "Updated"


def test_update_nonexistent(db, svc):
    assert svc.update(db, 999, TaskUpdate(title="X")) is None


def test_delete_task(db, svc):
    t = svc.create(db, TaskCreate(title="Delete me"))
    assert svc.delete(db, t.id) is True
    assert svc.get_task(db, t.id) is None


def test_delete_nonexistent(db, svc):
    assert svc.delete(db, 999) is False


def test_update_status(db, svc):
    t = svc.create(db, TaskCreate(title="Status test"))
    updated = svc.update_status(db, t.id, "done")
    assert _enum_val(updated.status) == "done"
