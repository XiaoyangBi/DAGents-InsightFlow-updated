"use client";

import { useEffect, useId, useState } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  chart: string;
}

export function MermaidDiagram({ chart }: Props) {
  const [svg, setSvg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [stopped, setStopped] = useState(false);
  const elementId = useId().replace(/:/g, "");

  useEffect(() => {
    setStopped(false);
    setSvg("");
    setError(null);
  }, [chart]);

  useEffect(() => {
    let active = true;

    async function renderChart() {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "loose",
          theme: "dark",
        });
        const { svg: rendered } = await mermaid.render(`mermaid-${elementId}`, chart.trim());
        if (!active) return;
        setSvg(rendered);
        setError(null);
      } catch (err) {
        if (!active) return;
        const message = err instanceof Error ? err.message : "流程图渲染失败";
        setError(message);
        setSvg("");
      }
    }

    if (chart.trim() && !stopped) {
      void renderChart();
    }

    return () => {
      active = false;
    };
  }, [chart, elementId, stopped]);

  if (stopped) {
    return (
      <div className="my-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <p className="text-sm font-medium text-[var(--text-primary)]">已停止 canvas 生成</p>
          <Button type="button" size="sm" variant="outline" onClick={() => setStopped(false)}>
            重新生成
          </Button>
        </div>
        <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-[var(--text-secondary)]">{chart}</pre>
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4">
        <p className="mb-2 text-sm font-medium text-amber-200">流程图渲染失败</p>
        <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-amber-50">{chart}</pre>
        <p className="mt-2 text-xs text-amber-200/80">{error}</p>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="my-4 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-[var(--text-muted)]">正在渲染流程图...</p>
          <Button type="button" size="sm" variant="outline" onClick={() => setStopped(true)}>
            停止生成
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="my-4 overflow-x-auto rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-4"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}
