import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.report_agent import (
    ANALYSIS_HEADINGS,
    DECISION_HEADINGS,
    REPORT_HEADINGS,
    SUPPLEMENT_HEADINGS,
    ReportAgent,
    ReportDraft,
    ReportOutline,
    ReportOutlineSection,
    ReportSectionBatch,
)
from app.core.runtime.context import AgentContext
from app.schemas.report import ReportSection


def _make_sections(headings: list[str]) -> list[ReportSection]:
    return [
        ReportSection(
            heading=heading,
            level=2,
            content=(
                "流程说明：\n\n```mermaid\nflowchart LR\n  A[开始] --> B[结束]\n```\n\n证据边界说明。"
                if heading == "关键流程图"
                else f"{heading} content。当前采集结果未覆盖，结论仅作为方向性判断，后续仍需结合更充分证据复核。"
            ),
            source_refs=[],
        )
        for heading in headings
    ]


def _make_batches():
    return [
        ReportSectionBatch(sections=_make_sections(ANALYSIS_HEADINGS)),
        ReportDraft(
            title="Test Report",
            executive_summary="Summary",
            sections=_make_sections(DECISION_HEADINGS),
        ),
        ReportSectionBatch(sections=_make_sections(SUPPLEMENT_HEADINGS)),
    ]


def _make_outline() -> ReportOutline:
    return ReportOutline(
        title="Test Report",
        executive_summary="Summary",
        sections=[
            ReportOutlineSection(
                heading=heading,
                objective=f"{heading} objective",
                key_points=[f"{heading} point"],
                related_artifacts=[],
            )
            for heading in REPORT_HEADINGS
        ],
    )


def _make_light_react_outputs() -> list:
    return [_make_outline(), *[
        ReportSectionBatch(sections=_make_sections([heading]))
        for heading in REPORT_HEADINGS
    ]]


def _make_draft() -> ReportDraft:
    return ReportDraft(
        title="Test Report",
        executive_summary="Summary",
        sections=[
            ReportSection(
                heading="Overview",
                level=2,
                content="Content",
                source_refs=["https://example.com"],
            )
        ],
    )


def _mock_ctx() -> AgentContext:
    return AgentContext(
        workflow_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        node_id="report_writing",
        iteration=0,
        events=SimpleNamespace(
            emit=AsyncMock(),
            progress=AsyncMock(),
            stream_token=AsyncMock(),
        ),
    )


