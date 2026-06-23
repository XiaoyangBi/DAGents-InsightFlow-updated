import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "DAGents-InsightFlow",
  description: "AI-Native Workflow Observatory — 竞品分析多 Agent 协作系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="zh"
      className="h-full antialiased"
      style={
        {
          "--font-geist-sans":
            '"Inter", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif',
          "--font-geist-mono": '"JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace',
          "--font-space-grotesk":
            '"Inter", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif',
        } as React.CSSProperties
      }
      suppressHydrationWarning
    >
      <body
        className="min-h-full flex flex-col"
        style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-primary)" }}
        suppressHydrationWarning
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
