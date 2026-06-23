"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Spinner } from "@/components/ui/spinner";
import type { InterviewMessage } from "@/types/interview";

interface Props {
  messages: InterviewMessage[];
  isStreaming: boolean;
  enableQuickReply?: boolean;
  onQuickReply?: (text: string) => void;
}

export function ChatStream({ messages, isStreaming, enableQuickReply = false, onQuickReply }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const visibleMessages = messages.filter(
    (msg, index) => Boolean(msg.content) || (isStreaming && index === messages.length - 1),
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto p-6">
      {visibleMessages.map((msg, i) => (
        <div key={i} className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`max-w-[75%] overflow-hidden rounded-[24px] text-sm leading-relaxed shadow-sm backdrop-blur-sm ${
              msg.role === "user"
                ? "rounded-tr-lg border border-emerald-400/20 bg-[var(--accent)] text-[#04111c] shadow-[0_18px_40px_var(--accent-glow)]"
                : "rounded-tl-lg border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-primary)]"
            }`}
          >
            {msg.content ? (
              msg.role === "user" ? (
                <div className="space-y-2 px-5 py-4">
                  <span className="block text-[10px] font-medium uppercase tracking-[0.16em] text-[#0a4b3e]/70">
                    你的输入
                  </span>
                  <p className="leading-relaxed font-medium">{msg.content}</p>
                </div>
              ) : (
                <div className="space-y-3 px-5 py-4">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex h-6 items-center rounded-full border border-[var(--border)] bg-[var(--bg-panel)] px-2.5 text-[10px] font-medium uppercase tracking-[0.16em] text-[var(--text-muted)]">
                      Agent 回应
                    </span>
                  </div>
                  <div className="
                  prose prose-sm max-w-none dark:prose-invert
                  prose-p:leading-[1.85] prose-p:my-3
                  prose-headings:font-semibold prose-headings:tracking-tight
                  prose-h2:text-base prose-h2:mt-6 prose-h2:mb-4
                  prose-h3:text-sm prose-h3:mt-5 prose-h3:mb-3
                  prose-strong:font-medium
                  prose-li:my-2 prose-li:leading-[1.85]
                  prose-ul:my-4 prose-ol:my-4
                  prose-ul:list-none prose-ul:pl-0
                  prose-ol:list-none prose-ol:pl-0
                  prose-code:text-emerald-500 dark:prose-code:text-emerald-300 dark:prose-code:bg-zinc-800 prose-code:bg-[var(--bg-elevated)] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-normal prose-code:text-xs
                  space-y-3
                ">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      li: ({ children }) => {
                        const text = extractText(children);
                        if (enableQuickReply && text.trim()) {
                          return (
                            <QuickReplyCard text={text} onClick={() => onQuickReply?.(text)}>
                              <div className="text-sm text-[var(--text-secondary)] leading-[1.85]">{children}</div>
                            </QuickReplyCard>
                          );
                        }
                        return (
                          <ReadableListItem>
                            <div className="text-sm text-[var(--text-secondary)] leading-[1.85]">{children}</div>
                          </ReadableListItem>
                        );
                      },
                      p: ({ children }) => (
                        <p className="leading-[1.9] text-[var(--text-primary)]">{children}</p>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote className="rounded-r-2xl border-l-2 border-[var(--accent)]/60 bg-[var(--bg-panel)] px-4 py-3 text-[var(--text-secondary)]">
                          {children}
                        </blockquote>
                      ),
                      pre: ({ children }) => (
                        <pre className="overflow-x-auto rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] p-4 text-xs leading-6 text-[var(--text-primary)]">
                          {children}
                        </pre>
                      ),
                      code: ({ className, children }) => {
                        const isBlock = Boolean(className);
                        if (isBlock) {
                          return <code className={className}>{children}</code>;
                        }
                        return (
                          <code className="rounded-md bg-[var(--bg-elevated)] px-1.5 py-0.5 text-[11px] text-emerald-500 dark:text-emerald-300">
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
                </div>
              )
            ) : (
              isStreaming && i === visibleMessages.length - 1 && (
                <div className="flex items-center gap-2 px-5 py-4 text-[var(--text-muted)]">
                  <Spinner size={14} />
                  <span className="text-xs">AI 正在思考...</span>
                </div>
              )
            )}
          </div>
        </div>
      ))}
      {visibleMessages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] shadow-sm">
            <svg className="w-6 h-6 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <p className="text-sm text-[var(--text-secondary)] font-medium">开始对话</p>
          <p className="text-xs text-[var(--text-muted)]">AI 将通过对话引导你完成竞品分析配置</p>
        </div>
      )}
    </div>
  );
}

function QuickReplyCard({
  text,
  onClick,
  children,
}: {
  text: string;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const [selected, setSelected] = useState(false);

  const handleClick = () => {
    setSelected(true);
    onClick?.();
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`mb-2 w-full rounded-2xl border p-4 text-left shadow-sm transition-all ${
        selected
          ? "border-emerald-400/35 bg-emerald-500/12"
          : "border-[var(--border)] bg-[var(--bg-panel)] hover:-translate-y-0.5 hover:border-[var(--accent)]/35 hover:bg-[var(--bg-elevated)]"
      }`}
      aria-label={`使用建议：${text}`}
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="inline-flex h-6 items-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-2.5 text-[10px] font-medium uppercase tracking-[0.16em] text-[var(--text-muted)]">
          Quick Reply
        </span>
        <span className="text-[10px] text-[var(--text-muted)]">点击直接发送</span>
      </div>
      <div className="flex items-start gap-3">
        <span className="mt-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] text-[10px] font-medium text-[var(--text-muted)]">
          •
        </span>
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </button>
  );
}

/* ─── Readable List Item ─── */
function ReadableListItem({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-2 w-full rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] p-4 text-left shadow-sm">
      <div className="flex items-start gap-3">
        <span className="mt-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] text-[10px] font-medium text-[var(--text-muted)]">
          •
        </span>
        <div className="min-w-0 flex-1">
          {children}
        </div>
      </div>
    </div>
  );
}

function extractText(children: React.ReactNode): string {
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(extractText).join(" ");
  if (children && typeof children === "object" && "props" in children) {
    return extractText((children as { props: { children?: React.ReactNode } }).props.children);
  }
  return "";
}
