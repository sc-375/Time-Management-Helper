"""AI service that orchestrates LLM adapters with system prompt."""
import re
import json
import logging
from sqlalchemy.orm import Session
from ..models.llm_config import LLMConfig
from ..models.ai_message import AIChatMessage, MessageRole
from ..adapters.ollama import OllamaAdapter
from ..adapters.openai import OpenAIAdapter
from ..utils.system_prompt import build_system_prompt
from ..utils.crypto import decrypt

logger = logging.getLogger(__name__)


class AIService:

    def _get_adapter(self, db: Session):
        config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
        if not config or not config.enabled:
            raise ValueError("AI 服务未配置或未启用")

        api_key = None
        if config.api_key:
            api_key = decrypt(config.api_key) or config.api_key

        provider_str = config.provider.value if hasattr(config.provider, "value") else config.provider

        if provider_str == "ollama":
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
        messages = [{"role": m.role.value if hasattr(m.role, "value") else m.role, "content": m.content} for m in history]

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
        previews = []
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
        from datetime import date as dt_date
        adapter = self._get_adapter(db)
        today = dt_date.today()
        prompt = f"""今天是 {today.isoformat()}。请将以下用户输入拆解为独立任务，返回 JSON 数组。

用户输入：{text}

要求：
1. 每个活动生成一条任务，不要把一个活动拆成多条
2. title 用动词+名词格式，≤15字
3. priority: 用户明确说了"高"/"优先"用 high，否则 medium
4. estimated_minutes: 有明确时间的按实际时长，否则默认 45
5. due_date: 用 YYYY-MM-DD 格式。明天={today}的第二天。没提到日期的填 null

只返回 JSON 数组。"""

        try:
            raw = adapter.chat([{"role": "user", "content": prompt}], "你是任务解析助手。只输出 JSON。")
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
