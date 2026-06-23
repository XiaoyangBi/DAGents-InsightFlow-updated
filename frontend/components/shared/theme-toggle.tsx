"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  const isDark = theme === "dark";

  return (
    <div className="flex max-w-[720px] items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] px-4 py-3">
      <div className="max-w-[220px]">
        <p className="text-sm font-medium text-[var(--text-primary)]">主题</p>
        <p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">
          {isDark ? "当前为深色模式" : "当前为浅色模式"}
        </p>
      </div>
      <button
        onClick={() => setTheme(isDark ? "light" : "dark")}
        className={`relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors ${
          isDark
            ? "border-emerald-400/30 bg-emerald-500/90"
            : "border-[var(--border)] bg-[var(--bg-elevated)]"
        }`}
      >
        <span
          className={`inline-flex h-5 w-5 items-center justify-center rounded-full bg-white shadow-sm transition-transform ${
            isDark ? "translate-x-6" : "translate-x-1"
          }`}
        >
          {isDark ? <Moon size={10} className="text-zinc-700" /> : <Sun size={10} className="text-amber-500" />}
        </span>
      </button>
    </div>
  );
}
