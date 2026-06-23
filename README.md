# DAGents-InsightFlow

AI 驱动的竞品分析多 Agent 协作系统。通过 LangGraph 编排多个专业 Agent，自动完成信息采集、多维分析、报告撰写和质量审查的完整竞品分析流程。

## 近期更新

- 统一了 `core/runtime/` 运行时抽象，工作流支持 `run / recover / resume`，并具备暂停、人工决策、回跳重试能力。
- 将原来的 4 段式 DAG 拆成更细粒度的研究流水线，覆盖采集、综合分析、功能、定价、情感、定位、角色、GTM、报告与审查。
- 新增 `ContextAssembler` 与 V2 上下文装配链路，在节点执行前统一注入 `memory_context`、`rag_context` 与 `context_trace`。
- 前端已从“占位页面”升级为可用的研究工作台，包含 Dashboard、Settings、Workflow Studio、访谈面板、节点过程流与报告展示。
- 报告生成改为证据驱动的分批写作流程，部分缺源时不再直接退回兜底模板，整体可用性和稳定性更高。

## 一句话定位

不是告诉你竞品做了什么，而是帮助产品经理回答：

> 这对我到底有什么用？

## 这个项目适合谁

- **没思路时找参考**：想知道别人是怎么做的，并快速找到当前阶段可借鉴的较优解。
- **有方向时找证据**：已经有判断，但需要真实案例和来源来验证想法、说服团队。
- **需要落地结论时做取舍**：不想陷入信息堆积，而是希望最终输出能服务具体项目决策。

## 这个项目解决什么问题

传统竞品分析很容易停留在“信息罗列”层面：别人做了什么、有哪些功能、宣传了什么卖点。

但对产品经理来说，真正重要的不是信息本身，而是：

- 我要解决的问题是什么
- 哪些信息对解决这个问题真正有用
- 这些信息是否来自可信来源
- 对方成功或失败的原因到底是什么
- 最终能给当前项目带来什么可执行结论

因此，DAGents-InsightFlow 的目标不是生成一份“更长的竞品报告”，而是帮助用户围绕明确问题，输出可参考、可验证、可决策的分析结论。

## 产品方法论

对于产品经理来说，竞品分析的极简定义不是“别人做了什么”，而是：

1. 明确自己要解决的问题
2. 找到与问题相关的分析对象
3. 拆解对方成功与失败的原因
4. 得出对自己真正有用的结论

这个项目的目标，不是帮助用户堆积更多竞品信息，而是帮助用户回答一个更关键的问题：

> 这对我到底有什么用？

在实际工作中，竞品分析通常服务于两个核心目的：

- **找参考**：当自己没有清晰思路时，参考别人已经验证过的做法，找到当前阶段的较优解。
- **验证想法**：当自己已经有方向时，用案例和证据验证判断，既说服自己，也说服团队。

如果一份竞品分析无法回答下面五个问题，那它就是不合格的：

1. 你要解决什么问题？
2. 哪些信息对解决这个问题真正有用？
3. 你是在哪里找的信息？
4. 你的分析是主观还是客观，是表面还是本质？
5. 你的结论是什么，对这次项目有什么具体帮助？

因此，这个项目默认遵循三步竞品分析框架：

- **定义**：先定义目标问题与竞品范围，解决“分析谁”的问题。
- **拆解**：围绕目标问题，拆解竞品在产品、品牌、营销、体验等层面的关键动作与结果。
- **结论**：输出可执行的判断，明确“我们该借鉴什么、验证什么、避免什么”。

为帮助用户聚焦分析对象，项目中将竞品默认分为五类：

- **核心竞品**：与我们高度重合，是最直接的参照对象，必须深挖。
- **标杆竞品**：规模更大、影响力更强，适合学习其方法、趋势与打法。
- **潜力竞品**：规模未必占优，但在策略或执行上有亮点，值得关注。
- **替代竞品**：产品形态不同，但解决的是同一个更高层级需求。
- **避坑竞品**：反面教材，用来明确哪些事情不能做。

这也意味着，DAGents-InsightFlow 关注的重点不是“信息越多越好”，而是：

- 问题是否清晰
- 信息是否有用
- 来源是否可信
- 分析是否触及本质
- 结论是否能够指导决策

## 产品定位方法论

这个项目同样把“产品定位”视为竞品分析的前置问题。产品存在的意义，不是展示功能和参数，而是提供用户价值。

