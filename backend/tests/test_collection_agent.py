from types import SimpleNamespace
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from app.agents.agent_utils import raw_data_to_context
from app.agents.collection_agent import CollectionAgent
from app.agents.query_planner import build_search_query_plan, fallback_search_query_plan
from app.schemas.search import SearchQueryPlan, SearchQuerySpec


def _ctx():
    return SimpleNamespace(
        events=SimpleNamespace(emit=AsyncMock(), progress=AsyncMock(), stream_token=AsyncMock()),
    )


def test_fallback_query_plan_is_domain_neutral_and_covers_dimensions():
    plan = fallback_search_query_plan(
        product_category="硬件 / 消费电子",
        product_profile={"market_category": "electric vehicle", "product_form": "hardware"},
        focus_dimensions=["续航表现", "补能网络"],
    )

    by_intent = {spec.intent: spec for spec in plan.queries}
    assert "续航表现" in by_intent["dimension:续航表现"].query_template
    assert "补能网络" in by_intent["dimension:补能网络"].query_template
    assert all("手续费" not in spec.query_template for spec in plan.queries)


def test_fallback_query_plan_includes_business_context_without_domain_rules():
    plan = fallback_search_query_plan(
        product_category="企业软件 / SaaS",
        product_profile={"market_category": "cloud database"},
        focus_dimensions=["迁移成本"],
        extra_requirements="用于决定是否进入金融行业客户市场",
    )

    by_intent = {spec.intent: spec for spec in plan.queries}
    assert "金融行业客户市场" in by_intent["business_context"].query_template


@pytest.mark.asyncio
async def test_llm_query_planner_provides_domain_terms_and_restores_missing_dimension():
    planned = SearchQueryPlan(
        strategy_summary="优先行业监管和运营数据",
        queries=[
            SearchQuerySpec(
                intent="dimension:续航表现",
                dimension="续航表现",
                query_template="{product} CLTC 实测 续航 冬季",
                recovery_query_templates=["{product} 高速 续航 测试"],
                preferred_source_types=["review", "dataset"],
            ),
        ],
    )

    with (
        patch("app.agents.query_planner.llm_is_configured", return_value=True),
        patch("app.agents.query_planner.invoke_json_model", new=AsyncMock(return_value=planned)),
    ):
        result = await build_search_query_plan(
            product_category="硬件 / 消费电子",
            product_profile={"market_category": "electric vehicle"},
            focus_dimensions=["续航表现", "补能网络"],
        )

    by_intent = {spec.intent: spec for spec in result.queries}
    assert "CLTC" in by_intent["dimension:续航表现"].query_template
    assert "dimension:补能网络" in by_intent
    assert "official" in by_intent


def test_result_relevance_keeps_high_confidence_official_page_without_product_name():
    agent = CollectionAgent()
    item = {"title": "提现服务收费规则", "content": "单个实名账户享有免费提现额度", "score": 0.82}

    assert agent._result_is_relevant("支付宝", item, "支付宝 提现 收费规则 官方")
    assert not agent._result_is_relevant("支付宝", {**item, "score": 0.2}, "支付宝 提现 收费规则 官方")


def test_raw_data_context_prioritizes_distinct_search_intents():
    raw_data = {
        "支付宝": [
            {"title": "A", "url": "a", "source_intent": "overview", "relevance_score": 0.9},
            {"title": "B", "url": "b", "source_intent": "overview", "relevance_score": 0.8},
            {"title": "C", "url": "c", "source_intent": "dimension:费率", "relevance_score": 0.7},
        ],
    }

    context = raw_data_to_context(raw_data, max_items_per_product=2)

    assert [item["url"] for item in context["支付宝"]] == ["a", "c"]


@pytest.mark.asyncio
async def test_collect_for_product_runs_recovery_queries_when_initial_recall_is_low():
    client = AsyncMock()
    client.search.return_value = {"results": []}
    agent = CollectionAgent()
    plan = fallback_search_query_plan(
        product_category="移动应用",
        product_profile=None,
        focus_dimensions=["费率"],
    )

    result = await agent._collect_for_product(client, "支付宝", plan, _ctx())

    assert result == []
    assert client.search.await_count == 9
    queries = [call.kwargs["query"] for call in client.search.await_args_list]
    assert any("费率" in query and "报告" in query for query in queries)


