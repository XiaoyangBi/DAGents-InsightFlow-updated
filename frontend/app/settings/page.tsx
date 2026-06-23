"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { AuthGuard } from "@/components/auth/auth-guard";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import {
  BUILTIN_MODEL_OPTIONS,
  DEFAULT_APP_SETTINGS,
  type AppSettings,
  type CustomModelConfig,
  type ModelProvider,
  readAppSettings,
  writeAppSettings,
} from "@/lib/analysis-preferences";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { ArrowLeft, Brain, Check, ChevronDown, Plus, RotateCcw, Save, Trash2, X } from "lucide-react";

const MODEL_PROVIDER_OPTIONS: ModelProvider[] = [
  "OpenAI",
  "Anthropic",
  "DeepSeek",
  "Google",
  "MiniMax",
  "Moonshot",
  "OpenRouter",
  "OpenAI Compatible",
];

const PROVIDER_MODEL_OPTIONS: Record<ModelProvider, string[]> = {
  OpenAI: ["gpt-5.4", "gpt-5.2", "gpt-4o", "gpt-4o-mini"],
  Anthropic: [],
  DeepSeek: ["deepseek-v4-pro", "deepseek-chat", "deepseek-reasoner"],
  Google: ["gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-2.5-pro"],
  MiniMax: ["MiniMax-M2.7"],
  Moonshot: ["kimi-k2.5"],
  OpenRouter: ["openai/gpt-5.4", "google/gemini-3.1-pro-preview", "moonshotai/kimi-k2.5"],
  "OpenAI Compatible": [],
};

type CustomModelDraft = {
  provider: ModelProvider;
  presetModel: string;
  customModel: string;
  apiKey: string;
  baseUrl: string;
};

