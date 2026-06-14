"""Build system prompt with dynamic context injection."""
from datetime import date
import json
from sqlalchemy.orm import Session
from ..models.task import Task

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]


def build_system_prompt(db: Session) -> str:
    today = date.today()
    weekday = WEEKDAYS[today.weekday()]
    tasks = db.query(Task).filter(Task.status != "done").order_by(Task.priority).all()
    tasks_json = json.dumps(
        [{"id": t.id, "title": t.title, "priority": t.priority.value if hasattr(t.priority, "value") else t.priority,
          "due_date": str(t.due_date) if t.due_date else None} for t in tasks],
        ensure_ascii=False,
    )

    return f"""# 时间上下文
今天是 {today.isoformat()}，星期{weekday}。

# 当前任务数据
待办任务：{tasks_json}

# 任务管理准则
- 优先级：🔴高（今天必须完成） > 🟡中（本周完成） > 🟢低
- 任务分解：超过4小时的任务须拆为≤2小时的子任务
- 时间估算：默认每任务45分钟

# 交互风格
- 称呼用户"你"，以助理口吻对话
- 回复时用自然语言列出任务建议即可，系统会自动提取
- 生成任务后主动询问："需要我将这些任务添加到待办列表吗？" """
