"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { AuthGuard } from "@/components/auth/auth-guard";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import {
  DEFAULT_APP_SETTINGS,
  type AppSettings,
  readAppSettings,
  writeAppSettings,
} from "@/lib/analysis-preferences";
import { ArrowLeft, ChevronDown, RotateCcw, Save, X } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();
  const [savedSettings, setSavedSettings] = useState<AppSettings>(DEFAULT_APP_SETTINGS);
  const [draftSettings, setDraftSettings] = useState<AppSettings>(DEFAULT_APP_SETTINGS);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    appearance: false,
    analysis: false,
    modelData: false,
  });

  useEffect(() => {
    const loaded = readAppSettings();
    setSavedSettings(loaded);
    setDraftSettings(loaded);
  }, []);

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

  return (
    <AuthGuard>
      <div className="min-h-screen" style={{ backgroundColor: "var(--bg-primary)" }}>
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-3">
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
              >
                <ArrowLeft size={18} />
              </Link>
              <h1 className="text-sm font-bold text-[var(--text-primary)]">设置</h1>
            </div>
            {user && (
              <p className="text-xs text-[var(--text-muted)]">{user.username}</p>
            )}
          </div>
        </header>

        <main className="mx-auto max-w-3xl space-y-6 px-6 py-8">
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
            <div className="space-y-4">
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
            description="定义访谈和后续分析默认依赖什么模型、是否联网、是否保留引用和长期记忆。"
            collapsed={collapsed.modelData}
            onToggle={() => toggleSection("modelData")}
          >
            <div className="space-y-4">
              <PreferenceRow title="默认模型" description="当前主要作为前端偏好保存，便于后续接入多模型路由。">
                <SegmentedControl
                  value={draftSettings.modelDataSettings.defaultModel}
                  options={["deepseek-v4-pro", "gpt-4.1", "claude-sonnet-4"]}
                  onChange={(value) =>
                    setDraftSettings((prev) => ({
                      ...prev,
                      modelDataSettings: { ...prev.modelDataSettings, defaultModel: value },
                    }))
                  }
                />
              </PreferenceRow>

              <PreferenceRow title="联网检索" description="决定访谈推荐竞品与后续分析是否优先结合外部公开信息。">
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

              <PreferenceRow title="引用证据" description="控制输出时更偏始终附引用、智能附引用，还是关闭引用偏好。">
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

              <PreferenceRow title="长期记忆沉淀" description="把访谈里抽出的长期追踪对象、核心问题和标签单独写入本地记忆库。">
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

              <PreferenceRow title="中间推理痕迹" description="保留更完整的推理轨迹偏好，便于后续扩展审计与过程复盘。">
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
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-5">
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
          className={`mt-1 inline-flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] text-[var(--text-muted)] transition-transform ${
            collapsed ? "" : "rotate-180"
          }`}
        >
          <ChevronDown size={14} />
        </span>
      </button>
      {!collapsed && <div className="mt-5">{children}</div>}
    </section>
  );
}

function PreferenceRow({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="max-w-xl">
        <p className="text-sm font-medium text-[var(--text-primary)]">{title}</p>
        <p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">{description}</p>
      </div>
      <div className="lg:shrink-0">{children}</div>
    </div>
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
      className={`inline-flex min-w-[88px] items-center justify-center rounded-xl border px-3 py-2 text-xs font-medium transition-all ${
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
    <div className="inline-flex flex-wrap items-center gap-2 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-1.5">
      {options.map((option) => {
        const active = value === option;
        return (
          <button
            key={String(option)}
            type="button"
            onClick={() => onChange(option)}
            className={`rounded-xl px-3 py-2 text-xs font-medium transition-all ${
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
