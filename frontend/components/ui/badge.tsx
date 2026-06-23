import * as React from "react";
import { cn } from "@/lib/cn";

const variants = {
  default: "border-[var(--border)] bg-[var(--bg-panel)] text-[var(--text-secondary)]",
  success: "border-emerald-500/20 bg-emerald-500/10 text-emerald-500 dark:text-emerald-300",
  warning: "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-300",
  danger: "border-rose-500/20 bg-rose-500/10 text-rose-500 dark:text-rose-300",
  info: "border-blue-500/20 bg-blue-500/10 text-blue-500 dark:text-blue-300",
  indigo: "border-indigo-500/20 bg-indigo-500/10 text-indigo-500 dark:text-indigo-300",
} as const;

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: keyof typeof variants;
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-[0.01em]",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
