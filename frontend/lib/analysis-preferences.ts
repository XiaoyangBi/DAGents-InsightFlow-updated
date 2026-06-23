import type { WorkflowConfig } from "@/types/workflow";

export type AnalysisPreferences = {
  reportLanguage: "中文" | "英文";
  analysisDepth: "快速" | "标准" | "深入";
  competitorCount: 3 | 5 | 8;
  outputFocus: "功能" | "定价" | "用户反馈" | "全量";
  reportStyle: "简报型" | "结构化研究型";
};

export type ModelDataSettings = {
  defaultModel: "deepseek-v4-pro" | "gpt-4.1" | "claude-sonnet-4";
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

export const DEFAULT_MODEL_DATA_SETTINGS: ModelDataSettings = {
  defaultModel: "deepseek-v4-pro",
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