可以用一句话描述一个产品：

> 这是一个为【目标用户】，在【使用场景】下，解决【某类问题】的【产品品类】。

因此，在分析竞品之前，项目会优先尝试回答以下五个定位问题：

1. 我们的目标用户是谁，是否足够具体？
2. 他们的痛点是什么，这个痛点够不够痛？
3. 这个市场够不够大，是大众需求还是小众需求？
4. 产品能不能解决这个问题，解决得够不够好？
5. 产品有没有差异化，为什么用户要选它而不是其他方案？

围绕这个目标，项目默认用五个维度来拆解产品定位：

- **用户**：产品究竟在解决谁的问题，包括用户画像、消费偏好与潜在动因。
- **场景**：用户在什么时间、环境、情绪和社交关系中使用产品。
- **问题**：用户面临的是痛点、痒点还是爽点，问题是否真实存在。
- **解决方案**：产品如何在功能层、情绪层、社交层提供价值。
- **支撑点**：用户凭什么相信这个产品，包括技术证明、信任背书、口碑效应、设计细节与品牌势能。

项目希望通过竞品分析回答的不只是“产品长什么样”，而是：

- 它到底为谁服务
- 它在哪些场景下创造价值
- 它解决的究竟是什么问题
- 它用什么方案和支撑点建立了用户信任
- 它的定位是否真的成立

## 上市分析方法论

除了产品定位，这个项目也关注产品如何完成从 0 到 1、再到 1 到 10 的市场验证。对于竞品来说，成功往往不只来自产品本身，也来自上市和增长策略。

因此，项目在需要时会继续拆解以下问题：

- **上市节奏**：是慢热型、爆破型还是长尾型？各阶段分别做了什么？
- **预算分配**：时间、平台、内容出口和内容方向如何分配？
- **平台组合**：线上线下、各个渠道分别承担什么角色，如何配合？
- **内容策略**：它如何讲产品，用了什么概念，如何把概念落到用户感知？
- **投放动作**：是否投流，预算结构是否合理，ROI 表现如何？
- **商业结果**：最终是否成功，亮点在哪里，问题在哪里，哪些经验可复用？

这意味着，项目输出的最终目标不是机械模仿竞品，而是帮助用户看清：

- 别人为何成功或失败
- 哪些动作值得借鉴
- 哪些动作需要规避
- 我们应该如何做得更好

## 技术栈
- 后端：FastAPI + LangGraph + SQLAlchemy Async + PostgreSQL
- 前端：Next.js 16 + React 19 + Tailwind CSS 4 + React Query + React Flow
- LLM：OpenAI 兼容接口（默认接火山方舟），支持 LangChain / LangGraph 调用链
- 搜索：Tavily API
- 可观测性：LangSmith（可选）
- 上下文扩展：可插拔 Memory / Retrieval 接口，便于后续接入长期记忆与 RAG 后端

## 已实现功能

- [x] 用户注册 / 登录 / JWT 认证
- [x] Dashboard、Settings、Workflow Studio、报告页等前端界面
- [x] InterviewAgent 多轮 SSE 流式访谈，自动提取并补全 `WorkflowConfig`
- [x] 根据产品画像与问题上下文自动推荐竞品、生成竞品分组与工作流标题
- [x] 细粒度 LangGraph DAG 编排，支持多分析子节点与 review 条件回跳
- [x] 统一运行时抽象：`GraphRuntime + NodeRunner + Pause/RoutePolicy`
- [x] 工作流 `run / recover / resume / retry / cancel` 生命周期管理
- [x] 人在回路决策：支持 `jump`、`replace_competitor`、`drop_competitor`、`approve`、`abort`
- [x] 事件日志、节点快照、SSE 广播与节点过程流展示
- [x] `execution_attempt` 隔离，避免重试与恢复混入旧一轮数据
- [x] 产物存储与下载，支持结构化制品、Markdown 报告和 trace 溯源
- [x] 可插拔 Memory / Retrieval 接口与 V2 context 装配链路
- [x] ReportAgent 证据驱动写作与 ReviewAgent 质量审查
- [x] LangSmith 可选接入，支持链路追踪
- [ ] 生产级 memory / retrieval backend 仍待接入具体实现
- [ ] 更完整的部署文档与示例数据集仍待补齐

## 近期优化

