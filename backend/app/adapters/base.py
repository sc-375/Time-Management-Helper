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
