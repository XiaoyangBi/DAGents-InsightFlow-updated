"use client";

import Link from "next/link";
import Image from "next/image";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center overflow-hidden rounded-[20px] border border-[var(--border)] bg-[var(--bg-card)] shadow-sm">
            <Image
              src="/insightflow-mark.svg"
              alt="DAGents-InsightFlow"
              width={56}
              height={56}
              className="h-14 w-14"
              priority
            />
          </div>
          <p className="text-[11px] font-medium uppercase tracking-[0.24em] text-[var(--accent)]">DAGents-InsightFlow</p>
          <h1 className="mt-2 text-3xl font-semibold text-[var(--text-primary)]" data-display="true">登录</h1>
          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">进入你的竞品调研中枢</p>
        </div>
        <div className="rounded-[28px] border border-[var(--border)] bg-[var(--bg-card)] p-6 shadow-[var(--panel-shadow)] backdrop-blur-xl">
          <LoginForm />
        </div>
        <p className="text-center text-xs text-[var(--text-muted)]">
          还没有账号？{" "}
          <Link href="/auth/register" className="font-medium text-[var(--accent)] hover:underline">
            注册
          </Link>
        </p>
      </div>
    </div>
  );
}
