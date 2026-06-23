from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agents.analysis_agent import AnalysisAgent
from app.schemas.competitor_role import CompetitorRoleAnalysis, CompetitorRoleItem
from app.schemas.feature import FeatureItem, FeatureMatrix
from app.schemas.gtm import GTMAnalysis
from app.schemas.positioning import PositioningAnalysis
from app.schemas.pricing import PricingComparison
from app.schemas.sentiment import UserSentimentAnalysis
from app.schemas.workflow import target_product_is_launched


def test_unlaunched_target_is_excluded_from_comparison_products():
    agent = AnalysisAgent()
    state = {
        "config": {
            "target_product": "自研导购产品",
            "target_product_status": "pre_launch",
            "competitors": ["返利网"],
        },
        "raw_data": {
            "自研导购产品": [{"url": "https://example.com/internal"}],
            "返利网": [{"url": "https://example.com/fanli"}],
        },
    }

    _, target, competitors, _, _, _, products = agent._analysis_inputs(state)
    feature, pricing, sentiment, *_ = agent._fallback_analysis(
        target,
        competitors,
        ["核心功能"],
        state["raw_data"],
        {},
        products,
    )

    assert products == ["返利网"]
    assert [comparison.product for comparison in feature.matrix[0].comparisons] == ["返利网"]
    assert [plan.product for plan in pricing.plans] == ["返利网"]
    assert set(sentiment.per_product) == {"返利网"}


def test_launched_target_remains_in_comparison_products():
    agent = AnalysisAgent()
    state = {
        "config": {
            "target_product": "支付宝",
            "target_product_status": "launched",
            "competitors": ["微信支付"],
        },
        "raw_data": {"支付宝": [], "微信支付": []},
    }

    *_, products = agent._analysis_inputs(state)

    assert products == ["支付宝", "微信支付"]


def test_legacy_self_developed_target_is_treated_as_unlaunched():
    assert target_product_is_launched({
        "target_product": "自研导购类产品",
        "extra_requirements": "用于制定产品上线前增长策略",
    }) is False


def test_analysis_outputs_are_restricted_to_collected_products():
    agent = AnalysisAgent()
    feature_matrix = FeatureMatrix.model_validate({
        "dimensions": ["硬件配置"],
        "matrix": [{
            "feature_name": "硬件配置",
            "products": {
                "三星S26": "有来源",
                "Pixel 10": "公开来源不足",
            },
        }],
    })
    pricing = PricingComparison.model_validate({
        "plans": [
            {"product": "三星S26", "tiers": [{"name": "公开信息", "price": 6999, "highlights": ["有来源"]}]},
            {"product": "Pixel 10", "tiers": [{"name": "公开信息", "price": 0, "highlights": ["公开来源不足"]}]},
        ],
        "summary": "summary",
    })
    sentiment = UserSentimentAnalysis.model_validate({
        "per_product": {
            "三星S26": {"positive": 1, "negative": 0, "neutral": 1},
            "Pixel 10": {"positive": 0, "negative": 0, "neutral": 1},
        },
        "common_praises": [],
        "common_complaints": [],
    })

    filtered_feature, filtered_pricing, filtered_sentiment = agent._restrict_to_products(
        feature_matrix,
        pricing,
        sentiment,
        ["三星S26"],
    )

    assert filtered_feature.matrix[0].products == {"三星S26": "有来源"}
    assert [plan.product for plan in filtered_pricing.plans] == ["三星S26"]
    assert set(filtered_sentiment.per_product) == {"三星S26"}


def test_fallback_evidence_uses_collected_snippet_field():
    agent = AnalysisAgent()
    raw_data = {
        "支付宝": [{
            "url": "https://example.com/alipay",
            "title": "支付宝手续费规则",
            "snippet": "提现超过免费额度后按规则收取服务费。",
        }],
    }

    refs = agent._evidence_refs("支付宝", raw_data)
    summary = agent._source_based_summary("支付宝", raw_data["支付宝"])

    assert refs[0].snippet == "提现超过免费额度后按规则收取服务费。"
    assert "来源摘录，尚待分析" in summary


def test_feature_matrix_quality_gate_rejects_placeholder_only_content():
    matrix = FeatureMatrix.model_validate({
        "dimensions": ["手续费策略"],
        "matrix": [{
            "feature_name": "提现手续费",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "unknown",
                "difference_summary": "来源摘录，尚待分析：支付宝手续费规则",
                "evidence_refs": [{"url": "https://example.com", "title": "规则", "snippet": ""}],
            }],
        }],
    })

    assert AnalysisAgent._feature_matrix_is_deliverable(matrix) is False


