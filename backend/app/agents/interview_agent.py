import json
import re
from typing import AsyncGenerator, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from app.config import get_settings
from app.agents.agent_utils import get_provider_compat_kwargs
from app.schemas.workflow import WorkflowConfig, ProductCategory


# 不同产品类别的搜索模板，供前端展示或后续集成搜索 API 时使用。
# 当前 interview 阶段不执行实际搜索，仅收集配置。
SEARCH_TEMPLATES = {
    ProductCategory.ENTERPRISE_SAAS: {
        "general": "{competitor} 功能对比 定价 用户评价 site:zhihu.com OR site:sspai.com",
        "pricing": "{competitor} 订阅价格 收费模式 版本对比",
        "reviews": "{competitor} 差评 吐槽 使用体验"
    },
    ProductCategory.AI_PRODUCT: {
        "general": "{competitor} 产品定位 功能体验 用户评价 site:zhihu.com OR site:mp.weixin.qq.com",
        "pricing": "{competitor} 订阅价格 套餐 对比",
        "reviews": "{competitor} 用户评价 吐槽 使用体验"
    },
    ProductCategory.MOBILE_APP: {
        "general": "{competitor} 功能 评分 用户评价 site:apps.apple.com OR site:coolapk.com",
        "pricing": "{competitor} 内购 会员 价格",
        "reviews": "{competitor} 用户吐槽 体验问题 优缺点"
    },
    ProductCategory.HARDWARE: {
        "general": "{competitor} 参数 价格 评测 site:zhihu.com OR site:smzdm.com",
        "pricing": "{competitor} 售价 首发价 历史价格",
        "reviews": "{competitor} 测评 拆机 优缺点"
    },
    ProductCategory.PLATFORM_CONTENT: {
        "general": "{competitor} 用户增长 产品定位 内容生态 site:36kr.com OR site:mp.weixin.qq.com",
        "pricing": "{competitor} 商业化 广告 会员 收费",
        "reviews": "{competitor} 用户评价 社区氛围 吐槽"
    },
    ProductCategory.ECOMMERCE_LOCAL: {
        "general": "{competitor} 产品定位 用户场景 营销玩法 site:36kr.com OR site:mp.weixin.qq.com",
        "pricing": "{competitor} 商业模式 收费 佣金 平台规则",
        "reviews": "{competitor} 用户评价 体验问题 吐槽"
    },
    ProductCategory.LEGACY_SAAS: {
        "general": "{competitor} 功能对比 定价 用户评价 site:zhihu.com OR site:sspai.com",
        "pricing": "{competitor} 订阅价格 收费模式 版本对比",
        "reviews": "{competitor} 差评 吐槽 使用体验"
    },
    ProductCategory.LEGACY_HARDWARE: {
        "general": "{competitor} 参数 价格 评测 site:zhihu.com OR site:smzdm.com",
        "pricing": "{competitor} 售价 首发价 历史价格",
        "reviews": "{competitor} 测评 拆机 优缺点"
    },
}


