"""LLM configuration model (single-row table)."""
import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean
from ..database import Base


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
