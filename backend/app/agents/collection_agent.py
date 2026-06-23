import time
import asyncio
from datetime import datetime
from tavily import AsyncTavilyClient
from app.agents.base_agent import BaseAgent
from app.agents.agent_utils import tavily_is_configured
from app.config import get_settings
from app.core.runtime.context import AgentContext
from app.schemas.event import EventType
from app.schemas.competitor import CompetitorInfo, SearchResult
from app.schemas.search import SearchQueryPlan
from app.agents.competitor_resolver import normalize_competitor_name, resolve_competitors
from app.agents.query_planner import build_search_query_plan
from app.schemas.workflow import target_product_is_launched


DEFAULT_RECOVERY_PRIORITY_DEPTH = 2


class CollectionAgent(BaseAgent):
    """信息采集 Agent：通过 Tavily 搜索 API 并行采集竞品公开信息。

    对每个产品（目标产品 + N 个竞品）并发执行多条搜索查询，
    按 URL 去重后汇总为 raw_data 传入下游分析节点。
    """

    node_name = "information_collection"

    async def run(self, state: dict, ctx: AgentContext) -> dict:
        config = state.get("config", {})
        if not isinstance(config, dict):
            config = {}
        settings = get_settings()

        target = config.get("target_product", "")
        category = config.get("product_category", "")
        focus_dimensions = config.get("focus_dimensions", [])
        competitor_names = config.get("competitors", []) or []
        competitor_count = config.get("competitor_count", len(competitor_names) or 5)
        competitor_names = competitor_names[:competitor_count]
        include_target = target_product_is_launched(config)
        # 初始产品列表用于无 Tavily 的兜底路径；Tavily 可用时会先解析并替换竞品。
        products = [p for p in ([target] if include_target else []) + competitor_names if p]

        await self.log_and_broadcast(ctx, EventType.NODE_START, {
            "input_summary": {
                "target_product": target,
                "competitors_count": len(competitor_names),
                "phase": "collecting",
            },
        })
        await self.emit_progress(
            ctx,
            stage="validate_scope",
            message=f"正在校验目标产品与竞品范围，当前目标是 {target or '未命名产品'}。",
        )

        start = time.time()

        raw_data: dict[str, list] = {product: [] for product in products}
        collection_errors: dict[str, str] = {}
        search_plan: SearchQueryPlan | None = None
        search_coverage: dict[str, dict] = {}
        search_per: dict[str, dict] = {"mode": "plan_execute_replan", "planner": {}, "products": {}}
        competitors = [CompetitorInfo(name=name, category=category).model_dump(mode="json") for name in competitor_names]

        if not tavily_is_configured():
            await self.emit_progress(
                ctx,
                stage="search_unavailable",
                message="未检测到 Tavily 配置，当前将跳过实时搜索，仅保留诊断信息。",
                level="warning",
            )
            for product in products:
                collection_errors[product] = "Tavily API key is not configured; skipped live search."
        else:
            client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
            await self.emit_progress(
                ctx,
                stage="resolve_competitors",
                message="正在解析有效竞品实体，剔除不适合作为竞品的泛化描述。",
            )
            resolution = await resolve_competitors(
                client=client,
                target_product=target,
                category=category,
                focus_dimensions=focus_dimensions,
                competitor_names=competitor_names,
                competitor_count=competitor_count,
                product_profile=config.get("product_profile"),
            )
            if resolution.dropped or resolution.added:
                await self.log_and_broadcast(ctx, EventType.TOOL_RESULT, {
                    "tool": "competitor_resolver",
                    "target_product": target,
                    "product_profile": config.get("product_profile"),
                    "subcategory": resolution.subcategory,
                    "query": resolution.query,
                    "original_competitors": competitor_names,
                    "resolved_competitors": resolution.competitors,
                    "dropped": resolution.dropped,
                    "added": resolution.added,
                })
            competitor_names = resolution.competitors
            config = {**config, "competitors": competitor_names}
            competitors = [
                CompetitorInfo(name=name, category=category).model_dump(mode="json")
                for name in competitor_names
            ]
            await self.emit_progress(
                ctx,
                stage="resolved_competitors",
                message=f"已确认 {len(competitor_names)} 个有效竞品，准备开始公开来源采集。",
                level="success",
            )
            minimum_competitors = 1 if competitor_count <= 1 else min(2, competitor_count)
            if len(competitor_names) < minimum_competitors:
                collection_errors["__competitor_resolution__"] = (
                    f"Only resolved {len(competitor_names)} valid competitor(s); "
                    f"at least {minimum_competitors} required before analysis."
                )
                await self.emit_progress(
                    ctx,
                    stage="insufficient_competitors",
                    message=f"有效竞品数量不足，当前仅确认 {len(competitor_names)} 个，后续分析可能无法继续。",
                    level="warning",
                )
                raw_data = {}
                products = []
            else:
                # 目标产品也参与搜索，确保分析时有自身数据做基线对比。
                products = [p for p in ([target] if include_target else []) + competitor_names if p]
                raw_data = {product: [] for product in products}
                await self.emit_progress(
                    ctx,
                    stage="plan_queries",
                    message="正在根据产品画像、分析维度和业务问题生成结构化搜索计划。",
                )
                search_plan = await build_search_query_plan(
                    product_category=category,
                    product_profile=config.get("product_profile"),
                    focus_dimensions=focus_dimensions,
                    extra_requirements=config.get("extra_requirements", ""),
                )
                search_plan = self._normalize_search_plan(
                    search_plan,
                    max_executed_queries=settings.SEARCH_MAX_EXECUTED_QUERIES,
                )
                await self.log_and_broadcast(ctx, EventType.TOOL_RESULT, {
                    "tool": "query_planner",
                    "strategy_summary": search_plan.strategy_summary,
                    "query_count": len(search_plan.queries),
                    "intents": [spec.intent for spec in search_plan.queries],
                    "recovery_candidates": {
                        spec.intent: len(spec.recovery_query_templates)
                        for spec in search_plan.queries
                        if spec.recovery_query_templates
                    },
                })
                search_per["planner"] = {
                    "strategy_summary": search_plan.strategy_summary,
                    "query_count": len(search_plan.queries),
                    "intents": [spec.intent for spec in search_plan.queries],
                }
                await self.emit_progress(
                    ctx,
                    stage="execute_main_plan",
                    message=f"正在为 {len(products)} 个产品并发执行主查询计划，收集首轮公开证据。",
                )
                # 所有产品的搜索并发执行，总耗时 = max(单产品耗时) 而非 sum
                tasks = [
                    self._collect_for_product_per(client, product, search_plan, ctx)
                    for product in products
                ]
                # gather(return_exceptions=True)：单个产品失败不影响其他产品
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for product, result in zip(products, results):
                    if isinstance(result, Exception):
                        error_text = str(result)[:500]
                        collection_errors[product] = error_text
                        raw_data[product] = []
                        await self.emit_progress(
                            ctx,
                            stage="search_service_unavailable",
                            message=self._build_search_failure_message(product, error_text),
                            level="warning",
                        )
                    else:
                        product_results, per_trace = result
                        raw_data[product] = [item.model_dump(mode="json") for item in product_results]
                        search_per["products"][product] = per_trace
                search_coverage = self._build_search_coverage(raw_data, search_plan)
                search_per["final_coverage"] = search_coverage
                search_per["summary"] = self._build_per_summary(search_per["products"], search_coverage)

                missing_sources = [
                    product for product in products
                    if len(raw_data.get(product, [])) == 0
                ]
                missing_competitor_sources = [
                    product for product in missing_sources
                    if product != target
                ]
                if target in missing_sources or missing_competitor_sources:
                    collection_errors["__source_coverage__"] = (
                        "Missing source coverage for: " + ", ".join(missing_sources)
                    )
                    await self.emit_progress(
                        ctx,
                        stage="source_coverage_warning",
                        message=f"部分产品仍缺少来源覆盖：{', '.join(missing_sources)}。",
                        level="warning",
                    )

        duration_ms = int((time.time() - start) * 1000)
        total_sources = sum(len(items) for items in raw_data.values())
        failed_products = sum(
            1 for key in collection_errors
            if not (isinstance(key, str) and key.startswith("__"))
        )
        await self.emit_progress(
            ctx,
            stage="collection_complete",
            message=f"已完成采集，共覆盖 {len(raw_data)} 个产品，汇总 {total_sources} 条来源。",
            level="success",
        )

        await self.log_and_broadcast(ctx, EventType.NODE_COMPLETE, {
            "output_summary": {
                "collected_competitors": len(raw_data),
                "total_sources": total_sources,
                "failed_competitors": failed_products,
                "products_replanned": sum(
                    1
                    for trace in search_per.get("products", {}).values()
                    if trace.get("replan_query_count")
                ),
                "products_with_dimension_gaps": sum(
                    1 for coverage in search_coverage.values()
                    if coverage.get("missing_dimensions")
                ),
            },
            "duration_ms": duration_ms,
        })

        return {
            "config": config,
            "raw_data": raw_data,
            "collection_errors": collection_errors,
            "competitors": competitors,
            "search_plan": search_plan.model_dump(mode="json") if search_plan else {},
            "search_coverage": search_coverage,
            "search_per": search_per,
            "context_summaries": {},
            "current_phase": "collecting",
        }

    async def _collect_for_product_per(
        self,
        client: AsyncTavilyClient,
        product: str,
        search_plan: SearchQueryPlan,
        ctx: AgentContext,
    ) -> tuple[list[SearchResult], dict]:
        """Execute PER for a single product: main plan -> coverage eval -> targeted replan."""
        main_queries = self._render_query_plan(product, search_plan)
        await self.emit_progress(
            ctx,
            stage="search_product",
            message=f"正在为 {product} 并发执行主查询计划，共 {len(main_queries)} 条查询。",
        )
        main_results = await self._execute_query_batch_for_product(
            client,
            product,
            main_queries,
            ctx,
            phase="main",
            max_results=4,
        )
        main_coverage = self._build_product_coverage(main_results, search_plan)
        await self.emit_progress(
            ctx,
            stage="evaluate_coverage_gap",
            message=(
                f"已完成 {product} 的 coverage 评估，"
                f"当前缺失维度 {len(main_coverage.get('missing_dimensions', []))} 个。"
            ),
        )

        replan_queries = self._build_replan_query_plan(product, search_plan, main_coverage)
        final_results = main_results
        if replan_queries:
            replan_reason = []
            if main_coverage.get("missing_product"):
                replan_reason.append("缺失产品")
            if main_coverage.get("missing_dimensions"):
                replan_reason.append("缺失维度")
            await self.emit_progress(
                ctx,
                stage="execute_replan",
                message=(
                    f"{product} 存在 {'、'.join(replan_reason) or '覆盖缺口'}，"
                    f"正在并发执行 {len(replan_queries)} 条补救查询。"
                ),
                level="warning",
            )
            recovery_results = await self._execute_query_batch_for_product(
                client,
                product,
                replan_queries,
                ctx,
                phase="replan",
                max_results=6,
            )
            final_results = self._merge_search_results(main_results, recovery_results)

        final_results.sort(key=lambda item: item.relevance_score, reverse=True)
        final_coverage = self._build_product_coverage(final_results, search_plan)
        await self.log_and_broadcast(ctx, EventType.TOOL_RESULT, {
            "tool": "tavily.search",
            "product": product,
            "phase": "per_summary",
            "source_count": len(final_results),
            "main_query_count": len(main_queries),
            "replan_query_count": len(replan_queries),
            "covered_intents": final_coverage.get("covered_intents", []),
            "missing_dimensions": final_coverage.get("missing_dimensions", []),
        })
        await self.emit_progress(
            ctx,
            stage="summarize_product_sources",
            message=f"{product} 的来源整理完成，当前保留 {len(final_results)} 条去重结果。",
            level="success",
        )
        return final_results, {
            "main_query_count": len(main_queries),
            "main_coverage": main_coverage,
            "replan_query_count": len(replan_queries),
            "replan_queries": [query for _, query in replan_queries],
            "final_coverage": final_coverage,
        }

    async def _collect_for_product(
        self,
        client: AsyncTavilyClient,
        product: str,
        search_plan: SearchQueryPlan,
        ctx: AgentContext,
    ) -> list[SearchResult]:
        """对单个产品执行多查询搜索，URL 去重后返回结果列表。

        搜索策略：
        1. Planner 产出结构化主查询和 recovery 候选
        2. Executor 并发执行主查询
        3. Evaluator 评估 coverage gap
        4. Replanner 仅对缺失维度 / 缺失产品执行补救查询
        """
        collected, _ = await self._collect_for_product_per(client, product, search_plan, ctx)
        return collected

    async def _execute_query_batch_for_product(
        self,
        client: AsyncTavilyClient,
        product: str,
        queries: list[tuple[str, str]],
        ctx: AgentContext,
        *,
        phase: str,
        max_results: int,
    ) -> list[SearchResult]:
        """Execute one batch of Tavily queries concurrently for a single product."""
        if not queries:
            return []
        await self.log_and_broadcast(ctx, EventType.TOOL_CALL, {
            "tool": "tavily.search",
            "product": product,
            "phase": phase,
            "queries": [query for _, query in queries],
        })
        responses = await asyncio.gather(
            *[
                client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="advanced",
                    include_answer=False,
                )
                for _, query in queries
            ],
            return_exceptions=True,
        )
        collected_by_url: dict[str, SearchResult] = {}
        collected: list[SearchResult] = []
        failures: list[str] = []
        for (intent, query), response in zip(queries, responses):
            if isinstance(response, Exception):
                failures.append(f"{intent}: {str(response)[:120]}")
                continue
            for item in response.get("results", []):
                url = item.get("url", "")
                if not url or not self._result_is_relevant(product, item, query):
                    continue
                if url in collected_by_url:
                    existing = collected_by_url[url]
                    if intent not in existing.source_intents:
                        existing.source_intents.append(intent)
                    continue
                result = SearchResult(
                    url=url,
                    title=item.get("title") or url,
                    snippet=item.get("content") or item.get("snippet") or "",
                    content_summary=item.get("content"),
                    source_query=query,
                    source_intent=intent,
                    source_intents=[intent],
                    relevance_score=float(item.get("score") or 0),
                    retrieved_at=datetime.utcnow(),
                )
                collected_by_url[url] = result
                collected.append(result)
        if failures and len(failures) == len(queries):
            raise RuntimeError(f"{product} {phase} queries all failed: {failures[0]}")
        return collected

    def _render_query_plan(
        self,
        product: str,
        search_plan: SearchQueryPlan,
    ) -> list[tuple[str, str]]:
        """Render one workflow-level plan for a concrete product."""
        return self._dedupe_query_plan([
            (spec.intent, spec.query_template.format(product=product))
            for spec in search_plan.queries
        ])

    def _build_replan_query_plan(
        self,
        product: str,
        search_plan: SearchQueryPlan,
        coverage: dict,
    ) -> list[tuple[str, str]]:
        """Only fill missing dimensions or missing products using planner-provided recovery queries."""
        settings = get_settings()
        queries: list[tuple[str, str]] = []
        missing_dimensions = set(coverage.get("missing_dimensions") or [])
        missing_product = bool(coverage.get("missing_product"))
        if missing_product:
            product_specs = [
                spec for spec in search_plan.queries
                if spec.intent in {"overview", "official", "independent_evidence"}
            ]
            queries.extend(self._expand_recovery_queries(product, product_specs))
        if missing_dimensions:
            dimension_specs = [
                spec for spec in search_plan.queries
                if spec.dimension and spec.dimension in missing_dimensions
            ]
            queries.extend(self._expand_recovery_queries(product, dimension_specs))
        return self._dedupe_query_plan(queries)[:settings.SEARCH_MAX_RECOVERY_QUERIES]

    def _build_recovery_query_plan(
        self,
        product: str,
        search_plan: SearchQueryPlan,
        covered_intents: set[str],
        source_count: int,
    ) -> list[tuple[str, str]]:
        """Backward-compatible wrapper for tests and older call sites."""
        coverage = self._build_product_coverage_from_summary(
            covered_intents=covered_intents,
            source_count=source_count,
            search_plan=search_plan,
        )
        return self._build_replan_query_plan(product, search_plan, coverage)

    def _expand_recovery_queries(
        self,
        product: str,
        specs: list,
    ) -> list[tuple[str, str]]:
        """Prioritize the first few recovery templates, then consume the rest if budget allows."""
        queries: list[tuple[str, str]] = []
        max_recovery_depth = max((len(spec.recovery_query_templates) for spec in specs), default=0)
        recovery_depths = list(range(min(DEFAULT_RECOVERY_PRIORITY_DEPTH, max_recovery_depth)))
        recovery_depths.extend(range(DEFAULT_RECOVERY_PRIORITY_DEPTH, max_recovery_depth))
        for recovery_index in recovery_depths:
            for spec in specs:
                if recovery_index < len(spec.recovery_query_templates):
                    queries.append((
                        spec.intent,
                        spec.recovery_query_templates[recovery_index].format(product=product),
                    ))
        return queries

    @staticmethod
    def _build_search_failure_message(product: str, error_text: str) -> str:
        lowered = error_text.lower()
        if any(keyword in lowered for keyword in [
            "usage limit",
            "quota",
            "rate limit",
            "plan's set usage limit",
        ]):
            return (
                f"{product} 的联网搜索失败：Tavily 配额已耗尽，当前无法继续拉取公开来源。"
                " 请补充配额后重试。"
            )
        if any(keyword in lowered for keyword in [
            "api key",
            "unauthorized",
            "authentication",
            "forbidden",
        ]):
            return (
                f"{product} 的联网搜索失败：搜索服务当前不可用或鉴权异常，"
                " 暂时无法继续拉取公开来源。"
            )
        if any(keyword in lowered for keyword in [
            "timeout",
            "temporarily unavailable",
            "service unavailable",
            "connection",
            "connect",
            "network",
            "502",
            "503",
            "504",
        ]):
            return (
                f"{product} 的联网搜索失败：搜索服务暂时不可用，"
                " 当前无法继续拉取公开来源，请稍后重试。"
            )
        return f"{product} 的联网搜索失败：{error_text}"

    @staticmethod
    def _dedupe_query_plan(queries: list[tuple[str, str]]) -> list[tuple[str, str]]:
        seen: set[str] = set()
        deduped: list[tuple[str, str]] = []
        for intent, query in queries:
            if query in seen:
                continue
            seen.add(query)
            deduped.append((intent, query))
        return deduped

    @staticmethod
    def _normalize_search_plan(
        search_plan: SearchQueryPlan,
        *,
        max_executed_queries: int,
    ) -> SearchQueryPlan:
        """Keep planner freedom, but cap execution to the highest-priority queries."""
        return search_plan.model_copy(update={"queries": search_plan.queries[:max(1, max_executed_queries)]})

    @staticmethod
    def _merge_search_results(
        base_results: list[SearchResult],
        new_results: list[SearchResult],
    ) -> list[SearchResult]:
        merged_by_url: dict[str, SearchResult] = {item.url: item.model_copy(deep=True) for item in base_results}
        for item in new_results:
            if item.url in merged_by_url:
                existing = merged_by_url[item.url]
                intents = existing.source_intents or ([existing.source_intent] if existing.source_intent else [])
                for intent in item.source_intents or ([item.source_intent] if item.source_intent else []):
                    if intent and intent not in intents:
                        intents.append(intent)
                existing.source_intents = intents
                if item.relevance_score > existing.relevance_score:
                    existing.relevance_score = item.relevance_score
                    existing.title = item.title
                    existing.snippet = item.snippet
                    existing.content_summary = item.content_summary
                    existing.source_query = item.source_query
                    existing.source_intent = item.source_intent
                continue
            merged_by_url[item.url] = item.model_copy(deep=True)
        return list(merged_by_url.values())

    def _build_product_coverage(self, results: list[SearchResult], search_plan: SearchQueryPlan) -> dict:
        serialized = [item.model_dump(mode="json") for item in results]
        return self._build_search_coverage({"__product__": serialized}, search_plan)["__product__"]

    @staticmethod
    def _build_per_summary(product_traces: dict[str, dict], search_coverage: dict[str, dict]) -> dict:
        total_products = len(search_coverage)
        replanned_products = [
            product
            for product, trace in product_traces.items()
            if trace.get("replan_query_count", 0) > 0
        ]
        fully_covered_products = [
            product
            for product, coverage in search_coverage.items()
            if not coverage.get("missing_product") and not coverage.get("missing_dimensions")
        ]
        products_missing_after_replan = [
            product
            for product, coverage in search_coverage.items()
            if coverage.get("missing_product")
        ]
        dimensions_missing_after_replan = {
            product: coverage.get("missing_dimensions", [])
            for product, coverage in search_coverage.items()
            if coverage.get("missing_dimensions")
        }
        successful_replans = 0
        for product in replanned_products:
            trace = product_traces.get(product, {})
            main_missing = len((trace.get("main_coverage") or {}).get("missing_dimensions", []))
            final_missing = len((trace.get("final_coverage") or {}).get("missing_dimensions", []))
            main_missing_product = bool((trace.get("main_coverage") or {}).get("missing_product"))
            final_missing_product = bool((trace.get("final_coverage") or {}).get("missing_product"))
            if final_missing < main_missing or (main_missing_product and not final_missing_product):
                successful_replans += 1
        replan_hit_rate = (
            round(successful_replans / len(replanned_products), 3)
            if replanned_products
            else 0.0
        )
        products_with_remaining_gaps = sorted(set(products_missing_after_replan) | set(dimensions_missing_after_replan))
        return {
            "mode": "plan_execute_replan",
            "total_products": total_products,
            "replanned_products": replanned_products,
            "replanned_product_count": len(replanned_products),
            "fully_covered_products": fully_covered_products,
            "fully_covered_product_count": len(fully_covered_products),
            "products_with_remaining_gaps": products_with_remaining_gaps,
            "products_missing_after_replan": products_missing_after_replan,
            "dimensions_missing_after_replan": dimensions_missing_after_replan,
            "successful_replans": successful_replans,
            "replan_hit_rate": replan_hit_rate,
        }

    @staticmethod
    def _build_product_coverage_from_summary(
        *,
        covered_intents: set[str],
        source_count: int,
        search_plan: SearchQueryPlan,
    ) -> dict:
        planned_intents = [spec.intent for spec in search_plan.queries]
        dimension_intents = {intent for intent in planned_intents if intent.startswith("dimension:")}
        missing = [intent for intent in planned_intents if intent not in covered_intents]
        return {
            "source_count": source_count,
            "covered_intents": sorted(covered_intents),
            "missing_intents": missing,
            "missing_dimensions": [
                intent.removeprefix("dimension:")
                for intent in missing
                if intent in dimension_intents
            ],
            "missing_product": source_count == 0,
            "needs_replan": source_count == 0 or any(intent in dimension_intents for intent in missing),
        }

    def _result_is_relevant(self, product: str, item: dict, query: str) -> bool:
        """Accept explicit entity matches and high-confidence search-engine matches.

        Official help pages often omit the parent product name from their title and
        snippet. Requiring a literal mention dropped those valuable narrow sources.
        """
        if self._result_mentions_product(product, item):
            return True
        score = float(item.get("score") or 0)
        return score >= 0.55 and normalize_competitor_name(product).lower() in query.lower()

    @staticmethod
    def _build_search_coverage(raw_data: dict[str, list], search_plan: SearchQueryPlan) -> dict[str, dict]:
        planned_intents = [spec.intent for spec in search_plan.queries]
        dimension_intents = {intent for intent in planned_intents if intent.startswith("dimension:")}
        coverage: dict[str, dict] = {}
        for product, items in raw_data.items():
            covered = {
                intent
                for item in items
                if isinstance(item, dict)
                for intent in (item.get("source_intents") or [item.get("source_intent")])
                if intent
            }
            missing = [intent for intent in planned_intents if intent not in covered]
            coverage[product] = {
                "source_count": len(items),
                "covered_intents": sorted(covered),
                "missing_intents": missing,
                "missing_dimensions": [
                    intent.removeprefix("dimension:")
                    for intent in missing
                    if intent in dimension_intents
                ],
                "missing_product": len(items) == 0,
                "needs_replan": len(items) == 0 or any(intent in dimension_intents for intent in missing),
            }
        return coverage

    def _result_mentions_product(self, product: str, item: dict) -> bool:
        """Return whether a search result visibly mentions the queried product."""
        product_name = normalize_competitor_name(product)
        if not product_name:
            return False

        title = str(item.get("title") or "")
        content = str(item.get("content") or item.get("snippet") or "")
        text = f"{title}\n{content}".lower()
        product_lower = product_name.lower()
        if product_lower in text:
            return True

        compact_product = product_lower.replace(" ", "")
        compact_text = text.replace(" ", "")
        return bool(compact_product and compact_product in compact_text)
