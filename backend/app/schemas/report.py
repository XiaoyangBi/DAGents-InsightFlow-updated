from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


def _normalize_source_ref(value: object) -> str:
    text = str(value or "").strip()
    # LLM 经常把 URL 包成 `url`、"url" 或 'url'；这里只做外层去壳，
    # 不放宽来源边界，后续仍会与 allowed URLs 做精确匹配。
    while len(text) >= 2:
        if (text.startswith("`") and text.endswith("`")) or (
            text.startswith('"') and text.endswith('"')
        ) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()
            continue
        break
    return text


class ReportSection(BaseModel):
    heading: str
    level: int
    content: str
    source_refs: list[str] = []

    @field_validator("source_refs", mode="before")
    @classmethod
    def normalize_source_refs(cls, value: object) -> list[str]:
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            value = [value]
        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            ref = _normalize_source_ref(item)
            if not ref or ref in seen:
                continue
            seen.add(ref)
            normalized.append(ref)
        return normalized


class Citation(BaseModel):
    index: int
    url: str
    title: str
    access_date: date


class ReportOutput(BaseModel):
    title: str
    executive_summary: str
    sections: list[ReportSection]
    citations: list[Citation]
    full_markdown: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
