# 时间规划 / 任务管理平台 — 基础功能设计文档

> 日期：2026-06-14 | 状态：已确认 | 范围：基础功能阶段

---

## 1. 项目定位

一个本地部署的任务管理与时间规划平台。基础功能阶段覆盖：任务 CRUD、看板视图、日历视图（月/周）、AI 智能助手（Ollama 本地 + 第三方 API Key 双模式）、QQ 邮箱提醒。单用户模式，无需登录。强调数据隐私、自由定制。

---

## 2. 技术架构

| 层级 | 选型 |
|------|------|
| 后端 | Python FastAPI + SQLAlchemy + APScheduler |
| 前端 | Vue 3 + Element Plus + Vite + Pinia + Axios |
| 数据库 | SQLite（起步；后续可迁移至 PostgreSQL） |
| AI 助手 | Ollama（本地）+ OpenAI 兼容 API（第三方），双模式切换 |
| 邮件 | smtplib + email（SMTP_SSL） |
| 部署 | 开发阶段手动启动，不强制 Docker |

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────┐
│                    浏览器 (localhost:5173)            │
│  ┌───────────────────────────────────────────────┐  │
│  │              Vue 3 + Element Plus              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │  │
│  │  │ 任务看板  │ │ 日历视图  │ │  AI 对话面板  │  │  │
│  │  └──────────┘ └──────────┘ └──────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │  │
│  │  │ 统计页面  │ │ 邮件配置  │ │   设置页面   │  │  │
│  │  └──────────┘ └──────────┘ └──────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
│         │  /api/* 请求  (Vite proxy)                 │
└─────────┼───────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────┐
│         ▼              FastAPI (:8000)               │
│  ┌──────────────────────────────────────────────┐   │
│  │              REST API Router                   │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                     │
│  ┌──────────────┼───────────────────────────────┐   │
│  │           Service Layer                        │   │
│  │  TaskService │ AIService │ EmailService        │   │
│  │  CalendarService │ StatsService                │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                     │
│  ┌──────────────┼───────────────────────────────┐   │
│  │           Data Layer                           │   │
│  │  SQLite (SQLAlchemy)  │  APScheduler           │   │
│  └──────────────────────────────────────────────┘   │
│                 │                                     │
│         ┌───────┴───────┐                            │
│         ▼               ▼                            │
│   ┌──────────┐   ┌──────────────┐                    │
│   │  SQLite  │   │  Ollama 服务  │ (本地 :11434)      │
│   └──────────┘   └──────────────┘                    │
└─────────────────────────────────────────────────────┘
```

### 2.2 分层约定

- **Router 层**：请求校验、序列化、响应格式化。不碰数据库。
- **Service 层**：核心业务逻辑。不依赖 HTTP 细节。
- **Data 层**：SQLAlchemy ORM 模型和数据库操作。

---

## 3. 数据模型

### 3.1 Task — 任务

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | 自增主键 |
| title | str(200) | 任务标题 |
| description | text | 详细描述（可选） |
| priority | enum | high / medium / low（🔴🟡🟢） |
| status | enum | todo / in_progress / done |
| due_date | date? | 截止日期 |
| due_time | time? | 截止时间（可选） |
| estimated_minutes | int? | 预估耗时（分钟） |
| actual_minutes | int? | 实际耗时（分钟） |
| parent_id | int? (FK→self) | 父任务 ID |
| tags | str(500) | 逗号分隔标签 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 3.2 Reminder — 提醒规则

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| task_id | int (FK→Task) | 关联任务 |
| remind_at | datetime | 提醒触发时间 |
| method | enum | email（基础阶段仅邮件） |
| sent | bool | 是否已发送，默认 false |

### 3.3 EmailConfig — 邮箱配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | 固定为 1（单行配置） |
| smtp_host | str | 如 smtp.qq.com |
| smtp_port | int | 如 465 |
| sender_email | str | 发件邮箱 |
| auth_code | str | SMTP 授权码（AES-256-GCM 加密存储） |
| enabled | bool | 是否启用 |

### 3.4 LLMConfig — 大模型配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | 固定为 1（单行配置） |
| provider | enum | ollama / openai / custom |
| base_url | str | Ollama: http://localhost:11434，OpenAI: https://api.openai.com |
| api_key | str? | Ollama 为空，第三方需填写（AES-256-GCM 加密存储） |
| model | str | 如 deepseek-r1:7b / gpt-4o |
| enabled | bool | 是否启用 |

### 3.5 AIChatMessage — AI 对话记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int (PK) | |
| role | enum | user / assistant |
| content | text | 消息内容 |
| created_at | datetime | |

### 3.6 实体关系

```
Task ──1:N──> Reminder
Task ──1:N──> Task (自引用，parent_id)
EmailConfig (单行)
LLMConfig (单行)
AIChatMessage (多行，按时间排序)
```

---

## 4. API 设计

所有响应统一格式：

```json
{ "code": 0, "data": {...}, "message": "ok" }
```

### 4.1 Tasks

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/tasks` | 任务列表（可选过滤：`?status=&priority=&due_before=&due_after=&tag=&search=`） |
| `POST` | `/api/tasks` | 创建任务 |
| `GET` | `/api/tasks/{id}` | 任务详情（含子任务列表） |
| `PUT` | `/api/tasks/{id}` | 更新任务 |
| `DELETE` | `/api/tasks/{id}` | 删除任务（级联删除子任务和关联提醒） |
| `PATCH` | `/api/tasks/{id}/status` | 快速切换状态 `{"status": "done"}` |

### 4.2 Calendar

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/calendar?year=&month=` | 获取某月所有有任务的日期及其任务列表 |
| `GET` | `/api/calendar/week?start=&end=` | 获取某周任务 |

### 4.3 AI

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/ai/chat` | 发送对话消息，返回 AI 回复 |
| `GET` | `/api/ai/history` | 获取对话历史 |
| `DELETE` | `/api/ai/history` | 清空对话历史 |
| `POST` | `/api/ai/create-task` | AI 解析自然语言 → 返回任务预览（不入库） |

### 4.4 Email

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/email/config` | 获取邮件配置（auth_code 脱敏） |
| `PUT` | `/api/email/config` | 更新邮件配置 |
| `POST` | `/api/email/test` | 发送测试邮件 |
| `GET` | `/api/reminders` | 某任务的提醒列表 |
| `POST` | `/api/reminders` | 创建提醒规则 |
| `DELETE` | `/api/reminders/{id}` | 删除提醒规则 |

### 4.5 Settings

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/settings/llm` | 获取 LLM 配置 |
| `PUT` | `/api/settings/llm` | 更新 LLM 配置 |
| `POST` | `/api/settings/llm/test` | 测试 LLM 连接 |

### 4.6 Stats

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/stats/overview` | 总任务数、完成率、平均耗时 |
| `GET` | `/api/stats/weekly` | 近 4 周每周完成趋势 |

---

## 5. 前端页面与路由

### 5.1 路由结构

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | — | 重定向到 `/tasks` |
| `/tasks` | 任务看板 | 主页面，三列 Kanban |
| `/tasks/:id` | 任务详情 | 侧边抽屉或对话框 |
| `/calendar` | 日历视图 | 月/周切换 |
| `/ai-chat` | AI 对话 | 对话面板 |
| `/settings` | 设置 | LLM + 邮件配置 |

### 5.2 页面说明

**任务看板 (`/tasks`)**

- 三列看板（待办 / 进行中 / 已完成），支持拖拽切换状态
- 顶部搜索栏：关键词 + 标签过滤
- 「AI 快速创建」按钮：唤起输入框，自然语言 → 任务预览 → 确认创建
- 每个任务卡片显示：标题、优先级色标、截止日期、子任务数、标签

**日历视图 (`/calendar`)**

- 月/周切换按钮
- 月视图：标准月历网格，有任务日期显示优先级色点，点击日期展开任务列表
- 周视图：7 列时间轴，任务按时间块纵向排列

**AI 对话 (`/ai-chat`)**

- 左侧对话历史，右侧聊天窗口
- AI 回复中的 ` ```task ` 代码块解析为任务卡片，带「添加到待办」按钮
- 顶部显示当前模型名称和连接状态指示

**设置页 (`/settings`)**

- LLM 配置卡片：Provider 选择（Ollama / OpenAI / 自定义）、base_url、api_key、model、测试连接按钮
- 邮件配置卡片：SMTP 信息、测试发送按钮

---

## 6. AI 服务设计

### 6.1 双模式适配器

```
                    ┌─────────────┐
                    │  AIService   │
                    │  (统一接口)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Ollama   │ │ OpenAI   │ │ Custom   │
        │ Adapter  │ │ Adapter  │ │ Adapter  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
             ▼             ▼             ▼
     /api/generate   /chat/completions  用户自定义 URL
```

`AIService` 为统一抽象类，定义 `chat(messages, stream)` 和 `health_check()` 接口。三个 Adapter 各自实现。运行时根据 `LLMConfig.provider` 选择适配器，切换 Provider 无需修改业务代码。

### 6.2 系统提示词

每次对话请求动态注入时间上下文和当前任务数据：

```text
# 时间上下文
今天是 {YYYY-MM-DD}，{星期X}。

# 任务管理准则
- 优先级：🔴高（今天必须完成） > 🟡中（本周完成） > 🟢低
- 任务分解：超过4小时的任务须拆为≤2小时的子任务
- 时间估算：默认每任务45分钟，基于历史数据微调

# 任务拆解规范
- 标题：动词+名词，≤15字
- 预估耗时：精确到15分钟
- 超过2小时的主任务必须分解子任务

# 交互风格
- 称呼用户"你"，以助理口吻对话
- 回复默认 Markdown 格式
- 生成任务后主动询问："需要我将这些任务添加到待办列表吗？"

# 当前任务数据
待办任务：{tasks_json}
```

### 6.3 对话 → 任务创建流程

```
用户输入 "明天下午3点和王经理开会讨论Q3预算"
        │
        ▼
   AIService.chat()  ← 系统提示词 + 对话历史 + 用户输入
        │
        ▼
   AI 回复（Markdown），包含 ```task JSON 代码块
   格式：
   ```task
   {"title": "和产品对齐需求", "priority": "中", "estimated_minutes": 45, "due_date": "2026-06-16"}
   ```
        │
        ▼
   前端解析 ```task → 渲染任务卡片组件
   卡片上有 [添加到待办] 按钮
        │
        ▼
   用户点击 → POST /api/tasks → 任务入库
```

---

## 7. 邮件提醒服务

### 7.1 架构

```
┌─────────────────────────────────────┐
│          APScheduler (后台线程)       │
│  每 60 秒扫描 Reminder 表            │
│  remind_at <= now AND sent = false  │
│         │                           │
│         ▼                           │
│  EmailService.send()                │
│         │                           │
│         ▼                           │
│  smtplib.SMTP_SSL → QQ邮箱 SMTP     │
│         │                           │
│         ▼                           │
│  标记 sent = true                   │
└─────────────────────────────────────┘
```

### 7.2 设计要点

- **调度器**：APScheduler，FastAPI 启动时自动拉起后台线程，零额外依赖。
- **扫描间隔**：60 秒，`settings.py` 中可配置。
- **失败重试**：发送失败不标记 `sent=true`，下次扫描自动重试。每个提醒独立计数，连续失败 3 次后放弃并在日志告警。
- **auth_code 安全**：AES-256-GCM 加密存储，密钥从环境变量 `SECRET_KEY` 读取。API 返回时脱敏显示（`****xxxx`）。
- **限额感知**：QQ 邮箱日限约 100 封，发送前检查当日计数，超限时前端提示。

### 7.3 提醒创建方式

- 用户手动：任务详情中选"提前 30 分钟"/"提前 1 小时"/自定义时间
- AI 建议：对话中 AI 建议提醒策略，用户确认后自动创建

---

## 8. 项目结构

```
time-management/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口，启动 APScheduler
│   │   ├── config.py            # 配置（数据库 URL、SECRET_KEY 等）
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── task.py
│   │   │   ├── reminder.py
│   │   │   ├── email_config.py
│   │   │   ├── llm_config.py
│   │   │   └── ai_message.py
│   │   ├── routers/             # API 路由
│   │   │   ├── tasks.py
│   │   │   ├── calendar.py
│   │   │   ├── ai.py
│   │   │   ├── email.py
│   │   │   ├── settings.py
│   │   │   └── stats.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── task_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── email_service.py
│   │   │   ├── calendar_service.py
│   │   │   └── stats_service.py
│   │   ├── adapters/            # AI 适配器
│   │   │   ├── base.py
│   │   │   ├── ollama.py
│   │   │   └── openai.py
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   └── utils/               # 工具函数（加密、日期处理等）
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── TaskBoard.vue
│   │   │   ├── CalendarView.vue
│   │   │   ├── AIChat.vue
│   │   │   └── Settings.vue
│   │   ├── components/          # 可复用组件
│   │   │   ├── TaskCard.vue
│   │   │   ├── TaskForm.vue
│   │   │   ├── KanbanColumn.vue
│   │   │   ├── MonthCalendar.vue
│   │   │   ├── WeekCalendar.vue
│   │   │   ├── ChatMessage.vue
│   │   │   └── TaskPreviewCard.vue
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── api/                 # Axios 封装
│   │   ├── router/              # Vue Router
│   │   └── App.vue
│   ├── vite.config.ts
│   └── package.json
├── docs/superpowers/specs/      # 设计文档
└── 项目说明.md                   # 原始项目说明（初稿）
```

---

## 9. 非功能需求

### 9.1 性能

- API 响应时间 ≤ 200ms（不含 AI 调用）
- AI 对话采用流式返回（SSE），首字延迟 ≤ 3s
- SQLite 在 10000 条任务以下无需优化

### 9.2 安全

- SMTP auth_code AES 加密存储
- 第三方 API Key AES 加密存储
- SECRET_KEY 从环境变量读取，提供 `.env.example` 模板
- 无用户认证阶段，前端仅限本机访问（localhost）

### 9.3 可维护性

- 后端分层清晰（Router → Service → Data）
- AI 适配器模式便于新增 Provider
- 前端组件粒度合理，每个组件职责单一
- API 统一响应格式

---

## 10. 不在本期范围

以下功能明确推迟到后续阶段：

- 番茄钟 / 专注模式（第二阶段）
- 数据统计图表 / 效率热力图（第二阶段）
- 任务委派 / 共享任务板（第三阶段）
- IFTTT 规则引擎 / Webhook / CLI（第四阶段）
- PWA / 响应式移动端（第五阶段）
- 教务系统课表导入
- Docker 容器化部署
- 用户认证与多用户
```

---

## 11. 变更记录

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-06-14 | 初稿 | 基于项目说明初稿完成基础功能设计 |