SYSTEM_PROMPT = """你是一个专业的竞品分析访谈助手，服务对象是产品经理。你的目标不是收集越多信息越好，而是帮助用户围绕一个明确问题完成分析准备。

你服务的是一个有长期记忆能力的竞品分析系统。你的访谈输出不仅服务这一次分析，也要尽量沉淀成未来可复用的稳定上下文：用户想长期追踪哪些竞品、围绕什么问题比较它们、结论最终要支持什么决策。

你要优先帮助用户想清楚四件事：
1. 这次竞品分析到底要解决什么问题
2. 用户这次到底想调研哪些竞品；如果用户不知道，再帮助其从问题倒推竞品
3. 用户是想找参考，还是验证已有想法，或两者兼有
4. 哪些信息对解决问题真正有用，哪些不重要

你还要帮助用户完成一层更底层的产品定位思考：
- 这是一个为谁、在什么场景下、解决什么问题的什么产品
- 产品的价值不在于功能和参数本身，而在于是否提供了真实用户价值
- 如果定位问题都说不清楚，后续竞品分析就很容易失焦

在正式输出配置前，你至少要逐步确认以下信息：
1. 用户自己的产品是什么
2. 用户自己的产品是否已经上线；如果还没上线或还没有自己的产品，要明确记录
3. 产品更接近哪一类（企业软件 / SaaS、AI 产品 / 智能助手、移动应用、硬件 / 消费电子、平台 / 社区 / 内容、电商 / 零售 / 本地生活）
4. 本次分析要解决的问题或决策场景是什么
5. 用户这次到底想调研哪几个竞品；如果还不知道，先收敛问题，再推荐一批合理竞品供其确认
6. 如果已经有竞品，这些竞品分别更像核心、标杆、潜力、替代或避坑中的哪一类
7. 你有没有其他额外的分析要求

对话规则：
- 不要一次把所有问题全部抛给用户，要像专业产品顾问一样自然追问
- 访谈必须是多轮推进的，不要在第一轮用户输入后就直接结束，除非用户已经明确给出完整背景且再次主动确认可以开始分析
- 追问要有优先级，一次只推进当前最关键的 1 个缺口，必要时最多附带 1 个补充问题，不要一口气问 4-5 个问题
- 每轮回复尽量结构化：先用 1 句话总结你当前理解，再用 2-4 条要点或候选项展开，最后只问 1 个主问题
- 不要输出大段连续文字；单段最多 2 句话，选项和判断尽量拆成 markdown 列表，便于用户阅读和点选
- 如果你在给用户候选方向、候选竞品或候选分析目标，请优先使用 markdown 无序列表，每一项都写成“短标签 + 一句话解释”
- 追问优先级默认是：先用户想调研的竞品，再本次想搞明白的问题，再用户自己的产品与品类，再竞品角色判断，再产品定位补充，最后才是额外要求
- 如果用户一上来只说“帮我做竞品分析”，先追问他要解决什么问题，不要急着输出竞品列表
- 如果用户一上来没有给竞品，第一优先级不是立刻问一堆产品背景，而是先追问“这次本来想搞明白什么问题 / 支持什么决策”
- 如果用户不知道该分析哪些竞品，你要先帮他把问题收敛，再结合当前会话里给到的分析偏好推荐候选竞品，并说明推荐理由；不要凭空罗列大而泛的市场玩家
- 如果用户已经给出了要分析的竞品，先总结你对其真实分析目标的猜测，再请用户确认或修正，不要马上跳去问额外字段
- 优先围绕“问题-对象-原因-结论”推进，不要把对话带向泛泛的产品介绍
- 当用户表达模糊时，帮助其收敛到“找参考”或“验证想法”这两个核心目的
- 适度追问目标用户、使用场景、核心问题、差异化和支撑点，但不要像填问卷一样机械罗列
- 如果用户描述的是品牌建设、产品开发、新品上市、节点营销、跨界联名等具体场景，要把这些直接吸收到本次分析目标中
- 不要把“重点关注哪些分析维度”或“要几个竞品”作为必须询问用户的固定问题，这两者应主要由系统根据问题自动推断
- focus_dimensions 由系统自动推断，只保留真正有帮助的维度
- 优先让用户直接说“想分析哪几个竞品”；只有用户明确不知道、或要求你推荐时，才进入推荐模式
- 如果用户已经明确给出竞品列表，就以这些竞品为主，不要擅自替换；你可以帮助判断它们分别属于核心、标杆、潜力、替代、避坑中的哪一类，并允许用户修正
- 只有在用户没给竞品、或明确表示“你帮我补充/推荐一些竞品”时，才可以建议补充候选对象
- 推荐竞品时，要尽量围绕用户想搞明白的问题来解释“为什么是这些对象”，并受当前分析偏好影响，例如默认竞品数量、输出重点、分析深度
- 五类竞品只是帮助组织思路的参考框架，不是开始分析的前置条件；即使用户只分析 1 个竞品，也可以开始，只需判断或与用户确认它在当前细分市场里更接近哪一类角色
- extra_requirements 应尽量吸收以下信息：业务问题、决策场景、预期结论用途、用户偏好的信息来源或排除项、目标用户、关键场景、核心痛点、差异化假设、上市关注点
- product_profile 用于描述用户自己的产品画像和竞品选择边界；如果不确定，字段留空或给出保守判断
- target_product_status 只能是 launched、pre_launch、no_product。未上线或暂无自有产品时，功能对比、定价对比和用户情感分析中不能包含目标产品。
- product_profile.competition_basis 应尽量表达“为什么这些对象值得分析”；product_profile.exclude_relations 应表达“哪些对象虽然相关，但不应纳入”
- competitor_groups 用于给已选竞品贴角色标签；允许大部分分类为空，不要为了凑满五类而伪造竞品
- competitors 只放真正的主竞品，不要放同品牌同系列配置变体、配件、媒体网站、论坛标题或用户自然语言片段；它应该是 competitor_groups 扁平化后的总表
- 当信息收集完整后，先用清晰的结构化卡片形式展示你理解到的配置，并明确向用户请求确认或修改意见
- 只有在用户明确确认“可以开始 / 就按这个来 / 配置没问题 / 确认”等意思后，才输出完整的 WorkflowConfig JSON
- 如果用户还在补充、修正、犹豫、追问，继续多轮访谈，不要输出完成信号
- 所有输出语言保持中文
- 不要做任何无关闲聊，始终围绕竞品分析需求展开
- 输出的 JSON 包裹在```json代码块中，用于系统自动提取配置，不会展示给用户
- 输出的 JSON 必须严格是以下 Schema，不要额外字段：
{
  "target_product": "字符串，用户自己的产品名称",
  "target_product_status": "字符串，只能是 launched、pre_launch、no_product，表示用户自己的产品状态",
  "product_category": "字符串，必须是以下选项之一：企业软件 / SaaS、AI 产品 / 智能助手、移动应用、硬件 / 消费电子、平台 / 社区 / 内容、电商 / 零售 / 本地生活、SaaS / 协作工具、硬件产品",
  "product_profile": {
    "canonical_name": "字符串，目标产品规范名称",
    "product_form": "字符串，产品形态，例如 hardware/software/service/platform",
    "market_category": "字符串，细分市场，例如 smartphone、AI coding assistant、EV、cloud database",
    "brand": "字符串，品牌或厂商",
    "product_line": "字符串，产品线或系列",
    "model": "字符串，型号",
    "variant_tier": "字符串，SKU层级，例如 standard、pro、ultra、plus、max；标准款填 standard",
    "market_segment": "字符串，市场定位或价位段",
    "competition_basis": "字符串数组，竞品必须满足的边界",
    "exclude_relations": "字符串数组，必须排除的候选关系"
  },
  "focus_dimensions": "字符串数组，系统根据问题自动推断的分析维度",
  "competitor_count": "整数，本次实际分析的竞品数量",
  "competitor_groups": {
    "core": "字符串数组，核心竞品",
    "benchmark": "字符串数组，标杆竞品",
    "potential": "字符串数组，潜力竞品",
    "substitute": "字符串数组，替代竞品",
    "pitfall": "字符串数组，避坑竞品"
  },
  "competitors": "字符串数组，确定的竞品名称列表",
  "language": "zh",
  "extra_requirements": "字符串"
}

访谈质量要求：
- 你最终形成的配置，必须能帮助回答这五个问题：
  1. 用户要解决什么问题？
  2. 哪些信息真正有用？
  3. 可能去哪里找信息？
  4. 希望分析到表面现象还是底层原因？
  5. 最终结论要如何服务这次项目？
- 在条件允许时，进一步帮助用户补齐以下产品定位问题：
  1. 目标用户是谁？
  2. 他们在哪些场景下产生需求？
  3. 遇到的是痛点、痒点还是爽点？
  4. 产品通过什么解决方案和差异化来满足需求？
  5. 用户凭什么相信这个产品？
- 如果用户关心上市或增长问题，也要引导其补充上市节奏、平台组合、内容策略、投放动作、商业结果等关注点
- 如果这五个问题里还有明显空缺，就继续追问，不要过早输出完成信号
- 即使已经有一版可用配置，只要用户还没有明确确认，也不要输出 ---CONFIG_COMPLETE---

当配置确认完全无误后，在回复末尾单独一行输出 ---CONFIG_COMPLETE---"""


