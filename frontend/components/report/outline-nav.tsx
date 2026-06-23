"use client";

import type { ReportSection } from "@/types/artifact";
import { buildReportNavigation } from "@/lib/report-navigation";

interface Props {
  sections: ReportSection[];
  activeSection: string | null;
  onSelect: (anchorId: string) => void;
}

export function OutlineNav({ sections, activeSection, onSelect }: Props) {
  const navigation = buildReportNavigation(sections);

  return (
    <nav className="sticky top-4 max-h-[calc(100vh-10rem)] space-y-1 overflow-y-auto pr-1">
      <h3 className="text-[11px] text-[var(--text-muted)] uppercase tracking-wider mb-3 font-medium">
        章节导航
      </h3>
      {navigation
        .map((section) => {
          const isActive = activeSection === section.anchorId;
          return (
            <div key={section.heading}>
              <button
                onClick={() => onSelect(section.anchorId)}
                className={`block w-full text-left text-xs py-1.5 pl-3 rounded-lg transition-colors border-l-2 ${
                  isActive
                    ? "border-emerald-500 text-emerald-500 bg-emerald-500/5"
                    : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:border-[var(--border)]"
                }`}
              >
                {section.heading}
              </button>
              {section.subheadings.map((subheading) => {
                const isSubsectionActive = activeSection === subheading.anchorId;
                return (
                  <button
                    key={subheading.anchorId}
                    onClick={() => onSelect(subheading.anchorId)}
                    className={`block w-full text-left text-[11px] py-1 pl-6 rounded-lg transition-colors ${
                      isSubsectionActive
                        ? "text-emerald-500 bg-emerald-500/5"
                        : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                    }`}
                  >
                    {subheading.label}
                  </button>
                );
              })}
            </div>
          );
        })}
    </nav>
  );
}
