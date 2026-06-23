import { readModelDataSettings } from "@/lib/analysis-preferences";
import type { CompetitorGroups, WorkflowConfig } from "@/types/workflow";

export type CompetitorHint = {
  name: string;
  role: string;
  tags: string[];
};

export type InterviewInsights = {
  longTermTargets: string[];
  coreQuestion: string;
  decisionUse: string;
  memoryTags: string[];
  competitorHints: CompetitorHint[];
};

export type InterviewMemoryEntry = InterviewInsights & {
  workflowId: string;
  targetProduct: string;
  updatedAt: string;
};

const MEMORY_BANK_STORAGE_KEY = "insightflow_interview_memory_bank";

const ROLE_LABELS: Record<keyof CompetitorGroups, string> = {
  core: "核心对标",
  benchmark: "标杆参考",
  potential: "潜力关注",
  substitute: "替代路径",
  pitfall: "避坑样本",
};

const DIMENSION_REASON_MAP: Array<{ match: string; label: string }> = [
  { match: "功能", label: "功能参考" },
  { match: "定价", label: "定价参照" },
  { match: "用户", label: "用户反馈" },
  { match: "增长", label: "增长打法" },
  { match: "场景", label: "场景对照" },
  { match: "定位", label: "定位参照" },
  { match: "方案", label: "方案拆解" },
];

export function deriveInterviewInsights(config: Partial<WorkflowConfig>): InterviewInsights {
  const longTermTargets = dedupeStrings(config.competitors ?? []);
  const coreQuestion = deriveCoreQuestion(config);
  const decisionUse = deriveDecisionUse(config);
  const memoryTags = dedupeStrings([
    config.target_product ?? "",
    config.product_category ?? "",
    ...(config.focus_dimensions ?? []).slice(0, 3),
    ...longTermTargets.slice(0, 3),
  ]).slice(0, 8);

  return {
    longTermTargets,
    coreQuestion,
    decisionUse,
    memoryTags,
    competitorHints: deriveCompetitorHints(config),
  };
}

export function persistInterviewInsights(workflowId: string, config: Partial<WorkflowConfig>) {
  if (typeof window === "undefined") return;
  if (!readModelDataSettings().retainLongTermMemory) return;

  const insights = deriveInterviewInsights(config);
  if (
    insights.longTermTargets.length === 0 &&
    !insights.coreQuestion &&
    !insights.decisionUse &&
    insights.memoryTags.length === 0
  ) {
    return;
  }

  const nextEntry: InterviewMemoryEntry = {
    workflowId,
    targetProduct: config.target_product ?? "",
    updatedAt: new Date().toISOString(),
    ...insights,
  };

  const current = readInterviewMemoryBank().filter((entry) => entry.workflowId !== workflowId);
  window.localStorage.setItem(MEMORY_BANK_STORAGE_KEY, JSON.stringify([nextEntry, ...current].slice(0, 50)));
}

export function readInterviewMemoryBank(): InterviewMemoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(MEMORY_BANK_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as InterviewMemoryEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function deriveCoreQuestion(config: Partial<WorkflowConfig>): string {
  const extra = cleanSentence(config.extra_requirements);
  if (extra) return extra;
  if (config.focus_dimensions && config.focus_dimensions.length > 0) {
    return `围绕${config.focus_dimensions.slice(0, 2).join("、")}理解主要竞品差异。`;
  }
  if (config.competitors && config.competitors.length > 0) {
    return `理解 ${config.competitors.slice(0, 2).join("、")} 的核心差异与可借鉴点。`;
  }
  return "";
}

function deriveDecisionUse(config: Partial<WorkflowConfig>): string {
  const extra = config.extra_requirements ?? "";
  const matched = extra.match(/(?:用于|帮助|支持|为了)([^|。；\n]+)/);
  if (matched?.[1]) return matched[1].trim();
  if (config.target_product) return `支持 ${config.target_product} 的下一步产品判断`;
  return "";
}

function deriveCompetitorHints(config: Partial<WorkflowConfig>): CompetitorHint[] {
  const groups = config.competitor_groups ?? emptyGroups();
  const dimensions = config.focus_dimensions ?? [];
  return dedupeStrings(config.competitors ?? []).map((name) => {
    const role = findRoleForCompetitor(name, groups);
    const tags = dedupeStrings([
      role ? ROLE_LABELS[role] : "",
      ...dimensions.flatMap((dimension) =>
        DIMENSION_REASON_MAP.filter((item) => dimension.includes(item.match)).map((item) => item.label),
      ),
    ]).slice(0, 3);

    return {
      name,
      role: role ? ROLE_LABELS[role] : "待确认角色",
      tags,
    };
  });
}

function findRoleForCompetitor(name: string, groups: Partial<CompetitorGroups>): keyof CompetitorGroups | null {
  const lowered = name.toLowerCase();
  const entries: Array<keyof CompetitorGroups> = ["core", "benchmark", "potential", "substitute", "pitfall"];
  for (const key of entries) {
    if ((groups[key] ?? []).some((item) => item.toLowerCase() === lowered)) {
      return key;
    }
  }
  return null;
}

function cleanSentence(value: string | undefined): string {
  return (value ?? "").split("|")[0].trim();
}

function dedupeStrings(values: string[]): string[] {
  const seen = new Set<string>();
  return values
    .map((value) => value.trim())
    .filter((value) => {
      if (!value) return false;
      const key = value.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function emptyGroups(): CompetitorGroups {
  return {
    core: [],
    benchmark: [],
    potential: [],
    substitute: [],
    pitfall: [],
  };
}
