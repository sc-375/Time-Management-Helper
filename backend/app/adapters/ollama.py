"""Ollama adapter using the /api/generate endpoint."""
import httpx
from .base import BaseAdapter


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