class TestReportAgent:
    @pytest.mark.asyncio
    async def test_partial_source_coverage_still_uses_llm(self):
        agent = ReportAgent()
        ctx = _mock_ctx()
        agent.log_and_broadcast = AsyncMock()
        agent.invoke_structured_llm = AsyncMock(side_effect=_make_light_react_outputs())

        state = {
            "config": {"target_product": "Notion"},
            "raw_data": {
                "Notion": [{"url": "https://example.com", "title": "Notion"}],
                "阿里语雀": [],
            },
            "collection_errors": {
                "__source_coverage__": "Missing source coverage for: 阿里语雀",
            },
            "feature_matrix": {},
            "pricing_comparison": {},
            "user_sentiment": {},
            "swot": {},
        }

        with patch("app.agents.report_agent.llm_is_configured", return_value=True):
            result = await agent.run(state, ctx)

        assert agent.invoke_structured_llm.await_count == 11
        payload = agent.invoke_structured_llm.call_args_list[0].args[1]
        assert payload["source_coverage_issue"] == "Missing source coverage for: 阿里语雀"
        assert payload["collection_errors"]["__source_coverage__"] == "Missing source coverage for: 阿里语雀"
        assert result["report"]["title"] == "Test Report"
        assert len(result["report"]["sections"]) == 10
        assert "# Test Report" in result["report"]["full_markdown"]
        assert "## 行动建议" in result["report"]["full_markdown"]

    @pytest.mark.asyncio
    async def test_report_batch_failure_is_not_converted_to_fallback(self):
        agent = ReportAgent()
        ctx = _mock_ctx()
        agent.log_and_broadcast = AsyncMock()
        agent.invoke_structured_llm = AsyncMock(
            side_effect=[
                _make_outline(),
                ReportSectionBatch(sections=_make_sections([REPORT_HEADINGS[0]])),
                ValueError("invalid structured output"),
            ]
        )

        state = {
            "config": {"target_product": "Notion", "competitors": ["语雀"]},
            "raw_data": {
                "Notion": [{"url": "https://example.com", "title": "Notion"}],
                "语雀": [{"url": "https://example.com/yuque", "title": "语雀"}],
            },
            "feature_matrix": {},
            "pricing_comparison": {},
            "user_sentiment": {},
            "swot": {},
        }

        with patch("app.agents.report_agent.llm_is_configured", return_value=True):
            with pytest.raises(ValueError, match="invalid structured output"):
                await agent.run(state, ctx)

        assert agent.invoke_structured_llm.await_count == 3

    @pytest.mark.asyncio
    async def test_missing_llm_does_not_deliver_generic_fallback(self):
        agent = ReportAgent()
        ctx = _mock_ctx()
        agent.log_and_broadcast = AsyncMock()
        state = {
            "config": {"target_product": "Notion"},
            "raw_data": {"Notion": [{"url": "https://example.com", "title": "Notion"}]},
        }

        with patch("app.agents.report_agent.llm_is_configured", return_value=False):
            with pytest.raises(RuntimeError, match="未生成通用 fallback 报告"):
                await agent.run(state, ctx)

    @pytest.mark.asyncio
    async def test_competitor_resolution_error_stays_insufficient(self):
        agent = ReportAgent()
        ctx = _mock_ctx()
        agent.log_and_broadcast = AsyncMock()
        agent.invoke_structured_llm = AsyncMock(return_value=_make_draft())

        state = {
            "config": {"target_product": "Notion"},
            "raw_data": {
                "Notion": [{"url": "https://example.com", "title": "Notion"}],
            },
            "collection_errors": {
                "__competitor_resolution__": "Only resolved 1 valid competitor(s); at least 2 required before analysis.",
            },
        }

        with patch("app.agents.report_agent.llm_is_configured", return_value=True):
            result = await agent.run(state, ctx)

        agent.invoke_structured_llm.assert_not_called()
        assert "资料不足" in result["report"]["title"]
        assert len(result["report"]["sections"]) == 7
        assert any(section["heading"] == "关键流程图" for section in result["report"]["sections"])

    def test_validate_sections_rejects_missing_heading(self):
        agent = ReportAgent()

        with pytest.raises(ValueError, match="headings mismatch"):
            agent._validate_sections(
                _make_sections(ANALYSIS_HEADINGS[:-1]),
                ANALYSIS_HEADINGS,
                "analysis",
            )

    def test_normalize_section_prevents_inline_heading_style_leak(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="成功与失败原因拆解",
            level=1,
            content="### 成功经验可复用拆解1. 第一项；2. 第二项。### 失败教训需规避拆解1. 第三项。",
            source_refs=[],
        )

        normalized = agent._normalize_section(section)

        assert normalized.level == 2
        assert "###" not in normalized.content
        assert "**成功经验可复用拆解**\n\n1. 第一项" in normalized.content
        assert "\n\n2. 第二项" in normalized.content
        assert "**失败教训需规避拆解**\n\n1. 第三项" in normalized.content

    def test_normalize_section_separates_standalone_bold_subheadings(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="产品定位判断",
            level=2,
            content=(
                "定位判断正文。\n"
                "**定位成立的核心支撑点**\n"
                "1. 第一项。\n\n"
                "2. 第二项。\n"
                "**当前定位下的核心覆盖场景**\n"
                "1. 场景一。"
            ),
            source_refs=[],
        )

        normalized = agent._normalize_section(section)

        assert "定位判断正文。\n\n**定位成立的核心支撑点**\n\n1. 第一项。" in normalized.content
        assert "2. 第二项。\n\n**当前定位下的核心覆盖场景**\n\n1. 场景一。" in normalized.content

    def test_normalize_mermaid_repairs_collapsed_fences_and_edges(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="关键流程图",
            level=2,
            content=(
                "流程说明：```mermaidflowchart LR    A[开始] --> B[检查]    "
                "B --> C[结束]``` 证据边界说明。"
            ),
            source_refs=[],
        )

        normalized = agent._normalize_section(section)
        agent._validate_mermaid_section(normalized)

        assert "\n\n```mermaid\nflowchart LR" in normalized.content
        assert "\n  B --> C[结束]\n```" in normalized.content

    def test_validate_mermaid_rejects_unbalanced_diagram(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="关键流程图",
            level=2,
            content="```mermaid\nflowchart LR\n  A[开始] --> B[结束\n```",
            source_refs=[],
        )

        with pytest.raises(ValueError, match="unbalanced delimiters"):
            agent._validate_mermaid_section(section)

    def test_normalize_mermaid_collapses_multiple_blocks_into_one_valid_block(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="关键流程图",
            level=2,
            content=(
                "流程说明。\n\n"
                "```mermaid\nflowchart LR\n  A[开始] --> B[中间]\n```\n\n"
                "补充说明。\n\n"
                "```mermaid\nflowchart LR\n  X[备用] --> Y[结束]\n```"
            ),
            source_refs=[],
        )

        normalized = agent._normalize_section(section)
        agent._validate_mermaid_section(normalized)

        assert normalized.content.count("```mermaid") == 1
        assert "流程说明" in normalized.content

    def test_normalize_mermaid_injects_fallback_block_when_missing(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="关键流程图",
            level=2,
            content="当前只输出了流程说明，没有合法流程图代码块。",
            source_refs=[],
        )

        normalized = agent._normalize_section(section)
        agent._validate_mermaid_section(normalized)

        assert normalized.content.count("```mermaid") == 1
        assert "flowchart TD" in normalized.content

    def test_validate_sections_rejects_remaining_markdown_heading(self):
        agent = ReportAgent()
        sections = _make_sections(ANALYSIS_HEADINGS)
        sections[0] = sections[0].model_copy(
            update={"content": "正文中意外出现 ### 未规范化标题"}
        )

        with pytest.raises(ValueError, match="unsupported Markdown heading syntax"):
            agent._validate_sections(sections, ANALYSIS_HEADINGS, "analysis")

    def test_report_section_normalizes_wrapped_source_refs(self):
        section = ReportSection(
            heading="结论先行",
            level=2,
            content="结论正文",
            source_refs=[
                " `https://example.com/a` ",
                '"https://example.com/b"',
                "'https://example.com/c'",
                "https://example.com/a",
            ],
        )

        assert section.source_refs == [
            "https://example.com/a",
            "https://example.com/b",
            "https://example.com/c",
        ]

    def test_constrain_section_source_refs_filters_urls_outside_allowlist(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="结论先行",
            level=2,
            content="结论正文",
            source_refs=[
                "https://allowed.example/a",
                "https://not-allowed.example/b",
            ],
        )

        constrained = agent._constrain_section_source_refs(
            section,
            ["https://allowed.example/a"],
        )

        assert constrained.source_refs == ["https://allowed.example/a"]

    def test_constrain_section_source_refs_clears_refs_when_allowlist_empty(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="结论先行",
            level=2,
            content="结论正文",
            source_refs=["https://not-allowed.example/b"],
        )

        constrained = agent._constrain_section_source_refs(section, [])

        assert constrained.source_refs == []

    def test_fallback_report_includes_mermaid_diagram_section(self):
        agent = ReportAgent()
        result = agent._fallback_report(
            "Claude Code",
            {
                "target_product": "Claude Code",
                "competitors": ["Cursor"],
                "focus_dimensions": ["目标用户", "使用场景", "核心问题"],
            },
            {
                "feature_matrix": {},
                "pricing_comparison": {},
                "user_sentiment": {},
                "swot": {},
                "competitor_role_analysis": {},
            },
            [],
        )

        assert any(section.heading == "关键流程图" for section in result.sections)
        assert "```mermaid" in result.full_markdown
        assert "Claude Code vs Cursor" in result.full_markdown

    @pytest.mark.asyncio
    async def test_section_missing_citations_is_backfilled_before_repair(self):
        agent = ReportAgent()
        ctx = _mock_ctx()
        agent.log_and_broadcast = AsyncMock()
        repaired_batch = ReportSectionBatch(
            sections=[
                ReportSection(
                    heading="关键发现",
                    level=2,
                    content="关键发现 content",
                    source_refs=["https://example.com"],
                )
            ]
        )
        agent.invoke_structured_llm = AsyncMock(return_value=repaired_batch)
        outline = _make_outline()
        payload, allowed_urls = agent._build_section_payload(
            heading="关键发现",
            state={
                "feature_matrix": {},
                "pricing_comparison": {},
                "user_sentiment": {},
                "swot": {},
            },
            shared={
                "config": {"target_product": "Notion"},
                "collection_errors": {},
                "source_coverage_issue": None,
            },
            raw_data={
                "Notion": [
                    {
                        "url": "https://example.com",
                        "title": "Notion 功能评测",
                        "snippet": "review comparison",
                        "source_intents": ["overview", "dimension:功能"],
                    }
                ]
            },
            sources={},
            outline=outline.sections[REPORT_HEADINGS.index("关键发现")],
            completed_sections=[],
        )

        repaired = await agent._repair_section_once_if_needed(
            ctx=ctx,
            heading="关键发现",
            section=ReportSection(
                heading="关键发现",
                level=2,
                content="关键发现 content",
                source_refs=[],
            ),
            payload=payload,
            allowed_urls=allowed_urls,
            completed_sections=[],
        )

        assert repaired.source_refs == ["https://example.com"]
        assert agent.invoke_structured_llm.await_count == 0

    def test_build_section_payload_infers_suggested_source_refs_from_artifact_evidence(self):
        agent = ReportAgent()
        outline = _make_outline()
        payload, allowed_urls = agent._build_section_payload(
            heading="竞品范围与角色判断",
            state={
                "competitor_role_analysis": {
                    "items": [{
                        "product": "拼多多",
                        "role": "benchmark",
                        "reason": "角色说明",
                        "evidence_refs": [
                            {"url": "https://example.com/pdd", "title": "拼多多"},
                            {"url": "https://not-allowed.example/other", "title": "其他"},
                        ],
                    }],
                    "summary": "总结",
                },
                "search_coverage": {},
                "search_per": {"summary": {}},
            },
            shared={
                "config": {"target_product": "微信支付"},
                "collection_errors": {},
                "source_coverage_issue": None,
            },
            raw_data={
                "拼多多": [
                    {
                        "url": "https://example.com/pdd",
                        "title": "拼多多角色来源",
                        "source_intents": ["role"],
                    }
                ]
            },
            sources={},
            outline=outline.sections[REPORT_HEADINGS.index("竞品范围与角色判断")],
            completed_sections=[],
        )

        assert allowed_urls == ["https://example.com/pdd"]
        assert payload["section_context"]["suggested_source_refs"] == ["https://example.com/pdd"]

    def test_backfill_section_source_refs_uses_suggested_refs(self):
        agent = ReportAgent()
        section = ReportSection(
            heading="竞品范围与角色判断",
            level=2,
            content="角色判断正文",
            source_refs=[],
        )

        repaired = agent._backfill_section_source_refs(
            section,
            ["https://example.com/pdd"],
            {
                "section_context": {
                    "suggested_source_refs": ["https://example.com/pdd"],
                }
            },
        )

        assert repaired.source_refs == ["https://example.com/pdd"]
