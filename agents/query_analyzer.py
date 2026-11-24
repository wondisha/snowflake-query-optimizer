"""Query performance analyzer."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryInsight:
    """Represents an optimization insight."""
    query_id: str
    issue_type: str
    severity: str
    description: str
    impact: str
    recommendation: str
    estimated_improvement: str


class QueryAnalyzer:
    """Analyzes query performance issues."""

    def __init__(self, connector):
        """Initialize query analyzer."""
        self.connector = connector
        self.insights_cache = {}

    def analyze_slow_queries(self) -> List[QueryInsight]:
        """Identify and analyze slow-running queries."""
        slow_queries = self.connector.get_slow_queries()
        insights = []

        for query in slow_queries:
            query_id = query.get("query_id")
            execution_time = query.get("execution_time", 0)
            bytes_scanned = query.get("bytes_scanned", 0)
            rows_produced = query.get("rows_produced", 0)

            # Cache check
            if query_id in self.insights_cache:
                insights.append(self.insights_cache[query_id])
                continue

            # Analyze scan efficiency (bytes scanned vs rows produced)
            if bytes_scanned > 1000000 and rows_produced > 0:  # > 1MB scanned
                bytes_per_row = bytes_scanned / rows_produced
                if bytes_per_row > 10000:  # > 10KB per row is inefficient
                    insight = QueryInsight(
                        query_id=query_id,
                        issue_type="inefficient_scan",
                        severity="high",
                        description=f"Query scanned {bytes_scanned/1024/1024:.1f}MB but only produced {rows_produced:,} rows ({bytes_per_row:.0f} bytes/row)",
                        impact=f"Execution time: {execution_time}ms. Poor scan efficiency indicates ineffective filters or joins.",
                        recommendation="Add WHERE clause predicates or review JOIN conditions to reduce scanned data",
                        estimated_improvement="30-50% query time reduction possible"
                    )
                    insights.append(insight)
                    self.insights_cache[query_id] = insight

            # Analyze execution time
            if execution_time > 30000:  # > 30 seconds
                insight = QueryInsight(
                    query_id=query_id,
                    issue_type="slow_execution",
                    severity="high",
                    description=f"Query execution time: {execution_time}ms ({execution_time/1000:.1f} seconds)",
                    impact="Long query execution times impact user experience and consume warehouse credits",
                    recommendation="Consider: (1) Adding indexes/clustering keys, (2) Partitioning large tables, (3) Query restructuring",
                    estimated_improvement="20-70% improvement likely with schema optimization"
                )
                insights.append(insight)
                self.insights_cache[query_id] = insight

        logger.info(f"[OK] Analyzed {len(slow_queries)} slow queries, found {len(insights)} issues")
        return insights

    def analyze_expensive_queries(self) -> List[QueryInsight]:
        """Identify queries consuming most credits."""
        expensive = self.connector.get_expensive_queries()
        insights = []

        for query in expensive:
            query_id = query.get("query_id")
            credits = query.get("credits_used", 0)
            execution_time = query.get("execution_time", 0)
            rows_produced = query.get("rows_produced", 0)

            if query_id in self.insights_cache:
                continue

            # Calculate cost per row
            cost_per_row = credits / rows_produced if rows_produced > 0 else 0

            insight = QueryInsight(
                query_id=query_id,
                issue_type="high_cost",
                severity="medium",
                description=f"Query consumed {credits:.2f} credits in {execution_time}ms",
                impact=f"High credit consumption: {cost_per_row:.6f} credits per row produced. Scales poorly with data volume.",
                recommendation="Optimize warehouse size, consider result caching, or add clustering keys to reduce scans",
                estimated_improvement=f"20-40% cost reduction with optimization (Save ~{credits*0.3:.2f} credits per run)"
            )
            insights.append(insight)
            self.insights_cache[query_id] = insight

        logger.info(f"[OK] Analyzed {len(expensive)} expensive queries, found {len(insights)} optimization opportunities")
        return insights

    def anomaly_detection(self, queries: List[Dict[str, Any]]) -> List[QueryInsight]:
        """Detect anomalous query patterns."""
        insights = []

        if not queries:
            return insights

        # Calculate statistics
        execution_times = [q.get("execution_time", 0) for q in queries]
        credits = [q.get("credits_used", 0) for q in queries]

        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        avg_credits = sum(credits) / len(credits) if credits else 0

        # Identify outliers (> 2x average)
        for query in queries:
            query_id = query.get("query_id")
            if query_id in self.insights_cache:
                continue

            exec_time = query.get("execution_time", 0)
            query_credits = query.get("credits_used", 0)

            if exec_time > avg_time * 2:
                insight = QueryInsight(
                    query_id=query_id,
                    issue_type="anomaly_slow",
                    severity="medium",
                    description=f"Query execution time ({exec_time}ms) is {exec_time/avg_time:.1f}x the average ({avg_time:.0f}ms)",
                    impact="Anomalous queries may indicate data skew, missing indexes, or changed table sizes",
                    recommendation="Investigate query plan, table statistics, and data distribution. Consider ANALYZE on tables.",
                    estimated_improvement="Normalize to baseline performance (25-50% improvement likely)"
                )
                insights.append(insight)
                self.insights_cache[query_id] = insight

        logger.info(f"✓ Detected {len(insights)} anomalous query patterns")
        return insights

    def get_query_plan_issues(self, query_text: str) -> List[str]:
        """Identify common issues from query text."""
        issues = []

        query_upper = query_text.upper()

        # Check for common anti-patterns
        if "SELECT *" in query_upper:
            issues.append("[ERROR] Uses SELECT * - specify only needed columns to reduce data transfer")

        if query_upper.count("JOIN") > 3:
            issues.append("[WARNING] Multiple JOINs (>3) - consider materialized views or denormalization")

        if "LIKE '%%" in query_upper or "LIKE '%%'" in query_upper:
            issues.append("[ERROR] Uses LIKE with leading wildcard - cannot use indexes efficiently")

        if "OR" in query_upper and "WHERE" in query_upper:
            issues.append("[WARNING] OR conditions may not use indexes efficiently - consider UNION ALL")

        if "DISTINCT" in query_upper and "GROUP BY" in query_upper:
            issues.append("[ERROR] Both DISTINCT and GROUP BY present - likely redundant")

        return issues