def test_feature_matrix_quality_gate_accepts_evidence_backed_comparison():
    matrix = FeatureMatrix.model_validate({
        "dimensions": ["手续费策略"],
        "matrix": [{
            "feature_name": "提现手续费",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "supported",
                "difference_summary": "支付宝对免费提现额度之外的金额收取服务费。",
                "evidence_refs": [{
                    "url": "https://example.com",
                    "title": "规则",
                    "snippet": "超过免费提现额度后，将按照页面展示规则收取服务费。",
                }],
            }],
        }],
    })

    assert AnalysisAgent._feature_matrix_is_deliverable(matrix) is True


def test_feature_matrix_quality_gate_accepts_url_only_evidence_ref():
    matrix = FeatureMatrix.model_validate({
        "dimensions": ["手续费策略"],
        "matrix": [{
            "dimension": "提现手续费",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "supported",
                "difference_summary": "支付宝对免费提现额度之外的金额按照公开规则收取服务费。",
                "evidence_refs": ["https://example.com/alipay-fee"],
            }],
        }],
    })

    assert AnalysisAgent._feature_matrix_is_deliverable(matrix) is True


def test_feature_matrix_hides_dimensions_when_every_product_is_unknown():
    matrix = FeatureMatrix.model_validate({
        "dimensions": ["手续费减免", "手续费规则"],
        "matrix": [
            {
                "feature_name": "手续费减免",
                "comparisons": [
                    {"product": "支付宝", "support_level": "unknown"},
                    {"product": "微信支付", "support_level": "unknown"},
                ],
            },
            {
                "feature_name": "手续费规则",
                "comparisons": [
                    {"product": "支付宝", "support_level": "supported"},
                    {"product": "微信支付", "support_level": "unknown"},
                ],
            },
        ],
    })

    visible = AnalysisAgent._without_all_unknown_dimensions(matrix)

    assert visible.dimensions == ["手续费规则"]
    assert [item.feature_name for item in visible.matrix] == ["手续费规则"]


def test_sources_for_feature_dimension_prefers_matching_intent():
    sources = {
        "支付宝": [
            {
                "url": "https://example.com/dimension",
                "source_intent": "dimension:手续费策略",
                "source_intents": ["dimension:手续费策略"],
            },
            {"url": "https://example.com/official", "source_intent": "official"},
            {"url": "https://example.com/other", "source_intent": "business_context"},
        ],
    }

    selected = AnalysisAgent._sources_for_feature_dimension(sources, "手续费策略")

    assert [item["url"] for item in selected["支付宝"]] == [
        "https://example.com/dimension",
        "https://example.com/official",
    ]


def test_feature_dimensions_only_keep_feature_like_dimensions():
    dimensions = AnalysisAgent._feature_dimensions([
        "目标用户",
        "使用场景",
        "核心问题",
        "解决方案",
        "支撑点",
        "功能体验",
        "用户反馈",
        "上市与增长",
        "商业模式",
    ])

    assert dimensions == ["功能体验"]


def test_feature_dimensions_exclude_custom_content_strategy_dimension():
    dimensions = AnalysisAgent._feature_dimensions([
        "各竞品针对AI生成内容的去AI味优化机制",
        "功能体验",
    ])

    assert dimensions == ["功能体验"]


def test_restrict_role_analysis_strips_internal_config_prefix():
    agent = AnalysisAgent()
    role_analysis = CompetitorRoleAnalysis(
        items=[
            CompetitorRoleItem(
                product="拼多多",
                role="benchmark",
                reason="config.competitor_groups 明确将拼多多标注为 benchmark。拼多多作为社交电商平台，可作为微信支付生态商业化的标杆参考。",
                evidence_refs=[],
                confidence=0.8,
            )
        ],
        summary="基于 config.competitor_groups 的预设标签，拼多多被归类为 benchmark 角色。拼多多可作为标杆参考。",
    )

    result = agent._restrict_role_analysis(
        role_analysis,
        ["拼多多"],
        {"benchmark": ["拼多多"]},
    )

    assert result.items[0].reason == "拼多多作为社交电商平台，可作为微信支付生态商业化的标杆参考。"
    assert "config.competitor_groups" not in result.summary


