"use client";

"use client";

import Link from "next/link";
import { RegisterForm } from "@/components/auth/register-form";
import { Sparkles } from "lucide-react";

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-[20px] border border-[var(--border)] bg-[var(--bg-card)] shadow-sm">
            <Sparkles size={22} className="text-[var(--accent)]" />
          </div>
          <p className="text-[11px] font-medium uppercase tracking-[0.24em] text-[var(--accent)]">Build Your Observatory</p>
          <h1 className="mt-2 text-3xl font-semibold text-[var(--text-primary)]" data-display="true">创建账号</h1>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">建立你的长期分析空间，把竞品洞察、工作流和报告沉淀到同一个界面里。</p>
        </div>
        <div className="rounded-[28px] border border-[var(--border)] bg-[var(--bg-card)] p-6 shadow-[var(--panel-shadow)] backdrop-blur-xl">
          <RegisterForm />
        </div>
        <p className="text-center text-xs text-[var(--text-muted)]">
          已有账号？{" "}
          <Link href="/auth/login" className="font-medium text-[var(--accent)] hover:underline">
            登录
          </Link>
        </p>
      </div>
    </div>
  );
}
