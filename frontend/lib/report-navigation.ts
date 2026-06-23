function hashAnchorLabel(label: string) {
  let hash = 0;
  for (const char of label) {
    hash = (hash * 31 + char.codePointAt(0)!) >>> 0;
  }
  return hash.toString(36);
}

export function reportSectionAnchorId(heading: string) {
  return `report-section-${hashAnchorLabel(heading)}`;
}

export function reportSubsectionAnchorId(sectionHeading: string, label: string, occurrenceIndex: number) {
  return `report-subsection-${hashAnchorLabel(`${sectionHeading}::${label}::${occurrenceIndex}`)}`;
}

export function extractReportSubheadings(content: string) {
  return Array.from(content.matchAll(/^\s*\*\*([^*\n]+)\*\*\s*$/gm), (match) => match[1].trim());
}

export function buildReportNavigation(sections: Array<{ heading: string; content: string }>) {
  return sections.map((section) => ({
    heading: section.heading,
    anchorId: reportSectionAnchorId(section.heading),
    subheadings: extractReportSubheadings(section.content).map((label, occurrenceIndex) => ({
      label,
      anchorId: reportSubsectionAnchorId(section.heading, label, occurrenceIndex),
    })),
  }));
}

export function normalizeReportMarkdown(markdown: string) {
  return markdown
    .replace(
      /^[ \t]*\*\*([^*\n]+)\*\*[ \t]*$/gm,
      (_, label: string) => `\n\n**${label.trim()}**\n\n`,
    )
    .replace(/\n{3,}/g, "\n\n");
}
