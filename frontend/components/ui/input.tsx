import * as React from "react";
import { cn } from "@/lib/cn";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        "flex h-11 w-full rounded-xl border border-[var(--border)] bg-[var(--bg-card)] px-3.5 py-2.5 text-sm shadow-sm backdrop-blur-sm",
        "text-[var(--text-primary)] placeholder:text-[var(--text-muted)]",
        "hover:border-[var(--border-strong)]",
        "focus-visible:border-[var(--accent)] focus-visible:outline-none focus-visible:ring-[var(--focus-ring)]",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}