- 运行时重构为统一的 `core/runtime/`，把重试、暂停、路由、事件与节点执行职责收拢到可复用抽象层。
- Review 不再是特例节点，任意允许回跳的节点都能通过统一 `RoutePolicy` 参与 reroute。
- 访谈链路改为“积攒 -> 提取配置 -> 清洗文本 -> 回放 -> META”，避免原始 JSON 泄露到聊天区，同时保证前后配置一致。
- 右侧运行面板从原始 token 流改为节点过程叙述，用户看到的是“系统正在做什么”，而不是 LLM 底层输出。
- 报告生成对“部分缺源”更稳健，只在完全无来源或关键解析失败时退回资料不足模板。
- 前端新增分析偏好设置、工作流自动恢复、失败重试与历史 attempt 对齐逻辑，长流程体验更完整。

## 核心业务流程

### 工作流生命周期

```
创建工作流 → 访谈配置 → 启动执行 → 运行/暂停/恢复 → 完成/失败/取消
  created    configuring    running    paused/running    completed/failed/cancelled
```

1. **创建**：用户创建工作流，状态进入 `created / configuring`
2. **访谈配置**：InterviewAgent 通过多轮 SSE 对话收集目标产品、核心问题、竞品范围、分析重点等信息，并生成可编辑配置
3. **确认启动**：前端可在右侧面板或设置页偏好基础上覆写配置，调用 `/start` 后进入 `running`
4. **图执行**：`GraphRuntime` 按模板推进各节点，`NodeRunner` 负责重试、状态快照、制品落库和事件广播
5. **暂停决策**：当 review 或策略判定需要人工介入时，工作流进入 `paused`，用户可通过 `/decide` 执行 jump、替换竞品、保留证据不足结果或终止
6. **恢复与重试**：服务中断可走 `/recover`，失败后可用 `/retry/{node}` 创建新的 `execution_attempt`
7. **结束**：所有节点执行完毕且审查通过后进入 `completed`；用户中止则为 `cancelled`

### DAG 工作流编排

系统使用 LangGraph StateGraph 构建细粒度研究流水线，并在每个业务节点后串联控制门节点处理 pause / reroute：

```
information_collection
  → analysis
  → feature_analysis
  → pricing_analysis
  → sentiment_analysis
  → positioning_analysis
  → role_analysis
  → gtm_analysis
  → report_writing
  → review
```

**控制流逻辑**：
- review 通过 -> 结束
- review 未通过且可自动修复 -> reroute 到指定上游节点重新执行
- review 需要人工决策 -> pause，等待 `/decide`
- 超过最大修订次数或用户放弃 -> 结束

### Agent 职责

| Agent | 节点名 | 输入 | 输出 |
|-------|--------|------|------|
| **CollectionAgent** | `information_collection` | WorkflowConfig | 各竞品原始搜索数据 `raw_data` |
| **AnalysisAgent** | `analysis` 及多个 `*_analysis` 节点 | `raw_data`、上下文摘要 | SWOT、功能矩阵、定价、情感、定位、角色、GTM 等结构化结果 |
| **ReportAgent** | `report_writing` | 各分析模块结果、引用候选 | 完整 Markdown 竞品分析报告与章节引用 |
| **ReviewAgent** | `review` | 报告内容、来源覆盖情况 | 审查结果（通过 / 回跳 / 暂停人工决策） |

> 四个业务 Agent 均已接入真实调用链。配置真实 API key 后会调用 Tavily 与 OpenAI 兼容 LLM；缺少真实 key 或外部服务失败时会保留可诊断 fallback，避免静默返回空结构。

### 工作流状态（WorkflowState）

贯穿 DAG 所有节点的共享状态：

```python
WorkflowState = {
    "config": WorkflowConfig,
    "competitors": list[CompetitorInfo],
    "memory_context": dict,
    "rag_context": dict,
    "context_trace": dict,
    "raw_data": dict[str, list],
    "collection_errors": dict[str, str],
    "feature_matrix": FeatureMatrix | None,
    "pricing_comparison": PricingComparison | None,
    "user_sentiment": UserSentimentAnalysis | None,
    "positioning_analysis": PositioningAnalysis | None,
    "gtm_analysis": GTMAnalysis | None,
    "swot": SWOTAnalysis | None,
    "report": ReportOutput | None,
    "review_result": ReviewOutput | None,
    "revision_count": int,
    "max_revisions": int,
    "current_phase": str,
    "workflow_status": str,
    "errors": list[ErrorRecord],
}
```

### 事件与可观测性

