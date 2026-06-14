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

# 任务输出格式（重要！）
当你要向用户建议创建任务时，必须使用以下格式包裹每个任务：
```task
{{"title": "任务标题", "priority": "high|medium|low", "estimated_minutes": 45, "due_date": "YYYY-MM-DD"}}
```
示例：
```task
{{"title": "开项目启动会", "priority": "high", "estimated_minutes": 60, "due_date": "2026-06-16"}}
```
每个任务单独一个 ```task 代码块。先给出 Markdown 格式的文字说明，再用 ```task 块列出任务。

# 任务管理准则
- 优先级：🔴高（今天必须完成） > 🟡中（本周完成） > 🟢低
- 任务分解：超过4小时的任务须拆为≤2小时的子任务
- 时间估算：默认每任务45分钟

# 交互风格
- 称呼用户"你"，以助理口吻对话
- 回复默认 Markdown 格式
- 生成任务后主动询问："需要我将这些任务添加到待办列表吗？"
- 先给文字说明，再把可创建的任务用 ```task JSON 格式列出"""
