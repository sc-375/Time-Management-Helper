"""Email configuration model (single-row table)."""
from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class EmailConfig(Base):
    __tablename__ = "email_config"

    id = Column(Integer, primary_key=True, default=1)
    smtp_host = Column(String(200), default="smtp.qq.com", nullable=False)
    smtp_port = Column(Integer, default=465, nullable=False)
    sender_email = Column(String(200), default="", nullable=False)
    auth_code = Column(String(500), default="", nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
