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
    auth_code: str
    enabled: bool

    class Config:
        from_attributes = True