- **EventLogger**：每个事件独立写入 `workflow_event` 表并立即 commit，使用单调递增序列号 `seq`
- **节点过程流**：后端发送 `node_progress` 等用户态事件，前端按节点聚合展示执行过程
- **SSE 实时推送**：`SSEManager` 基于 `asyncio.Queue` 向所有订阅客户端广播节点执行进度
- **节点状态快照**：每次节点执行完成后保存完整 state 到 `workflow_node_state` 表，记录耗时、token 用量等指标
- **产物与溯源**：分析结果、报告、trace link 按 `execution_attempt` 维度落库与查询

### 节点重试机制

`execute_with_retry` 提供指数退避重试：
- 最多 3 次重试，每次超时 5 分钟
- 退避间隔：`2^attempt` 秒
- 每次失败记录 `NODE_ERROR` 事件
- 全部失败后抛出 `NodeFatalError`
- 工作流级 retry 会新建 `execution_attempt`，避免复用旧 checkpoint 与旧产物

## API 接口

### Auth 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录（返回 JWT） |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

### Workflow 工作流管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/workflows` | 创建工作流 |
| GET | `/api/v1/workflows` | 工作流列表 |
| GET | `/api/v1/workflows/{id}` | 工作流详情（含 config、phase、attempt、pause_state 等） |
| PATCH | `/api/v1/workflows/{id}` | 更新工作流标题 |
| POST | `/api/v1/workflows/{id}/start` | 确认配置并启动 DAG 执行 |
| POST | `/api/v1/workflows/{id}/retry/{node}` | 新建一轮 `execution_attempt` 后重跑 |
| POST | `/api/v1/workflows/{id}/recover` | 从 checkpoint 恢复运行中的工作流 |
| POST | `/api/v1/workflows/{id}/decide` | 人在回路决策（jump / replace / approve / abort） |
| POST | `/api/v1/workflows/{id}/cancel` | 手动取消当前工作流 |
| DELETE | `/api/v1/workflows/{id}` | 删除工作流（级联删除所有关联数据） |

### Interview 访谈配置
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/workflows/{id}/interview/stream` | SSE 流式访谈对话 |
| GET | `/api/v1/workflows/{id}/interview/history` | 访谈历史记录 |
| POST | `/api/v1/workflows/{id}/interview/confirm` | 确认配置（校验完整性） |

### Event 事件与监控
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/workflows/{id}/events` | 事件列表（支持按 node / event_type / attempt 筛选） |
| GET | `/api/v1/workflows/{id}/stream` | SSE 实时事件流 |
| GET | `/api/v1/workflows/{id}/states` | 节点状态快照历史（支持按 attempt 查询） |

### Artifact 产物
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/workflows/{id}/artifacts` | 产物列表 |
| GET | `/api/v1/artifacts/{id}` | 产物详情（含 content JSON） |
| GET | `/api/v1/artifacts/{id}/download` | 下载 Markdown 报告 |

### Trace 溯源
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/workflows/{id}/trace` | 溯源链接列表 |

## 项目目录结构

