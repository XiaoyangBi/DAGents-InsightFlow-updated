import type { WorkflowConfig } from "@/types/workflow";

export type ModelProvider =
  | "OpenAI"
  | "Anthropic"
  | "DeepSeek"
  | "Google"
  | "MiniMax"
  | "Moonshot"
  | "OpenRouter"
  | "OpenAI Compatible";

export type BuiltinModelOption = {
  id: string;
  label: string;
  provider: ModelProvider;
  model: string;
  badge?: string;
};

export type CustomModelConfig = {
  id: string;
  provider: ModelProvider;
  model: string;
  apiKey: string;
  baseUrl?: string;
};

export type AnalysisPreferences = {
  reportLanguage: "中文" | "英文";
  analysisDepth: "快速" | "标准" | "深入";
  competitorCount: 3 | 5 | 8;
  outputFocus: "功能" | "定价" | "用户反馈" | "全量";
  reportStyle: "简报型" | "结构化研究型";
};

export type ModelDataSettings = {
  defaultModel: string;
  customModels: CustomModelConfig[];
  webResearchEnabled: boolean;
  citationMode: "always" | "smart" | "off";
  retainLongTermMemory: boolean;
  saveReasoningTrail: boolean;
};

export type AppSettings = {
  analysisPreferences: AnalysisPreferences;
  modelDataSettings: ModelDataSettings;
};

export const DEFAULT_ANALYSIS_PREFERENCES: AnalysisPreferences = {
  reportLanguage: "中文",
  analysisDepth: "标准",
  competitorCount: 5,
  outputFocus: "全量",
  reportStyle: "结构化研究型",
};

export const BUILTIN_MODEL_OPTIONS: BuiltinModelOption[] = [
  { id: "builtin:deepseek-v4-pro", label: "deepseek-v4-pro", provider: "DeepSeek", model: "deepseek-v4-pro" },
  { id: "builtin:gpt-5.4", label: "gpt-5.4", provider: "OpenAI", model: "gpt-5.4" },
  { id: "builtin:gpt-5.2", label: "gpt-5.2", provider: "OpenAI", model: "gpt-5.2" },
  { id: "builtin:minimax-m2.7", label: "MiniMax-M2.7", provider: "MiniMax", model: "MiniMax-M2.7" },
  { id: "builtin:kimi-k2.5", label: "kimi-k2.5", provider: "Moonshot", model: "kimi-k2.5" },
  { id: "builtin:gemini-3.1-pro-preview", label: "gemini-3.1-pro-preview", provider: "Google", model: "gemini-3.1-pro-preview" },
  { id: "builtin:gemini-3-flash-preview", label: "gemini-3-flash-preview", provider: "Google", model: "gemini-3-flash-preview" },
];

export const DEFAULT_MODEL_DATA_SETTINGS: ModelDataSettings = {
  defaultModel: BUILTIN_MODEL_OPTIONS[0].id,
  customModels: [],
  webResearchEnabled: true,
  citationMode: "smart",
  retainLongTermMemory: true,
  saveReasoningTrail: false,
};

export const DEFAULT_APP_SETTINGS: AppSettings = {
  analysisPreferences: DEFAULT_ANALYSIS_PREFERENCES,
  modelDataSettings: DEFAULT_MODEL_DATA_SETTINGS,
};

const APP_SETTINGS_STORAGE_KEY = "insightflow_app_settings";

function normalizeDefaultModelId(value: unknown) {
  if (typeof value !== "string" || !value.trim()) {
    return DEFAULT_MODEL_DATA_SETTINGS.defaultModel;
  }

  const builtinMatch = BUILTIN_MODEL_OPTIONS.find(
    (option) => option.id === value || option.model === value || option.label === value,
  );
  if (builtinMatch) {
    return builtinMatch.id;
  }

  if (value === "gpt-4.1" || value === "builtin:gpt-4.1") {
    return "builtin:gpt-5.4";
  }
  if (value === "claude-sonnet-4" || value === "builtin:claude-sonnet-4") {
    return DEFAULT_MODEL_DATA_SETTINGS.defaultModel;
  }
  if (value === "gpt-5.4" || value === "builtin:gpt-5.4-beta") {
    return "builtin:gpt-5.4";
  }
  if (value === "minimax-m2.7") {
    return "builtin:minimax-m2.7";
  }
  if (value.startsWith("builtin:")) {
    return DEFAULT_MODEL_DATA_SETTINGS.defaultModel;
  }

  return value;
}