@pytest.mark.asyncio
async def test_collection_agent_run_builds_per_summary_end_to_end():
    client = AsyncMock()

    async def _search(*, query, **kwargs):
        if "产品A 产品概览" in query:
            return {
                "results": [{
                    "url": "https://example.com/a-overview",
                    "title": "产品A 官方概览",
                    "content": "产品A 的公开介绍",
                    "score": 0.91,
                }],
            }
        if "产品A 定价 用户协议" in query:
            return {
                "results": [{
                    "url": "https://example.com/a-pricing",
                    "title": "产品A 定价规则",
                    "content": "产品A 的定价说明",
                    "score": 0.88,
                }],
            }
        return {"results": []}

    client.search.side_effect = _search
    plan = SearchQueryPlan(
        strategy_summary="按概览和定价分别检索",
        queries=[
            SearchQuerySpec(
                intent="overview",
                query_template="{product} 产品概览",
                recovery_query_templates=["{product} overview alt"],
            ),
            SearchQuerySpec(
                intent="dimension:定价",
                dimension="定价",
                query_template="{product} 定价",
                recovery_query_templates=["{product} 定价 用户协议"],
            ),
        ],
    )
    state = {
        "config": {
            "target_product": "自研产品",
            "target_product_status": "pre_launch",
            "product_category": "AI 产品 / 智能助手",
            "competitors": ["产品A"],
            "competitor_count": 1,
            "focus_dimensions": ["定价"],
        },
    }
    resolution = SimpleNamespace(
        competitors=["产品A"],
        dropped=[],
        added=[],
        query="产品A competitors",
        subcategory="generic",
    )

    with (
        patch("app.agents.collection_agent.tavily_is_configured", return_value=True),
        patch("app.agents.collection_agent.AsyncTavilyClient", return_value=client),
        patch("app.agents.collection_agent.resolve_competitors", new=AsyncMock(return_value=resolution)),
        patch("app.agents.collection_agent.build_search_query_plan", new=AsyncMock(return_value=plan)),
    ):
        result = await CollectionAgent().run(state, _ctx())

    summary = result["search_per"]["summary"]
    assert summary["replanned_product_count"] == 1
    assert summary["fully_covered_product_count"] == 1
    assert summary["successful_replans"] == 1
    assert summary["replan_hit_rate"] == 1.0
    assert result["search_coverage"]["产品A"]["missing_dimensions"] == []


@pytest.mark.asyncio
async def test_duplicate_url_accumulates_all_covered_intents():
    client = AsyncMock()
    client.search.return_value = {
        "results": [{
            "url": "https://example.com/product",
            "title": "产品A 官方说明",
            "content": "产品A 的公开说明",
            "score": 0.9,
        }],
    }
    plan = SearchQueryPlan(queries=[
        SearchQuerySpec(intent="dimension:性能", dimension="性能", query_template="{product} 性能"),
        SearchQuerySpec(intent="dimension:价格", dimension="价格", query_template="{product} 价格"),
    ])

    result = await CollectionAgent()._collect_for_product(client, "产品A", plan, _ctx())

    assert len(result) == 1
    assert result[0].source_intents == ["dimension:性能", "dimension:价格"]
    assert client.search.await_count == 2


def test_recovery_query_plan_retries_uncovered_dimension_even_with_many_sources():
    plan = SearchQueryPlan(
        queries=[
            SearchQuerySpec(
                intent="dimension:C端手续费",
                dimension="C端手续费",
                query_template="{product} C端手续费 官方规则",
                recovery_query_templates=["{product} C端手续费 用户协议"],
            ),
            SearchQuerySpec(
                intent="dimension:B端商户费率",
                dimension="B端商户费率",
                query_template="{product} B端商户费率 官方规则",
                recovery_query_templates=["{product} 商户 收单 服务费率"],
            ),
        ],
    )
    queries = CollectionAgent()._build_recovery_query_plan(
        "微信支付",
        plan,
        {"dimension:C端手续费"},
        source_count=12,
    )

    assert len(queries) == 1
    assert queries[0][0] == "dimension:B端商户费率"
    assert "商户 收单 服务费率" in queries[0][1]


