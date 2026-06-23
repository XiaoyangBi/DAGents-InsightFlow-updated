"use client";

import React, { Children, isValidElement, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ReportOutput } from "@/types/artifact";
import { MermaidDiagram } from "@/components/report/mermaid-diagram";
import {
  buildReportNavigation,
  normalizeReportMarkdown,
  reportSectionAnchorId,
} from "@/lib/report-navigation";

interface Props {
  report: ReportOutput;
  activeSection: string | null;
  onCitationClick: (index: number) => void;
}

function extractNodeText(node: React.ReactNode): string {
  return Children.toArray(node)
    .map((child) => {
      if (typeof child === "string" || typeof child === "number") {
        return String(child);
      }
      if (isValidElement<{ children?: React.ReactNode }>(child)) {
        return extractNodeText(child.props.children);
      }
      return "";
    })
    .join("")
    .trim();
}

function getStandaloneStrongLabel(children: React.ReactNode) {
  const items = Children.toArray(children).filter(
    (child) => !(typeof child === "string" && child.trim().length === 0),
  );
  if (items.length !== 1) {
    return null;
  }

  const [firstChild] = items;
  if (!isValidElement<{ children?: React.ReactNode }>(firstChild) || firstChild.type !== "strong") {
    return null;
  }

  return extractNodeText(firstChild.props.children) || null;
}

export function ReportViewer({ report, activeSection, onCitationClick }: Props) {
  const navigation = useMemo(() => buildReportNavigation(report.sections), [report.sections]);

  const subsectionAnchorLookup = useMemo(() => {
    return new Map(
      navigation.map((section) => [
        section.heading,
        section.subheadings.map((subheading) => ({
          label: subheading.label,
          anchorId: subheading.anchorId,
        })),
      ]),
    );
  }, [navigation]);

  let currentSectionHeading = "";
  const subsectionCursor = new Map<string, number>();

  return (
    <div className="prose dark:prose-invert max-w-none leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => {
            const match = href?.match(/^#citation-(\d+)$/);
            if (match) {
              return (
                <button
                  onClick={() => onCitationClick(parseInt(match[1]))}
                  className="text-emerald-400 hover:underline cursor-pointer"
                >
                  {children}
                </button>
              );
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline">
                {children}
              </a>
            );
          },
          h2: ({ children, className = "", ...props }) => {
            const heading = extractNodeText(children);
            currentSectionHeading = heading;
            const id = reportSectionAnchorId(heading);
            const isActive = activeSection === id;
            return (
              <h2
                {...props}
                id={id}
                className={`scroll-mt-20 ${isActive ? "text-emerald-300" : ""} ${className}`}
              >
                {children}
              </h2>
            );
          },
          p: ({ children, className = "", ...props }) => {
            const label = getStandaloneStrongLabel(children);
            const subheadings = subsectionAnchorLookup.get(currentSectionHeading) ?? [];
            const nextIndex = subsectionCursor.get(currentSectionHeading) ?? 0;
            const nextSubheading = label ? subheadings[nextIndex] : undefined;
            const id = nextSubheading?.label === label ? nextSubheading.anchorId : undefined;
            const isActive = activeSection === id;

            if (id) {
              subsectionCursor.set(currentSectionHeading, nextIndex + 1);
            }

            return (
              <p
                {...props}
                id={id}
                className={`scroll-mt-20 ${isActive ? "text-emerald-300" : ""} ${className}`}
              >
                {children}
              </p>
            );
          },
          code: ({ className, children }) => {
            const value = String(children).replace(/\n$/, "");
            if (className?.includes("language-mermaid")) {
              return <MermaidDiagram chart={value} />;
            }
            return (
              <code className={className}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => <>{children}</>,
        }}
      >
        {normalizeReportMarkdown(report.full_markdown)}
      </ReactMarkdown>
    </div>
  );
}