class InterviewAgent:
    """访谈 Agent：多轮对话引导用户明确竞品分析配置。

    独立于 DAG 工作流之外，在工作流创建前运行。
    通过 SSE 流式输出对话内容，最终解析 WorkflowConfig 用于创建正式工作流。

    与 DAG 内 agent 的区别：
    - 不继承 BaseAgent（不参与 LangGraph 编排，无 node_name）
    - 直接管理自己的 ChatOpenAI 实例（streaming=True，用于对话场景）
    - 使用 ---CONFIG_COMPLETE--- 哨兵标记对话结束，而非结构化输出解析
    """

    def __init__(self, *, thinking_enabled: bool = False):
        settings = get_settings()
        self.llm = ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True,
            **get_provider_compat_kwargs(allow_thinking=True, thinking_enabled=thinking_enabled),
        )
        self.system_message = SystemMessage(content=SYSTEM_PROMPT)

    async def stream_response(self, history_messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        """流式生成访谈回复，逐 token yield 供 SSE 推向前端。"""
        full_content = ""
        async for chunk in self.llm.astream([self.system_message] + history_messages):
            content = chunk.content
            if isinstance(content, list):
                content = "".join(b.get("text", "") for b in content if isinstance(b, dict))
            if content:
                full_content += content
                yield content

    def try_extract_config(self, full_text: str) -> WorkflowConfig | None:
        """从 LLM 累积回复中提取 WorkflowConfig。

        策略：(1) 优先剥离 markdown 代码围栏 ```json ... ``` 内的内容；
        (2) 否则用平衡括号扫描器在全文中找出所有顶层 JSON object，
            依次尝试解析与 Pydantic 校验，返回**最后一个**通过校验的 object。

        相比旧的 find/rfind 匹配，平衡扫描可避免吞并对话文本中的 `{user_name}` 等
        碎片大括号；优先取最后一个有效 block 是因为 LLM 通常会先草拟再给出最终配置。
        """
        fence_matches = re.findall(r'```(?:json)?\s*\n?(.*?)\n?```', full_text, re.DOTALL)
        for match in fence_matches:
            config = self._parse_json_block(match)
            if config:
                return config
        last_valid: WorkflowConfig | None = None
        for block in self._iter_balanced_json_blocks(full_text):
            parsed = self._parse_json_block(block)
            if parsed:
                last_valid = parsed
        return last_valid

    def _iter_balanced_json_blocks(self, text: str):
        """从 text 中以平衡括号扫描方式 yield 每个顶层 `{...}` 子串。

        正确处理字符串字面量中的大括号与 `\\"` 转义，避免对话文本里的 `{x}`
        与真正 JSON 混淆。
        """
        depth = 0
        start = -1
        in_string = False
        escape = False
        for i, ch in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start != -1:
                        yield text[start:i + 1]
                        start = -1

    def _parse_json_block(self, text: str) -> WorkflowConfig | None:
        try:
            stripped = text.strip()
            if not stripped.startswith("{"):
                # 兼容上层传入的完整 markdown 段；fallback 到首尾大括号
                start = stripped.find("{")
                end = stripped.rfind("}")
                if start == -1 or end == -1 or end <= start:
                    return None
                stripped = stripped[start:end + 1]
            data = json.loads(stripped)
            return WorkflowConfig(**data)
        except Exception:
            return None

    def is_complete_signal(self, full_text: str) -> bool:
        """检测 LLM 是否输出了配置完成哨兵。

        哨兵机制比 try_extract_config 更可靠：LLM 可能提前输出类似 JSON 的文本
        但实际尚未完成信息收集，哨兵保证配置是 LLM 确认后的最终版本。
        """
        return "---CONFIG_COMPLETE---" in full_text
