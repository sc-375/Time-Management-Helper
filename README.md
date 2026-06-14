# Time Management Platform

本地部署的任务管理与时间规划平台。看板、日历、AI 助手、邮件提醒。

## 技术栈

- **后端**：Python FastAPI + SQLAlchemy + SQLite + APScheduler
- **前端**：Vue 3 + Element Plus + Vite + Pinia
- **AI**：Ollama 本地推理 / OpenAI 兼容 API
- **邮件**：SMTP（QQ 邮箱等）

## 快速开始

### 环境要求

- Python ≥ 3.11
- Node.js ≥ 18
- （可选）Ollama — 用于本地 AI 助手

### 1. 克隆项目

```bash
git clone https://github.com/sc-375/Time-Management-Helper.git
cd Time-Management-Helper
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，将 SECRET_KEY 改为随机字符串（至少 32 位）
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端运行在 http://localhost:8000，API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

### 4. 配置 AI 助手（可选）

**方案 A — Ollama 本地**（免费，数据不出本地）：

```bash
# 安装 Ollama：https://ollama.com
ollama pull deepseek-r1:7b   # 或其他模型如 qwen2.5:7b、llama3:8b
ollama serve                  # 启动服务（默认端口 11434）
```

然后在设置页面选择「Ollama (本地)」，Base URL 保持 `http://localhost:11434`，填入模型名，启用。

**方案 B — 第三方 API**：

在设置页面选择「OpenAI」或「自定义」，填入 API Key 和 Base URL。

### 5. 配置邮件提醒（可选）

以 QQ 邮箱为例：

1. 登录 mail.qq.com → 设置 → 帐户
2. 找到「POP3/IMAP/SMTP 服务」，开启「IMAP/SMTP 服务」
3. 发送短信验证后获取 16 位授权码
4. 在设置页面填入 SMTP 信息并保存

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 环境变量配置
│   │   ├── database.py      # SQLAlchemy 引擎
│   │   ├── models/          # 数据模型
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── adapters/        # AI 适配器（Ollama / OpenAI）
│   │   └── utils/           # 工具函数
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── views/           # 页面组件
│       ├── components/      # 可复用组件
│       ├── api/             # API 客户端
│       ├── stores/          # Pinia 状态
│       ├── router/          # Vue Router
│       └── styles/          # 设计系统
└── .gitignore
```

## 功能

- 任务看板（三列 Kanban + 拖拽）
- 日历视图（月 / 周）
- AI 对话助手（自然语言创建任务、智能拆解）
- 邮件提醒（SMTP + 定时扫描）
- 暗色侧边栏导航、时间感知光条
