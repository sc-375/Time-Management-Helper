"""Common response schema."""
from typing import Any
from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int = 0
    data: Any = None
    message: str = "ok"


def success(data: Any = None, message: str = "ok") -> APIResponse:
    return APIResponse(code=0, data=data, message=message)


def error(message: str, code: int = 1) -> APIResponse:
    return APIResponse(code=code, data=None, message=message)