```
frontend/
├── app/
│   ├── dashboard/                  # 工作流总览与新建入口
│   ├── settings/                   # 分析偏好设置页
│   ├── workflows/[id]/             # Workflow Studio（访谈 / 运行 / 报告）
│   └── auth/                       # 登录 / 注册
├── components/
│   ├── interview/                  # 聊天流与配置面板
│   ├── events/                     # 节点过程流与调试面板
│   ├── report/                     # 报告渲染组件
│   └── dashboard/                  # 仪表盘卡片与布局
├── lib/
│   ├── analysis-preferences.ts     # 分析偏好持久化
│   ├── interview-insights.ts       # 访谈摘要与竞品分组提取
│   ├── use-node-stream.ts          # 节点过程流聚合
│   └── api.ts                      # 前端 API 客户端

backend/
├── app/
│   ├── main.py                     # FastAPI 应用入口
│   ├── config.py                   # 配置管理（pydantic-settings）
│   ├── dependencies.py             # 依赖注入（JWT 认证）
│   ├── api/v1/
│   │   ├── router.py               # 路由聚合
│   │   ├── auth.py                 # 认证接口
│   │   ├── workflow.py             # 工作流管理接口
│   │   ├── interview.py            # 访谈配置接口
│   │   ├── event.py                # 事件查询与 SSE 流
│   │   ├── artifact.py             # 产物查询与下载
│   │   └── trace.py                # 溯源链接
│   ├── context/
│   │   └── assembler.py            # V2 context 装配（memory / rag / trace）
│   ├── core/
│   │   ├── competitive_template.py # 竞品分析图模板
│   │   ├── pause_service.py        # 暂停生命周期管理
│   │   ├── workflow_executor.py    # run / resume / recover 入口
│   │   └── runtime/
│   │       ├── graph_runtime.py    # StateGraph 编译与控制门节点
│   │       ├── node_runner.py      # 单节点执行器
│   │       ├── retry.py            # 重试与 NodeFatalError
│   │       ├── policies.py         # pause / route 策略
│   │       └── template.py         # GraphTemplate / NodeSpec 声明
│   ├── agents/
│   │   ├── base_agent.py           # Agent 基类（事件记录 + SSE 广播）
│   │   ├── interview_agent.py      # 访谈 Agent（LangChain + Tavily）
│   │   ├── collection_agent.py     # 信息采集 Agent
│   │   ├── analysis_agent.py       # 综合分析与多分析子节点
│   │   ├── report_agent.py         # 报告撰写 Agent
│   │   └── review_agent.py         # 质量审查 Agent
│   ├── memory/
│   │   └── backend/base.py         # Memory backend 标准接口
│   ├── retrieval/
│   │   └── backend/base.py         # Retrieval backend 标准接口
│   ├── services/
│   │   ├── workflow_service.py     # 工作流 CRUD 与生命周期管理
│   │   ├── interview_service.py    # 访谈流式处理、配置清洗与 META 回放
│   │   ├── event_service.py        # EventLogger 与事件查询
│   │   ├── sse_service.py          # SSE 广播管理器
│   │   ├── task_runner.py          # 脱离请求的后台任务启动
│   │   └── auth_service.py         # 用户认证与 JWT
│   └── db/
│       ├── base.py                 # SQLAlchemy Base
│       ├── session.py              # 异步会话工厂
│       └── models/
│           ├── user.py             # User
│           ├── workflow.py         # Workflow / InterviewMessage
│           ├── workflow_run.py     # 工作流执行批次
│           ├── workflow_pause.py   # 暂停记录
│           ├── workflow_event.py   # 事件日志
│           ├── workflow_node_state.py # 节点状态快照
│           ├── artifact.py         # 分析产物
│           ├── trace_link.py       # 溯源链接
│           ├── memory_document.py  # 长期记忆文档
│           ├── rag_chunk.py        # 检索分块
│           └── search_template.py  # 搜索模板
├── tests/
│   ├── conftest.py                 # 测试夹具
│   ├── test_human_in_the_loop.py   # 暂停 / 决策 / 恢复
│   ├── test_node_progress.py       # 节点过程流
│   ├── test_report_agent.py        # 报告引用与缺源兜底
│   └── test_v2_context.py          # V2 context 装配
└── .env                            # 环境变量配置（本地自建，不要提交）
```

## 环境要求
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

## 本地启动

### 后端启动

1. 进入 backend 目录
```bash
cd backend
```

2. 创建虚拟环境并激活
```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate    # Windows
```

3. 安装依赖
```bash
pip install -e ".[test]"
```

4. 复制并填写环境变量
```bash
cp .env.example .env
```

建议至少配置以下字段：

```env
DATABASE_URL=postgresql+asyncpg://postgres:your-password@127.0.0.1:5432/dagents
DATABASE_URL_SYNC=postgresql://postgres:your-password@127.0.0.1:5432/dagents
JWT_SECRET_KEY=your-jwt-secret-key
LLM_API_KEY=your-llm-api-key
LLM_BASE_URL=your-llm-base-url
LLM_MODEL=your-llm-model-name
TAVILY_API_KEY=your-tavily-api-key
MEMORY_BACKEND=noop
RETRIEVER_BACKEND=noop
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
```

5. 在 PostgreSQL 中创建数据库并执行迁移
```sql
CREATE DATABASE dagents;
```

```bash
alembic upgrade head
```

6. 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. 访问自动生成的 API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端启动

1. 进入前端目录并安装依赖
```bash
cd frontend
npm install
```

2. 如有需要，配置前端环境变量
```bash
echo 'NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1' > .env.local
```

3. 启动前端
```bash
npm run dev
```

4. 打开页面
- http://localhost:3000

## 运行测试

后端：

```bash
cd backend
python -m pytest -v
```

前端：