function createEmptyCustomModelDraft(): CustomModelDraft {
  return {
    provider: "OpenAI",
    presetModel: PROVIDER_MODEL_OPTIONS.OpenAI[0] ?? "",
    customModel: "",
    apiKey: "",
    baseUrl: "",
  };
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [savedSettings, setSavedSettings] = useState<AppSettings>(() => readAppSettings());
  const [draftSettings, setDraftSettings] = useState<AppSettings>(() => readAppSettings());
  const [showAddModelModal, setShowAddModelModal] = useState(false);
  const [customModelDraft, setCustomModelDraft] = useState<CustomModelDraft>(createEmptyCustomModelDraft);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    appearance: false,
    analysis: false,
    modelData: false,
  });

  const hasUnsavedChanges = useMemo(
    () => JSON.stringify(savedSettings) !== JSON.stringify(draftSettings),
    [savedSettings, draftSettings],
  );

  const toggleSection = (key: string) => {
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = () => {
    writeAppSettings(draftSettings);
    setSavedSettings(draftSettings);
  };

  const handleCancel = () => {
    setDraftSettings(savedSettings);
  };

  const handleRestoreDefaults = () => {
    setDraftSettings(DEFAULT_APP_SETTINGS);
  };

  const currentDefaultModelId = draftSettings.modelDataSettings.defaultModel;

  const saveCustomModel = () => {
    const resolvedModel =
      customModelDraft.presetModel === "__custom__"
        ? customModelDraft.customModel.trim()
        : customModelDraft.presetModel.trim();
    const trimmedApiKey = customModelDraft.apiKey.trim();
    if (!resolvedModel || !trimmedApiKey) return;

    const nextModel: CustomModelConfig = {
      id: `custom:${Date.now().toString(36)}`,
      provider: customModelDraft.provider,
      model: resolvedModel,
      apiKey: trimmedApiKey,
      baseUrl: customModelDraft.baseUrl.trim(),
    };

    setDraftSettings((prev) => ({
      ...prev,
      modelDataSettings: {
        ...prev.modelDataSettings,
        defaultModel: nextModel.id,
        customModels: [nextModel, ...prev.modelDataSettings.customModels],
      },
    }));
    setCustomModelDraft(createEmptyCustomModelDraft());
    setShowAddModelModal(false);
  };

  const removeCustomModel = (modelId: string) => {
    setDraftSettings((prev) => {
      const customModels = prev.modelDataSettings.customModels.filter((model) => model.id !== modelId);
      const defaultModel =
        prev.modelDataSettings.defaultModel === modelId
          ? BUILTIN_MODEL_OPTIONS[0].id
          : prev.modelDataSettings.defaultModel;

      return {
        ...prev,
        modelDataSettings: {
          ...prev.modelDataSettings,
          defaultModel,
          customModels,
        },
      };
    });
  };

  return (
    <AuthGuard>
      <div className="min-h-screen" style={{ backgroundColor: "var(--bg-primary)" }}>
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-[920px] items-center justify-between px-6 py-3">
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
              >
                <ArrowLeft size={18} />
              </Link>
              <h1 className="text-sm font-bold text-[var(--text-primary)]">设置</h1>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/memory"
                className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-3 py-2 text-xs font-medium text-[var(--text-secondary)] shadow-sm hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
              >
                <Brain size={14} /> 记忆中心
              </Link>
              {user && (
                <p className="text-xs text-[var(--text-muted)]">{user.username}</p>
              )}
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[920px] space-y-6 px-6 py-8">
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--panel-shadow)]">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">设置草稿</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <ActionButton onClick={handleRestoreDefaults} variant="ghost">
                  <RotateCcw size={14} /> 恢复初始设置
                </ActionButton>
                <ActionButton onClick={handleCancel} variant="ghost" disabled={!hasUnsavedChanges}>
                  <X size={14} /> 取消
                </ActionButton>
                <ActionButton onClick={handleSave} variant="primary" disabled={!hasUnsavedChanges}>
                  <Save size={14} /> 保存
                </ActionButton>
              </div>
            </div>
          </section>

          <section className="max-w-[760px] rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--card-shadow)]">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="max-w-md">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">Memory Center</p>
                <h2 className="mt-1.5 text-base font-semibold text-[var(--text-primary)]">查看长期记忆</h2>
                <p className="mt-1.5 text-sm leading-6 text-[var(--text-muted)]">
                  检查系统到底记住了什么，并进行清理或修正。
                </p>
              </div>
              <Link href="/memory">
                <Button variant="outline">
                  <Brain size={14} /> 打开记忆中心
                </Button>
              </Link>
            </div>
          </section>

          <SettingsSection
            title="外观"
            description=""
            collapsed={collapsed.appearance}
            onToggle={() => toggleSection("appearance")}
          >
            <ThemeToggle />
          </SettingsSection>

          <SettingsSection
            title="分析偏好"
            description=""
            collapsed={collapsed.analysis}
            onToggle={() => toggleSection("analysis")}
          >
            <div className="space-y-3">
              <PreferenceRow title="默认报告语言" description="决定报告和主要产出默认用哪种语言呈现。">
                <SegmentedControl
                  value={draftSettings.analysisPreferences.reportLanguage}
                  options={["中文", "英文"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      analysisPreferences: { ...prev.analysisPreferences, reportLanguage: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="默认分析深度" description="快速适合扫盘，标准适合日常调研，深入适合关键竞品复盘。">
                <SegmentedControl
                  value={draftSettings.analysisPreferences.analysisDepth}
                  options={["快速", "标准", "深入"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      analysisPreferences: { ...prev.analysisPreferences, analysisDepth: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="默认竞品数量" description="控制首次调研时建议覆盖的竞品范围。">
                <SegmentedControl
                  value={draftSettings.analysisPreferences.competitorCount}
                  options={[3, 5, 8]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      analysisPreferences: { ...prev.analysisPreferences, competitorCount: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="默认输出重点" description="决定报告更偏功能、定价、用户反馈，或做全量扫描。">
                <SegmentedControl
                  value={draftSettings.analysisPreferences.outputFocus}
                  options={["功能", "定价", "用户反馈", "全量"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      analysisPreferences: { ...prev.analysisPreferences, outputFocus: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="默认报告风格" description="简报型更短平快，结构化研究型更适合系统沉淀和复用。">
                <SegmentedControl
                  value={draftSettings.analysisPreferences.reportStyle}
                  options={["简报型", "结构化研究型"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      analysisPreferences: { ...prev.analysisPreferences, reportStyle: value },
                    }))
                  }
                />
              </PreferenceRow>
            </div>
          </SettingsSection>

          <SettingsSection
            title="模型与数据"
            description=""
            collapsed={collapsed.modelData}
            onToggle={() => toggleSection("modelData")}
          >
            <div className="space-y-3">
              <PreferenceRow title="默认模型" stacked>
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-xs font-medium uppercase tracking-[0.18em] text-[var(--text-muted)]">内置模型</p>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => setShowAddModelModal(true)}
                    >
                      <Plus size={14} /> 添加模型
                    </Button>
                  </div>

                  <div className="grid gap-2">
                    {BUILTIN_MODEL_OPTIONS.map((model) => {
                      const active = currentDefaultModelId === model.id;
                      return (
                        <ModelOptionCard
                          key={model.id}
                          title={model.label}
                          subtitle={model.provider}
                          active={active}
                          onClick={() =>
                            setDraftSettings((prev) => ({
                              ...prev,
                              modelDataSettings: { ...prev.modelDataSettings, defaultModel: model.id },
                            }))
                          }
                        />
                      );
                    })}
                  </div>

                  {draftSettings.modelDataSettings.customModels.length > 0 && (
                    <div className="space-y-2">
                      <p className="pt-1 text-xs font-medium uppercase tracking-[0.18em] text-[var(--text-muted)]">
                        我的模型
                      </p>
                      <div className="grid gap-2">
                        {draftSettings.modelDataSettings.customModels.map((model) => {
                          const active = currentDefaultModelId === model.id;
                          return (
                            <ModelOptionCard
                              key={model.id}
                              title={model.model}
                              subtitle={model.provider}
                              badge="自定义"
                              active={active}
                              onClick={() =>
                                setDraftSettings((prev) => ({
                                  ...prev,
                                  modelDataSettings: { ...prev.modelDataSettings, defaultModel: model.id },
                                }))
                              }
                              action={
                                <button
                                  type="button"
                                  onClick={(event) => {
                                    event.stopPropagation();
                                    removeCustomModel(model.id);
                                  }}
                                  className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] transition-colors hover:text-rose-300"
                                  aria-label={`删除模型 ${model.model}`}
                                >
                                  <Trash2 size={14} />
                                </button>
                              }
                            />
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </PreferenceRow>

              <PreferenceRow title="联网检索">
                <BooleanControl
                  enabled={draftSettings.modelDataSettings.webResearchEnabled}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      modelDataSettings: { ...prev.modelDataSettings, webResearchEnabled: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="引用证据">
                <SegmentedControl
                  value={draftSettings.modelDataSettings.citationMode}
                  options={["always", "smart", "off"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      modelDataSettings: { ...prev.modelDataSettings, citationMode: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="长期记忆沉淀">
                <BooleanControl
                  enabled={draftSettings.modelDataSettings.retainLongTermMemory}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      modelDataSettings: { ...prev.modelDataSettings, retainLongTermMemory: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="中间推理痕迹">
                <BooleanControl
                  enabled={draftSettings.modelDataSettings.saveReasoningTrail}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      modelDataSettings: { ...prev.modelDataSettings, saveReasoningTrail: value },
                    }))
                  }
                />
              </PreferenceRow>
            </div>
          </SettingsSection>

          <Modal
            open={showAddModelModal}
            onClose={() => {
              setShowAddModelModal(false);
              setCustomModelDraft(createEmptyCustomModelDraft());
            }}
            title="添加模型"
            className="max-w-xl"
          >
            <div className="space-y-5">
              <div className="space-y-2">
                <FieldLabel required>服务商</FieldLabel>
                <SelectControl
                  value={customModelDraft.provider}
                  onChange={(value) => {
                    const provider = value as ModelProvider;
                    const defaultPreset = PROVIDER_MODEL_OPTIONS[provider][0] ?? "__custom__";
                    setCustomModelDraft((prev) => ({
                      ...prev,
                      provider,
                      presetModel: defaultPreset,
                      customModel: "",
                    }));
                  }}
                >
                  {MODEL_PROVIDER_OPTIONS.map((provider) => (
                    <option key={provider} value={provider}>
                      {provider}
                    </option>
                  ))}
                </SelectControl>
              </div>

              <div className="space-y-2">
                <FieldLabel required>模型</FieldLabel>
                {PROVIDER_MODEL_OPTIONS[customModelDraft.provider].length > 0 ? (
                  <SelectControl
                    value={customModelDraft.presetModel}
                    onChange={(value) =>
                      setCustomModelDraft((prev) => ({
                        ...prev,
                        presetModel: value,
                        customModel: value === "__custom__" ? prev.customModel : "",
                      }))
                    }
                  >
                    {PROVIDER_MODEL_OPTIONS[customModelDraft.provider].map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                    <option value="__custom__">自定义输入</option>
                  </SelectControl>
                ) : null}

                {(PROVIDER_MODEL_OPTIONS[customModelDraft.provider].length === 0 ||
                  customModelDraft.presetModel === "__custom__") && (
                  <Input
                    value={customModelDraft.customModel}
                    onChange={(event) =>
                      setCustomModelDraft((prev) => ({ ...prev, customModel: event.target.value }))
                    }
                    placeholder="输入模型名称"
                  />
                )}
              </div>

              <div className="space-y-2">
                <FieldLabel required>API 密钥</FieldLabel>
                <Input
                  type="password"
                  value={customModelDraft.apiKey}
                  onChange={(event) =>
                    setCustomModelDraft((prev) => ({ ...prev, apiKey: event.target.value }))
                  }
                  placeholder="输入 API 密钥"
                />
              </div>

              <div className="space-y-2">
                <FieldLabel>Base URL</FieldLabel>
                <Input
                  value={customModelDraft.baseUrl}
                  onChange={(event) =>
                    setCustomModelDraft((prev) => ({ ...prev, baseUrl: event.target.value }))
                  }
                  placeholder="可选，兼容自定义接口"
                />
              </div>

              <div className="flex justify-end">
                <Button
                  type="button"
                  variant="primary"
                  onClick={saveCustomModel}
                  disabled={
                    !(customModelDraft.presetModel === "__custom__"
                      ? customModelDraft.customModel.trim()
                      : customModelDraft.presetModel.trim()) || !customModelDraft.apiKey.trim()
                  }
                >
                  添加模型
                </Button>
              </div>
            </div>
          </Modal>
        </main>
      </div>
    </AuthGuard>
  );
}

function SettingsSection({
  title,
  description,
  collapsed,
  onToggle,
  children,
}: {
  title: string;
  description: string;
  collapsed: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-start justify-between gap-4 text-left"
      >
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">{title}</h2>
          {description ? (
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">{description}</p>
          ) : null}
        </div>
        <span
          className={`mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] text-[var(--text-muted)] transition-transform ${
            collapsed ? "" : "rotate-180"
          }`}
        >
          <ChevronDown size={14} />
        </span>
      </button>
      {!collapsed && <div className="mt-4">{children}</div>}
    </section>
  );
}

function PreferenceRow({
  title,
  description,
  children,
  stacked,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  stacked?: boolean;
}) {
  return (
    <div
      className={`max-w-[720px] rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3 ${
        stacked
          ? "space-y-4"
          : "flex flex-col gap-3 lg:grid lg:grid-cols-[190px_minmax(0,1fr)] lg:items-center lg:gap-5"
      }`}
    >
      <div className="max-w-[220px]">
        <p className="text-sm font-medium text-[var(--text-primary)]">{title}</p>
        {description ? <p className="mt-1 text-xs leading-4.5 text-[var(--text-muted)]">{description}</p> : null}
      </div>
      <div className={stacked ? "" : "lg:justify-self-end"}>{children}</div>
    </div>
  );
}

function ModelOptionCard({
  title,
  subtitle,
  badge,
  active,
  onClick,
  action,
}: {
  title: string;
  subtitle: string;
  badge?: string;
  active: boolean;
  onClick: () => void;
  action?: React.ReactNode;
}) {
  return (
    <div
      className={`flex w-full max-w-[720px] items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-left transition-all ${
        active
          ? "border-emerald-500/40 bg-emerald-500/10 shadow-[0_0_0_1px_rgba(16,185,129,0.12)]"
          : "border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--border-strong)]"
      }`}
    >
      <button type="button" onClick={onClick} className="min-w-0 flex-1 text-left">
        <div className="flex items-center gap-2">
          <p className="truncate text-sm font-semibold text-[var(--text-primary)]">{title}</p>
          {badge ? (
            <span className="rounded-full border border-[var(--border)] px-2 py-0.5 text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
              {badge}
            </span>
          ) : null}
        </div>
        <p className="mt-1 text-xs text-[var(--text-muted)]">{subtitle}</p>
      </button>
      <div className="flex items-center gap-2">
        {action}
        {active ? (
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-300">
            <Check size={16} />
          </span>
        ) : null}
      </div>
    </div>
  );
}

function FieldLabel({
  children,
  required,
}: {
  children: React.ReactNode;
  required?: boolean;
}) {
  return (
    <label className="block text-sm font-medium text-[var(--text-primary)]">
      {required ? <span className="mr-1 text-rose-400">*</span> : null}
      {children}
    </label>
  );
}

function SelectControl({
  value,
  onChange,
  children,
}: {
  value: string;
  onChange: (value: string) => void;
  children: React.ReactNode;
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="flex h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-3.5 py-2.5 text-sm text-[var(--text-primary)] shadow-sm outline-none transition-colors hover:border-[var(--border-strong)] focus:border-[var(--accent)]"
    >
      {children}
    </select>
  );
}

function ActionButton({
  children,
  onClick,
  disabled,
  variant,
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant: "primary" | "ghost";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-medium transition-all ${
        variant === "primary"
          ? "border-transparent bg-[var(--accent)] text-white shadow-[0_10px_24px_var(--accent-glow)] hover:bg-[var(--accent-strong)]"
          : "border-[var(--border)] bg-[var(--bg-panel)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
      } ${disabled ? "cursor-not-allowed opacity-50" : ""}`}
    >
      {children}
    </button>
  );
}

function BooleanControl({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!enabled)}
      className={`inline-flex min-w-[80px] items-center justify-center rounded-xl border px-3 py-1.5 text-xs font-medium transition-all ${
        enabled
          ? "border-emerald-500/40 bg-emerald-500/12 text-emerald-300"
          : "border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)]"
      }`}
    >
      {enabled ? "开启" : "关闭"}
    </button>
  );
}

function SegmentedControl<T extends string | number>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: readonly T[];
  onChange: (value: T) => void;
}) {
  return (
    <div className="inline-flex flex-wrap items-center justify-end gap-1.5 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-1.5">
      {options.map((option) => {
        const active = value === option;
        return (
          <button
            key={String(option)}
            type="button"
            onClick={() => onChange(option)}
            className={`rounded-xl px-2.5 py-1.5 text-xs font-medium transition-all ${
              active
                ? "bg-[var(--accent)] text-white shadow-[0_10px_24px_var(--accent-glow)]"
                : "text-[var(--text-muted)] hover:bg-[var(--bg-panel)] hover:text-[var(--text-primary)]"
            }`}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}
