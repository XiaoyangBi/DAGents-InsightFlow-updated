```
DAGents-InsightFlow/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                         # FastAPI 入口，注册路由 + CORS
│   │   ├── config.py                       # pydantic-settings 全局配置
│   │   ├── dependencies.py                 # 全局依赖（DB session、current_user）
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py               # v1 路由聚合
│   │   │       ├── auth.py                 # POST register / login
│   │   │       ├── workflow.py             # CRUD + start + retry
│   │   │       ├── interview.py            # POST interview / confirm
│   │   │       ├── event.py                # GET events（分页+筛选）
│   │   │       ├── artifact.py             # GET artifacts / download
│   │   │       └── trace.py                # GET trace links
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py             # LangGraph StateGraph 编译 + 路由逻辑
│   │   │   ├── graph_nodes.py              # DAG 节点函数定义
│   │   │   ├── workflow_executor.py        # Celery 异步任务（启动 DAG）
│   │   │   ├── memory_manager.py           # ContextManager 工具
│   │   │   └── node_executor.py            # 节点级重试 + 超时包装
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py               # Agent 基类（event logging 工具等）
│   │   │   ├── interview_agent.py          # pre-workflow 多轮对话
│   │   │   ├── collection_agent.py         # Tavily 搜索 + 页面提取
│   │   │   ├── analysis_agent.py           # 功能矩阵/定价/情感/SWOT
│   │   │   ├── report_agent.py             # 报告模板渲染 + 内联引用
│   │   │   └── review_agent.py             # 四维审查 + 评分公式
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── workflow_state.py           # WorkflowState TypedDict
│   │   │   ├── config.py                   # WorkflowConfig、InterviewInput/Output
│   │   │   ├── competitor.py               # CompetitorInfo、SearchResult
│   │   │   ├── feature.py                  # FeatureMatrix、FeatureItem
│   │   │   ├── pricing.py                  # PricingComparison、PricingPlan
│   │   │   ├── sentiment.py                # UserSentimentAnalysis、Sentiment
│   │   │   ├── swot.py                     # SWOTAnalysis、SWOTItem
│   │   │   ├── report.py                   # ReportOutput、ReportSection、Citation
│   │   │   ├── review.py                   # ReviewOutput、ReviewCheck
│   │   │   ├── event.py                    # EventType、EventPayload 各结构
│   │   │   └── common.py                   # SourceRef、ErrorRecord、CompressedSummary
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                     # SQLAlchemy declarative base
│   │   │   ├── session.py                  # 同步/异步 session 管理
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── workflow.py
│   │   │   │   ├── workflow_node_state.py
│   │   │   │   ├── workflow_event.py
│   │   │   │   ├── artifact.py
│   │   │   │   ├── trace_link.py
│   │   │   │   └── search_template.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── user_repo.py
│   │   │       ├── workflow_repo.py
│   │   │       ├── event_repo.py
│   │   │       ├── artifact_repo.py
│   │   │       └── trace_repo.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py             # JWT 签发/验证
│   │   │   ├── interview_service.py        # 多轮对话维护 + config 提取
│   │   │   ├── search_service.py           # Tavily 搜索封装 + 模板匹配
│   │   │   └── sse_service.py              # SSE 事件推送
│   │   │
│   │   └── tasks/                          # Celery 任务
│   │       ├── __init__.py
│   │       ├── celery_app.py               # Celery 实例
│   │       └── workflow_tasks.py           # run_workflow.delay()
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_agents/
│   │   │   ├── test_collection_agent.py
│   │   │   ├── test_analysis_agent.py
│   │   │   ├── test_report_agent.py
│   │   │   └── test_review_agent.py
│   │   ├── test_api/
│   │   │   ├── test_auth.py
│   │   │   ├── test_workflow.py
│   │   │   └── test_interview.py
│   │   ├── test_db/
│   │   │   └── test_repositories.py
│   │   └── test_e2e/
│   │       └── test_full_workflow.py
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                      # 根布局（Provider 包裹）
│   │   ├── page.tsx                        # / → redirect to /dashboard
│   │   │
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── page.tsx                    # 工作流列表（卡片+搜索+分页）
│   │   │   └── loading.tsx
│   │   │
│   │   └── workflows/
│   │       └── [id]/
│   │           ├── page.tsx                # 工作流详情主页（Tabs 容器）
│   │           ├── interview/page.tsx      # 用户访谈聊天页
│   │           ├── report/page.tsx         # 报告展示页
│   │           ├── trace/page.tsx          # 溯源视图页
│   │           └── events/page.tsx         # 事件日志页
│   │
│   ├── components/
│   │   ├── ui/                             # 通用 UI 组件（shadcn/ui 风格）
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── modal.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── spinner.tsx
│   │   │   └── toast.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   ├── register-form.tsx
│   │   │   └── auth-guard.tsx              # 未登录重定向
│   │   │
│   │   ├── dashboard/
│   │   │   ├── workflow-card.tsx           # 列表卡片
│   │   │   ├── workflow-list.tsx
│   │   │   ├── create-workflow-button.tsx
│   │   │   └── filter-bar.tsx              # 按状态/日期筛选
│   │   │
│   │   ├── interview/
│   │   │   ├── chat-message.tsx            # 气泡消息
│   │   │   ├── message-input.tsx
│   │   │   ├── config-preview.tsx          # 确认卡片
│   │   │   └── chat-history.tsx
│   │   │
│   │   ├── workflow/
│   │   │   ├── progress-timeline.tsx       # 时间线组件
│   │   │   ├── phase-badge.tsx             # 阶段标签（状态色）
│   │   │   ├── phase-progress.tsx          # 四阶段进度条
│   │   │   ├── iteration-badge.tsx         # 打回次数标记
│   │   │   └── workflow-header.tsx         # 标题+状态+操作按钮
│   │   │
│   │   ├── report/
│   │   │   ├── report-viewer.tsx           # Markdown 渲染
│   │   │   ├── report-section.tsx          # 单个章节
│   │   │   ├── citation-list.tsx           # 参考文献列表
│   │   │   ├── feature-matrix-table.tsx    # 功能对比表格
│   │   │   ├── pricing-table.tsx           # 定价对比
│   │   │   ├── swot-card.tsx               # SWOT 四象限卡片
│   │   │   └── executive-summary.tsx
│   │   │
│   │   ├── trace/
│   │   │   ├── trace-list.tsx              # 溯源条目列表
│   │   │   ├── trace-item.tsx              # 单条：断言 → source
│   │   │   ├── source-link.tsx             # 外部链接（置信度标记）
│   │   │   └── claim-verification-badge.tsx
│   │   │
│   │   ├── events/
│   │   │   ├── event-log.tsx               # 事件日志表格
│   │   │   ├── event-item.tsx              # 单行事件
│   │   │   ├── event-filter.tsx            # 按类型/节点筛选
│   │   │   └── event-detail-drawer.tsx     # 展开 payload
│   │   │
│   │   └── shared/
│   │       ├── error-boundary.tsx
│   │       ├── empty-state.tsx
│   │       ├── pagination.tsx
│   │       ├── page-header.tsx
│   │       ├── sse-listener.tsx            # SSE 连接管理 hook
│   │       └── theme-toggle.tsx
│   │
│   ├── lib/
│   │   ├── api.ts                          # axios 实例 + 拦截器（JWT）
│   │   ├── auth-context.tsx                # React Context: user + token
│   │   ├── use-workflow.ts                 # React Query hooks
│   │   ├── use-events.ts
│   │   ├── use-artifacts.ts
│   │   ├── use-interview.ts
│   │   ├── use-sse.ts                      # SSE 连接 hook
│   │   └── utils.ts                        # 格式化日期、状态颜色映射等
│   │
│   ├── types/
│   │   ├── workflow.ts                     # Workflow, WorkflowConfig, PhaseStatus
│   │   ├── artifact.ts                     # Artifact, ReportOutput, FeatureMatrix etc.
│   │   ├── event.ts                        # WorkflowEvent, EventType
│   │   ├── trace.ts                        # TraceLink, Source
│   │   ├── interview.ts                    # InterviewMessage, InterviewConfig
│   │   └── api.ts                          # ApiResponse<T>, PaginatedResponse<T>
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── styles/
│   │   ├── globals.css                     # Tailwind 指令 + 自定义变量
│   │   └── markdown.css                    # report Markdown 渲染样式
│   │
│   ├── .env.local.example
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── docker-compose.yml                      # PostgreSQL
├── .gitignore
├── CLAUDE.md
├── plan.md
├── notice.md
└── README.md
```