```bash
cd frontend
npm run lint
```

## 数据库表结构

以下先列出核心业务表。随着最近的运行时与上下文链路升级，仓库中还新增了 `workflow_run`、`workflow_pause`、`memory_document`、`rag_chunk` 等表，用于执行批次、暂停恢复、长期记忆与 RAG 分块存储。

### user — 用户账户

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 用户唯一标识 |
| `username` | VARCHAR(64) | UNIQUE, NOT NULL | 用户名 |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt 哈希密码 |
| `display_name` | VARCHAR(128) | NULL | 显示名称 |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | 账户是否启用 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 更新时间（自动更新） |

### workflow — 工作流聚合根

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 工作流唯一标识 |
| `owner_id` | UUID | FK → user.id CASCADE, NOT NULL | 创建者 |
| `title` | VARCHAR(255) | NOT NULL | 工作流标题 |
| `status` | VARCHAR(32) | NOT NULL, DEFAULT 'created' | 状态：created / configuring / running / paused / completed / failed / cancelled |
| `current_phase` | VARCHAR(32) | NULL | 当前 DAG 阶段：collecting / analyzing / reporting / reviewing / done |
| `config` | JSON | NOT NULL, DEFAULT '{}' | 工作流配置（目标产品、竞品列表、分析维度等） |
| `revision_count` | INTEGER | NOT NULL, DEFAULT 0 | 当前修订轮次 |
| `max_revisions` | INTEGER | NOT NULL, DEFAULT 3 | 最大修订次数 |
| `total_tokens` | INTEGER | NOT NULL, DEFAULT 0 | 累计 LLM token 消耗 |
| `langgraph_checkpoint_id` | VARCHAR(128) | NULL | LangGraph checkpoint 引用 |
| `error_message` | TEXT | NULL | 失败时的错误信息 |
| `pause_state` | JSON | NULL | 暂停元数据（reason / options / paused_by_node / paused_at），checkpoint 负责 DAG state |
| `execution_attempt` | INTEGER | NOT NULL, DEFAULT 1 | 执行批次号，每次 retry 递增 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 更新时间（自动更新） |
| `completed_at` | TIMESTAMPTZ | NULL | 完成时间 |

### interview_message — 访谈消息历史

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 消息唯一标识 |
| `workflow_id` | UUID | FK → workflow.id CASCADE, NOT NULL | 所属工作流 |
| `role` | VARCHAR(16) | NOT NULL | 角色：user / assistant |
| `content` | TEXT | NOT NULL | 消息内容 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |

### workflow_event — 事件日志

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 事件唯一标识 |
| `workflow_id` | UUID | FK → workflow.id CASCADE, NOT NULL | 所属工作流 |
| `node_name` | VARCHAR(64) | NOT NULL | 产生事件的节点名 |
| `iteration` | INTEGER | NOT NULL, DEFAULT 0 | 节点迭代轮次 |
| `event_type` | VARCHAR(32) | NOT NULL | 事件类型（见 EventType 枚举） |
| `seq` | INTEGER | NOT NULL | 工作流内单调递增序列号 |
| `execution_attempt` | INTEGER | NOT NULL, DEFAULT 1 | 执行批次号 |
| `payload` | JSON | NOT NULL, DEFAULT '{}' | 事件负载数据 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |

### workflow_node_state — 节点执行快照

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 快照唯一标识 |
| `workflow_id` | UUID | FK → workflow.id CASCADE, NOT NULL | 所属工作流 |
| `node_name` | VARCHAR(64) | NOT NULL | 节点名 |
| `iteration` | INTEGER | NOT NULL, DEFAULT 0 | 节点迭代轮次 |
| `state_snapshot` | JSON | NOT NULL, DEFAULT '{}' | 执行后完整 WorkflowState 快照 |
| `artifact_ids` | JSON | NOT NULL, DEFAULT '[]' | 本次产生的产物 ID 列表 |
| `tokens_input` | INTEGER | NOT NULL, DEFAULT 0 | LLM 输入 token 数 |
| `tokens_output` | INTEGER | NOT NULL, DEFAULT 0 | LLM 输出 token 数 |
| `duration_ms` | INTEGER | NOT NULL, DEFAULT 0 | 执行耗时（毫秒） |
| `model_name` | VARCHAR(64) | NULL | 使用的 LLM 模型名 |
| `is_error` | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否为错误快照 |
| `error_message` | TEXT | NULL | 错误信息 |
| `execution_attempt` | INTEGER | NOT NULL, DEFAULT 1 | 执行批次号 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |

### artifact — 工作流产物

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 产物唯一标识 |
| `workflow_id` | UUID | FK → workflow.id CASCADE, NOT NULL | 所属工作流 |
| `artifact_type` | VARCHAR(32) | NOT NULL | 产物类型：collection_raw / feature_matrix / pricing_comparison / user_sentiment / swot_analysis / report |
| `title` | VARCHAR(255) | NOT NULL | 产物标题 |
| `content` | JSON | NOT NULL, DEFAULT '{}' | 结构化产物内容 |
| `content_text` | TEXT | NULL | 纯文本 / Markdown 内容（用于全文检索和下载） |
| `format_version` | VARCHAR(16) | NOT NULL, DEFAULT '1.0' | 内容格式版本 |
| `created_by_node` | VARCHAR(64) | NULL | 创建该产物的节点名 |
| `execution_attempt` | INTEGER | NOT NULL, DEFAULT 1 | 执行批次号 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 更新时间（自动更新） |

### trace_link — 溯源链接

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 溯源链接唯一标识 |
| `artifact_id` | UUID | FK → artifact.id CASCADE, NOT NULL | 所属产物 |
| `section_path` | VARCHAR(255) | NULL | 报告中的章节路径 |
| `claim_text` | TEXT | NULL | 被溯源的声明文本 |
| `source_url` | TEXT | NOT NULL | 来源 URL |
| `source_title` | VARCHAR(512) | NULL | 来源标题 |
| `source_snippet` | TEXT | NULL | 来源摘要片段 |
| `source_type` | VARCHAR(32) | NOT NULL, DEFAULT 'web' | 来源类型 |
| `retrieved_at` | TIMESTAMPTZ | NOT NULL | 来源检索时间 |
| `confidence` | FLOAT | NULL | 置信度评分 |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否人工验证 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |

### search_template — 搜索模板

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | UUID | PK | 模板唯一标识 |
| `category` | VARCHAR(64) | UNIQUE, NOT NULL | 产品类别 |
| `templates` | JSON | NOT NULL, DEFAULT '{}' | 搜索模板配置 |
| `description` | VARCHAR(255) | NULL | 模板描述 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 创建时间 |

## 一个跑通的工作流示例

### 用户访谈 Interview Agent

1. 登录后取得token

POST api/v1/auth/login

2. 创建工作流

POST api/v1/workflows

传入title: "分析英雄牌钢笔的竞品"

3. 进行访谈（多轮对话）

POST api/v1/workflows/{workflow_id}/interview/stream

user:
{
  "workflow_id": workflow_id,
  "user_message": "你好！帮我从价格、质量、产量和供应链三个方面分析英雄牌钢笔和其他知名厂商产品"
}

assistant:
好的，我先和你逐步确认本次竞品分析的相关信息：
首先我初步判断你要分析的目标产品是英雄牌钢笔，产品属于硬件产品分类，你想要重点关注的分析维度是价格、质量、产量与供应链这三个部分，请问这几点的理解是正确的吗？

除此之外还需要和你确认几个细节：你最多希望对比多少个竞品呢？有没有指定具体要对标分析的其他钢笔品牌，还是后续会自动为你筛选对应数量的主流知名钢笔竞品？另外你有没有其他额外的分析要求呀？

user:
{
  "workflow_id": workflow_id,
  "user_message": "最多对比6个，没有指定的品牌"
}

assistant:
📋 已收集到的竞品分析配置信息如下，请你确认：
| 配置项 | 详情 |
| ---- | ---- |
| 目标产品 | 英雄牌钢笔 |
| 产品类别 | 硬件产品 |
| 重点关注维度 | 价格、质量、产量与供应链 |
| 最大对比竞品数量 | 6个 |
| 指定竞品列表 | 无指定品牌，将自动筛选6个主流知名钢笔厂商作为对标对象 |
| 额外分析要求 | 无特殊额外要求 |

确认配置无误后，将按照以下规则启动分析流程：
```json
{
  "target_product": "英雄牌钢笔",
  "product_category": "硬件产品",
  "focus_dimensions": ["价格", "质量", "产量与供应链"],
  "competitor_count": 6,
  "competitors": [],
  "language": "zh",
  "extra_requirements": "无特殊额外分析要求"
}
```
---CONFIG_COMPLETE---