function normalizeCustomModels(value: unknown): CustomModelConfig[] {
  if (!Array.isArray(value)) return [];

  return value
    .filter((item): item is Partial<CustomModelConfig> => Boolean(item) && typeof item === "object")
    .map((item, index) => ({
      id: typeof item.id === "string" && item.id ? item.id : `custom-${index}`,
      provider:
        typeof item.provider === "string" && item.provider
          ? (item.provider as ModelProvider)
          : "OpenAI Compatible",
      model: typeof item.model === "string" ? item.model.trim() : "",
      apiKey: typeof item.apiKey === "string" ? item.apiKey : "",
      baseUrl: typeof item.baseUrl === "string" ? item.baseUrl.trim() : "",
    }))
    .filter((item) => Boolean(item.model));
}

export function readAppSettings(): AppSettings {
  if (typeof window === "undefined") return DEFAULT_APP_SETTINGS;
  try {
    const raw = window.localStorage.getItem(APP_SETTINGS_STORAGE_KEY);
    if (!raw) return DEFAULT_APP_SETTINGS;
    const parsed = JSON.parse(raw) as Partial<AppSettings>;
    return {
      analysisPreferences: {
        ...DEFAULT_ANALYSIS_PREFERENCES,
        ...(parsed.analysisPreferences ?? {}),
      },
      modelDataSettings: {
        ...DEFAULT_MODEL_DATA_SETTINGS,
        ...(parsed.modelDataSettings ?? {}),
        defaultModel: normalizeDefaultModelId(parsed.modelDataSettings?.defaultModel),
        customModels: normalizeCustomModels(parsed.modelDataSettings?.customModels),
      },
    };
  } catch {
    return DEFAULT_APP_SETTINGS;
  }
}

export function writeAppSettings(settings: AppSettings) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(APP_SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}

export function readAnalysisPreferences(): AnalysisPreferences {
  return readAppSettings().analysisPreferences;
}

export function writeAnalysisPreferences(preferences: AnalysisPreferences) {
  const current = readAppSettings();
  writeAppSettings({ ...current, analysisPreferences: preferences });
}

export function readModelDataSettings(): ModelDataSettings {
  return readAppSettings().modelDataSettings;
}

export function writeModelDataSettings(settings: ModelDataSettings) {
  const current = readAppSettings();
  writeAppSettings({ ...current, modelDataSettings: settings });
}

export function getAllModelOptions(settings: ModelDataSettings) {
  return [
    ...BUILTIN_MODEL_OPTIONS,
    ...settings.customModels.map((model) => ({
      id: model.id,
      label: model.model,
      provider: model.provider,
      model: model.model,
      badge: "自定义",
    })),
  ];
}

function focusDimensionsFor(outputFocus: AnalysisPreferences["outputFocus"]): string[] {
  switch (outputFocus) {
    case "功能":
      return ["核心问题", "解决方案", "功能体验"];
    case "定价":
      return ["商业模式", "定价策略", "上市与增长"];
    case "用户反馈":
      return ["目标用户", "使用场景", "用户反馈"];
    case "全量":
    default:
      return ["目标用户", "使用场景", "核心问题", "解决方案", "支撑点", "功能体验", "用户反馈", "上市与增长"];
  }
}

function extraRequirementsFor(preferences: AnalysisPreferences): string {
  return [
    `Preferred analysis depth: ${preferences.analysisDepth}`,
    `Preferred report style: ${preferences.reportStyle}`,
  ].join(" | ");
}

export function applyPreferencesToConfig(
  config: Partial<WorkflowConfig>,
  preferences: AnalysisPreferences,
): Partial<WorkflowConfig> {
  return {
    ...config,
    language: preferences.reportLanguage === "英文" ? "en" : "zh",
    competitor_count: preferences.competitorCount,
    focus_dimensions: focusDimensionsFor(preferences.outputFocus),
    extra_requirements: extraRequirementsFor(preferences),
  };
}
