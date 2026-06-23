import * as React from "react";
import { cn } from "@/lib/cn";

const variants = {
  default: "border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm hover:border-[var(--border-strong)] hover:bg-[var(--bg-panel)]",
  primary: "bg-[var(--accent)] text-white shadow-[0_14px_32px_var(--accent-glow)] hover:-translate-y-0.5 hover:bg-[var(--accent-strong)]",
  destructive: "bg-[var(--danger)] text-white shadow-[0_12px_24px_rgba(225,29,72,0.18)] hover:-translate-y-0.5 hover:brightness-110",
  ghost: "bg-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] hover:text-[var(--text-primary)]",
  outline: "border border-[var(--border)] bg-transparent text-[var(--text-primary)] hover:border-[var(--border-strong)] hover:bg-[var(--bg-panel)]",
} as const;

const sizes = {
  sm: "h-8 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-sm",
  icon: "h-9 w-9",
} as const;

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants;
  size?: keyof typeof sizes;
}

export function Button({
  className,
  variant = "default",
  size = "md",
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-200",
        "focus-visible:ring-[var(--focus-ring)] focus-visible:border-transparent",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled}
      {...props}
    />
  );
}