def test_replan_query_plan_skips_non_dimension_gap_when_product_already_has_sources():
    plan = SearchQueryPlan(
        queries=[
            SearchQuerySpec(
                intent="overview",
                query_template="{product} 产品概览",
                recovery_query_templates=["{product} overview"],
            ),
            SearchQuerySpec(
                intent="dimension:费率",
                dimension="费率",
                query_template="{product} 费率",
                recovery_query_templates=["{product} 费率 用户协议"],
            ),
        ],
    )
    coverage = {
        "source_count": 2,
        "covered_intents": ["dimension:费率"],
        "missing_intents": ["overview"],
        "missing_dimensions": [],
        "missing_product": False,
        "needs_replan": False,
    }

    queries = CollectionAgent()._build_replan_query_plan("微信支付", plan, coverage)

    assert queries == []


def test_replan_query_plan_for_missing_product_includes_foundational_recovery_queries():
    plan = SearchQueryPlan(
        queries=[
            SearchQuerySpec(
                intent="overview",
                query_template="{product} 产品概览",
                recovery_query_templates=["{product} overview alt"],
            ),
            SearchQuerySpec(
                intent="official",
                query_template="{product} 官方 文档",
                recovery_query_templates=["{product} 官网 说明"],
            ),
            SearchQuerySpec(
                intent="independent_evidence",
                query_template="{product} 评测",
                recovery_query_templates=["{product} review comparison"],
            ),
            SearchQuerySpec(
                intent="dimension:费率",
                dimension="费率",
                query_template="{product} 费率",
                recovery_query_templates=["{product} 费率 用户协议"],
            ),
        ],
    )
    coverage = {
        "source_count": 0,
        "covered_intents": [],
        "missing_intents": ["overview", "official", "independent_evidence", "dimension:费率"],
        "missing_dimensions": ["费率"],
        "missing_product": True,
        "needs_replan": True,
    }

    queries = CollectionAgent()._build_replan_query_plan("微信支付", plan, coverage)
    intents = [intent for intent, _ in queries]

    assert "overview" in intents
    assert "official" in intents
    assert "independent_evidence" in intents
    assert "dimension:费率" in intents


def test_search_coverage_reports_dimension_gaps_separately_from_source_count():
    plan = SearchQueryPlan(queries=[
        SearchQuerySpec(intent="overview", query_template="{product} overview"),
        SearchQuerySpec(intent="dimension:性能", dimension="性能", query_template="{product} 性能"),
        SearchQuerySpec(intent="dimension:价格", dimension="价格", query_template="{product} 价格"),
    ])
    raw_data = {
        "产品A": [{
            "url": "https://example.com/a",
            "source_intents": ["overview", "dimension:性能"],
        }],
    }

    coverage = CollectionAgent()._build_search_coverage(raw_data, plan)

    assert coverage["产品A"]["source_count"] == 1
    assert coverage["产品A"]["missing_dimensions"] == ["价格"]


def test_per_summary_counts_replans_and_remaining_gaps():
    product_traces = {
        "产品A": {
            "replan_query_count": 2,
            "main_coverage": {"missing_dimensions": ["价格"], "missing_product": False},
            "final_coverage": {"missing_dimensions": [], "missing_product": False},
        },
        "产品B": {
            "replan_query_count": 1,
            "main_coverage": {"missing_dimensions": ["功能"], "missing_product": True},
            "final_coverage": {"missing_dimensions": ["功能"], "missing_product": True},
        },
    }
    search_coverage = {
        "产品A": {"missing_dimensions": [], "missing_product": False},
        "产品B": {"missing_dimensions": ["功能"], "missing_product": True},
    }

    summary = CollectionAgent()._build_per_summary(product_traces, search_coverage)

    assert summary["replanned_product_count"] == 2
    assert summary["fully_covered_product_count"] == 1
    assert summary["products_missing_after_replan"] == ["产品B"]
    assert summary["dimensions_missing_after_replan"] == {"产品B": ["功能"]}
    assert summary["successful_replans"] == 1
    assert summary["replan_hit_rate"] == 0.5
