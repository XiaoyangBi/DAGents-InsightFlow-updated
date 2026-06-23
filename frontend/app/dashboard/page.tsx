"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { useWorkflows, useCreateWorkflow } from "@/lib/use-workflow";
import { AuthGuard } from "@/components/auth/auth-guard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { WorkflowCard } from "@/components/dashboard/workflow-card";
import { BentoGrid } from "@/components/dashboard/bento-grid";
import { EmptyState } from "@/components/shared/empty-state";
import Link from "next/link";
import { Plus, LogOut, Settings, Search, Brain } from "lucide-react";
import type { WorkflowStatus } from "@/types/workflow";

const STATUS_FILTERS: Array<{ label: string; value: WorkflowStatus | "all" }> = [
  { label: "全部", value: "all" },
  { label: "运行中", value: "running" },
  { label: "配置中", value: "configuring" },
  { label: "已完成", value: "completed" },
  { label: "失败", value: "failed" },
];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { data: workflows, isLoading, isError, error, refetch, isFetching } = useWorkflows();
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const createWorkflow = useCreateWorkflow();
  const router = useRouter();

  const handleCreate = async () => {
    if (creating) return;
    setCreating(true);
    try {
      const result = await createWorkflow.mutateAsync({ title: "未命名分析" });
      router.push(`/workflows/${result.workflow_id}`);
    } catch {
      setCreating(false);
    }
  };

  const runningCount = (workflows ?? []).filter((w) => w.status === "running").length;
  const configuringCount = (workflows ?? []).filter((w) => w.status === "configuring").length;
  const normalizedQuery = searchQuery.trim().toLowerCase();

  const filtered = useMemo(() => (
    (workflows ?? []).filter((w) => {
      const matchesStatus = statusFilter === "all" || w.status === statusFilter;
      const haystack = `${w.title} ${w.current_phase ?? ""}`.toLowerCase();
      const matchesSearch = !normalizedQuery || haystack.includes(normalizedQuery);
      return matchesStatus && matchesSearch;
    })
  ), [workflows, statusFilter, normalizedQuery]);

  return (
    <AuthGuard>
      <div className="min-h-screen" style={{ backgroundColor: "var(--bg-primary)" }}>
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] shadow-sm">
                <Image
                  src="/insightflow-mark.svg"
                  alt="DAGents-InsightFlow"
                  width={36}
                  height={36}
                  className="h-9 w-9"
                  priority
                />
              </div>
              <div>
                <h1 className="text-sm font-bold text-[var(--text-primary)]" data-display="true">DAGents-InsightFlow</h1>
                {user && <p className="text-xs text-[var(--text-muted)]">{user.username}</p>}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                onClick={handleCreate}
                disabled={creating}
                className="text-xs gap-1.5"
                size="sm"
                variant="primary"
              >
                {creating ? <Spinner size={12} /> : <Plus size={14} />} 新建分析
              </Button>
              <Link
                href="/memory"
                className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-3 py-2 text-xs font-medium text-[var(--text-secondary)] shadow-sm hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
              >
                <Brain size={14} /> 记忆中心
              </Link>
              <Link href="/settings" className="rounded-xl border border-transparent p-2 text-[var(--text-muted)] hover:border-[var(--border)] hover:bg-[var(--bg-card)] hover:text-[var(--text-primary)]">
                <Settings size={14} />
              </Link>
              <button onClick={logout} className="rounded-xl border border-transparent p-2 text-[var(--text-muted)] hover:border-[var(--border)] hover:bg-[var(--bg-card)] hover:text-[var(--text-primary)]">
                <LogOut size={14} />
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-6xl px-6 py-8">
          <section className="mb-8 rounded-[28px] border border-[var(--border)] bg-[var(--bg-card)] px-6 py-6 shadow-[var(--panel-shadow)] backdrop-blur-xl">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-2xl space-y-3">
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-[var(--accent)]">Workflow Observatory</p>
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold text-[var(--text-primary)] sm:text-4xl" data-display="true">
                    DAGents-InsightFlow
                  </h2>
                  <p className="max-w-lg text-xs leading-6 text-[var(--text-muted)] sm:text-sm">
                    从配置访谈洞见用户的意图，到多 Agent 执行，再到结构化内容沉淀，这里是你的竞品调研中枢，让每一次竞品调研，都像在同一张作战地图上推进。
                  </p>
                </div>
              </div>
              <div className="grid gap-3 text-sm text-[var(--text-secondary)] sm:grid-cols-3">
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
                  <div className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">运行中工作流</div>
                  <div className="mt-3 text-2xl leading-none font-semibold text-[var(--text-primary)]" data-display="true">
                    {runningCount}
                  </div>
                </div>
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
                  <div className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">累计分析</div>
                  <div className="mt-3 text-2xl leading-none font-semibold text-[var(--text-primary)]" data-display="true">
                    {(workflows ?? []).length}
                  </div>
                </div>
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
                  <div className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">配置中工作流</div>
                  <div className="mt-3 text-2xl leading-none font-semibold text-[var(--text-primary)]" data-display="true">
                    {configuringCount}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {STATUS_FILTERS.map((f) => (
                <button
                  key={f.value}
                  onClick={() => setStatusFilter(f.value)}
                  className={`rounded-full border px-3.5 py-2 text-xs font-medium transition-all ${
                    statusFilter === f.value
                      ? "border-[var(--accent)] bg-[var(--accent)] text-white shadow-[0_10px_24px_var(--accent-glow)]"
                      : "border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
            <div className="flex items-center justify-end">
              {searchOpen || normalizedQuery ? (
                <div className="relative w-full lg:w-72">
                  <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="搜索分析标题或阶段"
                    className="h-[40px] rounded-full pl-9 pr-10 text-xs"
                    autoFocus
                    onBlur={() => {
                      if (!searchQuery.trim()) setSearchOpen(false);
                    }}
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => {
                        setSearchQuery("");
                        setSearchOpen(false);
                      }}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                    >
                      关闭
                    </button>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setSearchOpen(true)}
                  aria-label="打开搜索"
                  className="flex h-[40px] w-[40px] items-center justify-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] shadow-sm transition-all hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                >
                  <Search size={16} />
                </button>
              )}
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20">
              <Spinner size={24} />
            </div>
          ) : isError ? (
            <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-5 py-6 text-sm text-amber-100">
              <p className="font-medium">首页数据加载失败</p>
              <p className="mt-2 text-xs leading-6 text-amber-100/80">
                {(error as Error | undefined)?.message || "服务暂时没有响应，请稍后重试。"}
              </p>
              <div className="mt-4 flex gap-2">
                <Button onClick={() => refetch()} size="sm" variant="primary">
                  重试
                </Button>
                <Button onClick={handleCreate} disabled={creating} size="sm" variant="outline">
                  {creating ? <Spinner size={12} /> : <Plus size={14} />} 新建分析
                </Button>
              </div>
            </div>
          ) : filtered.length === 0 ? (
            <EmptyState
              title={statusFilter === "all" && !normalizedQuery ? "还没有分析项目" : "没有匹配的工作流"}
              description={normalizedQuery ? "换个关键词试试，或切换上方状态筛选。" : "创建第一个竞品分析任务，启动 AI Agent 协作流程"}
              action={
                <Button onClick={handleCreate} disabled={creating} variant="primary">
                  {creating ? <Spinner size={14} /> : <Plus size={14} />} 新建分析
                </Button>
              }
            />
          ) : (
            <BentoGrid>
              {filtered.map((w) => (
                <WorkflowCard key={w.id} workflow={w} />
              ))}
            </BentoGrid>
          )}
          {!isLoading && !isError && isFetching && (
            <div className="mt-4 text-center text-xs text-[var(--text-muted)]">正在刷新首页数据...</div>
          )}
        </main>

      </div>
    </AuthGuard>
  );
}
