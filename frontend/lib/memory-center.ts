export type MemoryType =
  | "user_preference"
  | "product_profile"
  | "feature_focus"
  | "research_goal"
  | "confirmed_conclusion";

export type MemorySource = "user_explicit" | "workflow_summary" | "review_feedback" | "inferred";

export type MemoryScope = "user" | "product" | "thread";

export interface MemoryCenterItem {
  id: string;
  memoryType: MemoryType;
  title: string;
  content: string;
  summary: string;
  scope: MemoryScope;
  source: MemorySource;
  explicit: boolean;
  freshness: "recent" | "stable" | "aging";
  updatedAt: string;
  tags: string[];
  targetProduct?: string;
  researchThread?: string;
  status: "active" | "muted";
}

export const MEMORY_TYPE_LABELS: Record<MemoryType, string> = {
  user_preference: "用户偏好",
  product_profile: "产品画像",
  feature_focus: "功能焦点",
  research_goal: "研究目标",
  confirmed_conclusion: "已确认结论",
};

export const MEMORY_SOURCE_LABELS: Record<MemorySource, string> = {
  user_explicit: "用户明确告诉我",
  workflow_summary: "工作流总结沉淀",
  review_feedback: "评审反馈纠正",
  inferred: "系统推断待复核",
};

export const MEMORY_SCOPE_LABELS: Record<MemoryScope, string> = {
  user: "用户层",
  product: "产品层",
  thread: "研究线程",
};

export const MOCK_MEMORY_ITEMS: MemoryCenterItem[] = [
  {
    id: "mem-001",
    memoryType: "user_preference",
    title: "偏好结论先行，且引用要明显",
    content:
      "输出偏好是先给决策结论，再展开证据；对关键判断尽量附引用或证据边界，不喜欢没有依据的大段泛化分析。",
    summary: "更重视决策结论和证据可见性。",
    scope: "user",
    source: "user_explicit",
    explicit: true,
    freshness: "stable",
    updatedAt: "2026-06-21T09:12:00+08:00",
    tags: ["报告风格", "引用", "决策导向"],
    status: "active",
  },
  {
    id: "mem-002",
    memoryType: "product_profile",
    title: "当前主产品是 personal product analysis assistant",
    content:
      "你正在构建一个懂你的 personal product analysis assistant，希望它跨时间理解你做的产品、不同阶段的重点功能和持续竞品分析任务。",
    summary: "主产品方向是长期个人产品分析助手。",
    scope: "product",
    source: "user_explicit",
    explicit: true,
    freshness: "stable",
    updatedAt: "2026-06-22T14:30:00+08:00",
    tags: ["主产品", "定位", "长期助手"],
    targetProduct: "Personal Product Analysis Assistant",
    status: "active",
  },
  {
    id: "mem-003",
    memoryType: "research_goal",
    title: "V2 重点是可插拔记忆与 RAG",
    content:
      "当前阶段的 V2 改造目标，是把记忆系统做成标准接口 + 可替换实现，并让 RAG 成为一等事实增强能力。",
    summary: "V2 核心建设目标聚焦 Memory 与 RAG 双引擎。",
    scope: "thread",
    source: "workflow_summary",
    explicit: false,
    freshness: "recent",
    updatedAt: "2026-06-23T10:05:00+08:00",
    tags: ["V2", "架构", "Memory", "RAG"],
    researchThread: "V2 架构改造",
    status: "active",
  },
  {
    id: "mem-004",
    memoryType: "feature_focus",
    title: "优先关注记忆中心与可见性",
    content:
      "不仅要让系统记住你，还要让你显式看到它记住了什么，支持查看、筛选、删除、纠正和控制是否继续保留。",
    summary: "记忆透明度是当前产品体验重点。",
    scope: "thread",
    source: "review_feedback",
    explicit: true,
    freshness: "recent",
    updatedAt: "2026-06-23T10:28:00+08:00",
    tags: ["记忆中心", "可见性", "删除", "纠正"],
    researchThread: "Memory Center",
    status: "active",
  },
  {
    id: "mem-005",
    memoryType: "confirmed_conclusion",
    title: "Memory 负责懂你，RAG 负责站得住",
    content:
      "当前已确认的产品原则是：Memory 决定助手是否长期懂你，RAG 决定输出是否有事实支撑，两者都必须是一等能力。",
    summary: "Memory 与 RAG 不能互相替代。",
    scope: "user",
    source: "workflow_summary",
    explicit: false,
    freshness: "stable",
    updatedAt: "2026-06-22T20:40:00+08:00",
    tags: ["原则", "RAG", "长期记忆"],
    status: "active",
  },
  {
    id: "mem-006",
    memoryType: "feature_focus",
    title: "曾推断你更偏好增长拆解，但待确认",
    content:
      "系统从多次调研主题推断你偏好增长与上市节奏拆解，但目前这条还没有被明确确认，后续需要继续观察或由你手动修正。",
    summary: "一条待确认的系统推断。",
    scope: "user",
    source: "inferred",
    explicit: false,
    freshness: "aging",
    updatedAt: "2026-06-10T11:22:00+08:00",
    tags: ["推断", "增长", "待确认"],
    status: "muted",
  },
];

export function formatMemoryTime(iso: string): string {
  return new Date(iso).toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
