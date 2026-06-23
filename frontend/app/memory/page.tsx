"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  Archive,
  ArrowLeft,
  Brain,
  Eye,
  FolderKanban,
  Search,
  Trash2,
} from "lucide-react";

import { AuthGuard } from "@/components/auth/auth-guard";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth-context";
import {
  formatMemoryTime,
  MEMORY_SCOPE_LABELS,
  MEMORY_SOURCE_LABELS,
  MEMORY_TYPE_LABELS,
  MOCK_MEMORY_ITEMS,
  type MemoryCenterItem,
  type MemoryType,
} from "@/lib/memory-center";

const TYPE_FILTERS: Array<{ label: string; value: MemoryType | "all" }> = [
  { label: "全部记忆", value: "all" },
  { label: "用户偏好", value: "user_preference" },
  { label: "产品画像", value: "product_profile" },
  { label: "功能焦点", value: "feature_focus" },
  { label: "研究目标", value: "research_goal" },
  { label: "已确认结论", value: "confirmed_conclusion" },
];

export default function MemoryCenterPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<MemoryCenterItem[]>(MOCK_MEMORY_ITEMS);
  const [typeFilter, setTypeFilter] = useState<MemoryType | "all">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [showMuted, setShowMuted] = useState(true);
  const [selectedId, setSelectedId] = useState<string>(MOCK_MEMORY_ITEMS[0]?.id ?? "");

  const filteredItems = useMemo(() => {
    const keyword = searchQuery.trim().toLowerCase();
    return items.filter((item) => {
      if (!showMuted && item.status === "muted") return false;
      if (typeFilter !== "all" && item.memoryType !== typeFilter) return false;
      if (!keyword) return true;
      const haystack = [
        item.title,
        item.content,
        item.summary,
        item.targetProduct,
        item.researchThread,
        item.tags.join(" "),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(keyword);
    });
  }, [items, searchQuery, showMuted, typeFilter]);

  const selected =
    filteredItems.find((item) => item.id === selectedId) ?? filteredItems[0] ?? null;
  const activeCount = items.filter((item) => item.status === "active").length;
  const mutedCount = items.filter((item) => item.status === "muted").length;

  const handleDelete = (memoryId: string) => {
    setItems((prev) => prev.filter((item) => item.id !== memoryId));
    if (selectedId === memoryId) {
      setSelectedId("");
    }
  };

  const handleToggleMuted = (memoryId: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === memoryId
          ? { ...item, status: item.status === "muted" ? "active" : "muted" }
          : item
      )
    );
  };

  return (
    <AuthGuard>
      <div className="min-h-screen" style={{ backgroundColor: "var(--bg-primary)" }}>
        <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="rounded-xl border border-transparent p-2 text-[var(--text-muted)] hover:border-[var(--border)] hover:bg-[var(--bg-card)] hover:text-[var(--text-primary)]"
              >
                <ArrowLeft size={16} />
              </Link>
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] shadow-sm">
                <Brain size={18} className="text-[var(--accent)]" />
              </div>
              <div>
                <p className="text-[11px] font-medium uppercase tracking-[0.24em] text-[var(--accent)]">
                  Memory Center
                </p>
                <h1 className="text-sm font-bold text-[var(--text-primary)]" data-display="true">
                  你的产品研究记忆档案
                </h1>
              </div>
            </div>
            {user ? <p className="text-xs text-[var(--text-muted)]">{user.username}</p> : null}
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-6 py-8">
          <section className="mb-6 rounded-[28px] border border-[var(--border)] bg-[var(--bg-card)] px-6 py-5 shadow-[var(--panel-shadow)] backdrop-blur-xl">
            <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
              <div className="max-w-3xl space-y-2">
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-[var(--accent)]">
                  Personal Research Archive
                </p>
                <h2 className="text-2xl font-bold text-[var(--text-primary)] sm:text-3xl" data-display="true">
                  这里是系统当前保留的长期记忆。
                </h2>
                <p className="max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
                  只保留会跨会话影响分析的内容。点开一条即可查看完整细节。
                </p>
              </div>
              <div className="grid gap-3 text-sm text-[var(--text-secondary)] sm:grid-cols-2">
                <SummaryStat label="活跃记忆" value={activeCount} icon={<Brain size={15} />} />
                <SummaryStat label="静音记忆" value={mutedCount} icon={<Archive size={15} />} />
              </div>
            </div>
          </section>

          <section className="mb-6 grid gap-3 rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--card-shadow)] md:grid-cols-[1.4fr_auto] md:items-center">
            <div className="relative">
              <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
              <Input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="搜索记忆、标签或产品"
                className="pl-9"
              />
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2">
              <TypeTabs value={typeFilter} onChange={setTypeFilter} />
            </div>
          </section>

          <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
            <section className="space-y-4">
              <div className="flex items-center justify-between px-1">
                <p className="text-xs text-[var(--text-muted)]">
                  {filteredItems.length} 条记忆
                </p>
                <Button
                  variant={showMuted ? "outline" : "primary"}
                  size="sm"
                  onClick={() => setShowMuted((prev) => !prev)}
                >
                  <Archive size={14} /> {showMuted ? "隐藏静音" : "显示静音"}
                </Button>
              </div>
              {filteredItems.length === 0 ? (
                <div className="rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] shadow-[var(--card-shadow)]">
                  <EmptyState
                    title="没有匹配的记忆"
                    description="换个关键词或类型试试。"
                  />
                </div>
              ) : (
                filteredItems.map((item) => (
                  <MemoryCard
                    key={item.id}
                    item={item}
                    selected={selected?.id === item.id}
                    onSelect={() => setSelectedId(item.id)}
                    onDelete={() => handleDelete(item.id)}
                    onToggleMuted={() => handleToggleMuted(item.id)}
                  />
                ))
              )}
            </section>

            <aside className="xl:sticky xl:top-24 xl:h-fit">
              {selected ? (
                <section className="rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] p-5 shadow-[var(--panel-shadow)]">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--accent)]">
                        当前选中
                      </p>
                      <h3 className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{selected.title}</h3>
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.14em] ${
                        selected.status === "active"
                          ? "bg-emerald-500/12 text-emerald-500 dark:text-emerald-300"
                          : "bg-amber-500/12 text-amber-600 dark:text-amber-300"
                      }`}
                    >
                      {selected.status === "active" ? "Active" : "Muted"}
                    </span>
                  </div>

                  <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                    <DetailRow label="记忆类型" value={MEMORY_TYPE_LABELS[selected.memoryType]} />
                    <DetailRow label="来源" value={MEMORY_SOURCE_LABELS[selected.source]} />
                    <DetailRow label="层级" value={MEMORY_SCOPE_LABELS[selected.scope]} />
                    <DetailRow label="最近更新时间" value={formatMemoryTime(selected.updatedAt)} />
                    {selected.targetProduct ? <DetailRow label="关联产品" value={selected.targetProduct} /> : null}
                    {selected.researchThread ? <DetailRow label="研究线程" value={selected.researchThread} /> : null}
                  </div>

                  <div className="mt-5 rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
                    <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-[var(--text-muted)]">
                      记忆正文
                    </p>
                    <p className="mt-3 text-sm leading-7 text-[var(--text-secondary)]">{selected.content}</p>
                  </div>

                  <div className="mt-5 rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] p-4">
                    <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-[var(--text-muted)]">
                      标签索引
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {selected.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-2.5 py-1 text-[11px] text-[var(--text-secondary)]"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-5 rounded-2xl border border-dashed border-[var(--border-strong)] bg-[var(--bg-accent-soft)] p-4 text-xs leading-6 text-[var(--text-secondary)]">
                    <div className="flex items-center gap-2 text-[var(--text-primary)]">
                      <Eye size={14} className="text-[var(--accent)]" />
                      <span className="font-medium">这条记忆将如何影响系统</span>
                    </div>
                    <p className="mt-2">
                      后续进入分析和报告节点时，这条记忆会作为 `memory_context` 的一部分被注入。
                    </p>
                  </div>
                </section>
              ) : (
                <section className="rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] p-5 shadow-[var(--panel-shadow)]">
                  <EmptyState
                    title="还没有选中记忆"
                    description="从中间的档案卡片里选择一条记忆，这里会显示它的完整内容和影响范围。"
                  />
                </section>
              )}
            </aside>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}

function SummaryStat({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
        <span className="text-[var(--accent)]">{icon}</span>
        {label}
      </div>
      <div className="mt-3 text-2xl font-semibold leading-none text-[var(--text-primary)]" data-display="true">
        {value}
      </div>
    </div>
  );
}

function MemoryCard({
  item,
  selected,
  onSelect,
  onDelete,
  onToggleMuted,
}: {
  item: MemoryCenterItem;
  selected: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onToggleMuted: () => void;
}) {
  return (
    <article
      onClick={onSelect}
      className={`rounded-3xl border p-5 shadow-[var(--card-shadow)] transition-all ${
        selected
          ? "border-[var(--accent)] bg-[var(--bg-card)] shadow-[0_22px_48px_var(--accent-glow)]"
          : "border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] hover:shadow-[var(--card-shadow-hover)]"
      } cursor-pointer`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-[var(--bg-accent-soft)] px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.16em] text-[var(--accent)]">
              {MEMORY_TYPE_LABELS[item.memoryType]}
            </span>
            <span className="rounded-full border border-[var(--border)] px-2.5 py-1 text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
              {MEMORY_SCOPE_LABELS[item.scope]}
            </span>
            {item.explicit ? (
              <span className="rounded-full bg-blue-500/10 px-2.5 py-1 text-[10px] uppercase tracking-[0.16em] text-blue-600 dark:text-blue-300">
                显式确认
              </span>
            ) : null}
          </div>
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">{item.title}</h3>
          <p className="max-w-3xl text-sm leading-6 text-[var(--text-secondary)]">{item.summary}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              onToggleMuted();
            }}
            className="rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] px-3 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
          >
            {item.status === "muted" ? "重新启用" : "静音"}
          </button>
          <button
            type="button"
            onClick={(event) => {
              event.stopPropagation();
              onDelete();
            }}
            className="rounded-xl border border-rose-500/20 bg-rose-500/10 px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-500/15 dark:text-rose-300"
          >
            <span className="inline-flex items-center gap-1.5">
              <Trash2 size={13} /> 删除
            </span>
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] text-[var(--text-muted)]">
        <span>{MEMORY_SOURCE_LABELS[item.source]}</span>
        <span>·</span>
        <span>{formatMemoryTime(item.updatedAt)}</span>
        <span>·</span>
        <span>{freshnessLabel(item.freshness)}</span>
        {item.targetProduct ? (
          <>
            <span>·</span>
            <span className="inline-flex items-center gap-1">
              <FolderKanban size={12} /> {item.targetProduct}
            </span>
          </>
        ) : null}
      </div>
    </article>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
      <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</div>
      <div className="mt-2 text-sm font-medium text-[var(--text-primary)]">{value}</div>
    </div>
  );
}

function freshnessLabel(value: MemoryCenterItem["freshness"]) {
  if (value === "recent") return "最近更新";
  if (value === "stable") return "稳定记忆";
  return "待复核";
}

function TypeTabs({
  value,
  onChange,
}: {
  value: MemoryType | "all";
  onChange: (value: MemoryType | "all") => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {TYPE_FILTERS.map((filter) => {
        const active = value === filter.value;
        return (
          <button
            key={filter.value}
            type="button"
            onClick={() => onChange(filter.value)}
            className={`rounded-full border px-3 py-2 text-xs font-medium transition-all ${
              active
                ? "border-[var(--accent)] bg-[var(--accent)] text-white shadow-[0_10px_24px_var(--accent-glow)]"
                : "border-[var(--border)] bg-[var(--bg-panel)] text-[var(--text-muted)] hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
            }`}
          >
            {filter.label}
          </button>
        );
      })}
    </div>
  );
}