@pytest.mark.asyncio
async def test_feature_matrix_is_generated_one_dimension_at_a_time():
    agent = AnalysisAgent()
    agent.emit_progress = AsyncMock()
    agent.invoke_structured_llm = AsyncMock(side_effect=AssertionError("feature analysis must use the repairable JSON path"))
    agent.invoke_llm = AsyncMock(side_effect=[
        FeatureItem.model_validate({
            "feature_name": "功能",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "supported",
                "difference_summary": "支付宝已提供公开来源确认的功能能力。",
                "evidence_refs": ["https://example.com/feature"],
            }],
        }),
        FeatureItem.model_validate({
            "feature_name": "功能体验",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "supported",
                "difference_summary": "支付宝已提供公开来源确认的功能体验规则。",
                "evidence_refs": ["https://example.com/ux"],
            }],
        }),
    ])
    payload = {
        "focus_dimensions": ["功能", "功能体验"],
        "sources_by_product": {
            "支付宝": [{
                "url": "https://example.com/feature",
                "source_intents": ["dimension:功能"],
            }],
        },
    }

    result = await agent._invoke_feature_matrix_by_dimension(
        SimpleNamespace(),
        payload,
        ["支付宝"],
    )

    assert agent.invoke_llm.await_count == 2
    assert [item["feature_name"] for item in result["matrix"]] == ["功能", "功能体验"]
    assert agent.invoke_llm.await_args_list[0].args[1]["requested_dimension"] == "功能"
    assert agent.invoke_llm.await_args_list[1].args[1]["requested_dimension"] == "功能体验"
    agent.invoke_structured_llm.assert_not_awaited()


@pytest.mark.asyncio
async def test_feature_matrix_skips_non_feature_dimensions():
    agent = AnalysisAgent()
    agent.emit_progress = AsyncMock()
    agent.invoke_llm = AsyncMock(return_value=FeatureItem.model_validate({
        "feature_name": "功能体验",
        "comparisons": [{
            "product": "支付宝",
            "support_level": "supported",
            "difference_summary": "支付宝已提供公开来源确认的功能体验能力。",
            "evidence_refs": ["https://example.com/feature"],
        }],
    }))
    payload = {
        "focus_dimensions": ["目标用户", "用户反馈", "上市与增长", "功能体验"],
        "sources_by_product": {
            "支付宝": [{
                "url": "https://example.com/feature",
                "source_intents": ["dimension:功能体验"],
            }],
        },
    }

    result = await agent._invoke_feature_matrix_by_dimension(
        SimpleNamespace(),
        payload,
        ["支付宝"],
    )

    assert agent.invoke_llm.await_count == 1
    assert agent.invoke_llm.await_args.args[1]["requested_dimension"] == "功能体验"
    assert result["dimensions"] == ["功能体验"]
    assert [item["feature_name"] for item in result["matrix"]] == ["功能体验"]


@pytest.mark.asyncio
async def test_non_feature_analysis_subnodes_use_structured_llm():
    agent = AnalysisAgent()
    agent.invoke_llm = AsyncMock(side_effect=AssertionError("free-form LLM path must not be used"))
    payload = {
        "target_product": "支付宝",
        "focus_dimensions": ["手续费策略"],
        "sources_by_product": {},
    }
    products = ["支付宝", "微信支付"]
    competitors = ["微信支付"]
    cases = [
        ("pricing_analysis", PricingComparison(plans=[], summary="暂无公开定价"), PricingComparison),
        (
            "sentiment_analysis",
            UserSentimentAnalysis(
                per_product={product: {"neutral": 1} for product in products},
                common_praises=[],
                common_complaints=[],
            ),
            UserSentimentAnalysis,
        ),
        ("positioning_analysis", PositioningAnalysis(), PositioningAnalysis),
        ("role_analysis", CompetitorRoleAnalysis(), CompetitorRoleAnalysis),
        ("gtm_analysis", GTMAnalysis(), GTMAnalysis),
    ]

    for node_id, response, expected_schema in cases:
        agent.invoke_structured_llm = AsyncMock(return_value=response)

        await agent._invoke_subnode_llm(
            SimpleNamespace(node_id=node_id),
            payload,
            products,
            competitors,
            {"core": competitors},
        )

        assert agent.invoke_structured_llm.await_count == 1
        assert agent.invoke_structured_llm.await_args.args[2] is expected_schema

    agent.invoke_llm.assert_not_awaited()


