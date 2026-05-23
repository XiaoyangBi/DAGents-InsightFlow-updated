# DAGents-InsightFlow

AI 驱动的竞品分析多 Agent 协作系统。

## 技术栈
- 后端：FastAPI + LangGraph + 异步 PostgreSQL
- 前端：Next.js + Tailwind CSS

## 环境要求
- Python 3.11+
- PostgreSQL 14+

## 后端启动步骤
1. 进入 backend 目录
```bash
cd backend
```

2. 创建虚拟环境并激活
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install -e .
```

4. 确认配置文件 `.env` 已正确填写：
```
DATABASE_URL=postgresql+asyncpg://postgres:xxx@127.0.0.1:5432/dagents
LLM_API_KEY=你的火山方舟APIKey
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/
LLM_MODEL=你的模型接入点ID
TAVILY_API_KEY=你的Tavily APIKey
```

5. 在 PostgreSQL 中提前创建好 dagents 数据库：
```sql
CREATE DATABASE dagents;
```

6. 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. 访问自动生成的 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 运行测试
```bash
cd backend
pip install pytest pytest-asyncio httpx aiosqlite
python -m pytest -v
```

## 项目目录结构
```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理（pydantic-settings）
│   ├── dependencies.py      # 依赖注入（用户认证等）
│   ├── api/v1/
│   │   ├── auth.py           # 用户认证接口
│   │   ├── workflow.py       # 工作流 CRUD 接口
│   │   ├── interview.py      # 访谈 SSE 流式接口
│   │   └── router.py         # 路由聚合
│   ├── agents/
│   │   └── interview_agent.py # 访谈 Agent（LangChain + Tavily）
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── workflow.py       # WorkflowConfig / WorkflowStatus
│   │   ├── interview.py
│   │   ├── common.py
│   │   ├── competitor.py
│   │   ├── feature.py
│   │   ├── pricing.py
│   │   ├── sentiment.py
│   │   ├── swot.py
│   │   ├── report.py
│   │   ├── review.py
│   │   ├── event.py
│   │   └── workflow_state.py # LangGraph State 定义
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── workflow_service.py
│   │   └── interview_service.py
│   └── db/
│       ├── base.py           # SQLAlchemy Base
│       ├── session.py        # 异步会话工厂
│       └── models/
│           ├── user.py       # User ORM
│           └── workflow.py   # Workflow / InterviewMessage ORM
├── tests/
│   ├── conftest.py           # 测试夹具（SQLite 内存 DB）
│   └── test_api/
│       ├── test_auth.py
│       ├── test_workflow.py
│       └── test_interview.py
└── .env                      # 环境变量配置
```

## 已实现接口
### Auth 认证模块
- `POST /api/v1/auth/register` 用户注册
- `POST /api/v1/auth/login` 用户登录
- `GET /api/v1/auth/me` 获取当前用户信息

### Workflow 工作流模块
- `POST /api/v1/workflows?title=xxx` 创建新的竞品分析工作流
- `GET /api/v1/workflows` 获取当前用户的所有工作流列表
- `GET /api/v1/workflows/{id}` 获取单个工作流详情

### Interview 用户访谈模块
- `GET /api/v1/workflows/{workflow_id}/interview/history` 获取指定工作流的访谈历史对话记录
- `POST /api/v1/workflows/{workflow_id}/interview/stream` SSE 流式用户访谈对话
