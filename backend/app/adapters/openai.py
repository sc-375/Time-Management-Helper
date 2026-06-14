"""OpenAI-compatible adapter using /chat/completions endpoint."""
import httpx
from .base import BaseAdapter


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
