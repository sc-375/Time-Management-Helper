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
    api_key: Optional[str]
    model: str
    enabled: bool

    class Config:
        from_attributes = True