@pytest.mark.asyncio
async def test_feature_dimension_failure_uses_local_fallback_and_continues():
    agent = AnalysisAgent()
    agent.emit_progress = AsyncMock()
    agent.invoke_llm = AsyncMock(side_effect=[
        ValueError("truncated response"),
        FeatureItem.model_validate({
            "feature_name": "功能体验",
            "comparisons": [{
                "product": "支付宝",
                "support_level": "supported",
                "difference_summary": "支付宝已提供公开来源确认的功能体验规则。",
                "evidence_refs": ["https://example.com/ux"],
            }],
        }),
    ])
    payload = {
        "focus_dimensions": ["功能", "功能体验"],
        "sources_by_product": {
            "支付宝": [
                {
                    "url": "https://example.com/feature",
                    "title": "功能来源",
                    "snippet": "功能来源摘录",
                    "source_intents": ["dimension:功能"],
                },
                {
                    "url": "https://example.com/ux",
                    "source_intents": ["dimension:功能体验"],
                },
            ],
        },
    }

    result = await agent._invoke_feature_matrix_by_dimension(
        SimpleNamespace(),
        payload,
        ["支付宝"],
    )

    assert result["dimensions"] == ["功能体验"]
    assert len(result["matrix"]) == 1
    assert result["matrix"][0]["comparisons"][0]["support_level"] == "supported"
    assert any(
        call.kwargs.get("stage") == "feature_dimension_fallback"
        for call in agent.emit_progress.await_args_list
    )


@pytest.mark.asyncio
async def test_gtm_failure_uses_local_fallback_and_continues():
    agent = AnalysisAgent()
    agent.invoke_structured_llm = AsyncMock(side_effect=ValueError("invalid structured output"))
    agent.emit_progress = AsyncMock()
    payload = {
        "target_product": "支付宝",
        "focus_dimensions": ["手续费策略"],
        "sources_by_product": {
            "支付宝": [{
                "url": "https://example.com/alipay",
                "title": "支付宝公开来源",
                "snippet": "公开来源摘录",
            }],
        },
    }
    ctx = SimpleNamespace(node_id="gtm_analysis")

    result = await agent._invoke_subnode_llm(
        ctx,
        payload,
        ["支付宝", "微信支付"],
        ["微信支付"],
        {"core": ["微信支付"]},
    )

    gtm = GTMAnalysis.model_validate(result)
    assert gtm.summary
    assert any(
        call.kwargs.get("stage") == "gtm_analysis_fallback"
        for call in agent.emit_progress.await_args_list
    )


@pytest.mark.asyncio
async def test_gtm_analysis_uses_native_structured_output():
    agent = AnalysisAgent()
    agent.invoke_structured_llm = AsyncMock(return_value=GTMAnalysis.model_validate({
        "launch_rhythm": {"summary": "按季度推进"},
        "budget_allocation": {"summary": "预算更多投向重点渠道"},
        "channel_mix": {"summary": "以内容平台和搜索为主"},
        "content_strategy": {"summary": "强调场景化价值表达"},
        "paid_acquisition": {"summary": "存在阶段性投放动作"},
        "business_results": {"summary": "商业结果公开信息有限"},
        "summary": "已形成初步 GTM 判断。",
    }))
    payload = {
        "target_product": "支付宝",
        "focus_dimensions": ["上市与增长"],
        "sources_by_product": {"支付宝": []},
    }
    ctx = SimpleNamespace(node_id="gtm_analysis")

    result = await agent._invoke_subnode_llm(
        ctx,
        payload,
        ["支付宝", "微信支付"],
        ["微信支付"],
        {"core": ["微信支付"]},
    )

    agent.invoke_structured_llm.assert_awaited_once()
    assert result["summary"] == "已形成初步 GTM 判断。"


@pytest.mark.asyncio
async def test_analysis_short_circuits_when_source_coverage_has_blocking_gap():
    agent = AnalysisAgent()
    agent.emit_progress = AsyncMock()
    agent.log_and_broadcast = AsyncMock()
    ctx = SimpleNamespace(node_id="analysis", workflow_id="wf")

    state = {
        "config": {
            "target_product": "微信支付提现笔笔省",
            "competitors": ["支付宝余额提现"],
            "focus_dimensions": ["功能", "定价"],
        },
        "raw_data": {
            "微信支付提现笔笔省": [],
            "支付宝余额提现": [],
        },
        "collection_errors": {
            "__source_coverage__": "Missing source coverage for: 微信支付提现笔笔省, 支付宝余额提现",
        },
        "feature_matrix": {"matrix": [{"feature_name": "旧功能矩阵"}]},
        "pricing_comparison": {"plans": [{"product": "支付宝余额提现"}]},
        "swot": {"strengths": ["旧结论"]},
    }

    result = await agent.run(state, ctx)

    assert result["feature_matrix"] is None
    assert result["pricing_comparison"] is None
    assert result["swot"] is None
    assert result["analysis_modules"]["feature_analysis"]["complete"] is False
    assert any(
        call.kwargs.get("stage") == "blocked_by_source_gap"
        for call in agent.emit_progress.await_args_list
    )
