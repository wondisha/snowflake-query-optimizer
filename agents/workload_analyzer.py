"""Workload pattern analyzer."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class WorkloadPattern:
    """Represents a workload pattern insight."""
    pattern_type: str
    description: str
    affected_items: List[str]
    observation: str
    recommendation: str
    impact_level: str


class WorkloadAnalyzer:
    """Analyzes Snowflake workload patterns and usage trends."""

    def __init__(self, connector):
        """Initialize workload analyzer."""
        self.connector = connector

    def analyze_user_workloads(self) -> List[WorkloadPattern]:
        """Analyze query patterns by user."""
        query_history = self.connector.get_query_history(hours_back=168, limit=500)  # 7 days
        patterns = []

        # Group queries by user
        user_queries = defaultdict(list)
        for query in query_history:
            user = query.get("user_name")
            if user:
                user_queries[user].append(query)

        # Analyze per-user patterns
        for user, queries in user_queries.items():
            if len(queries) < 5:
                continue

            total_credits = sum(q.get("credits_used", 0) for q in queries)
            avg_execution_time = sum(q.get("execution_time", 0) for q in queries) / len(queries)
            failed_count = len([q for q in queries if q.get("execution_status") != "SUCCESS"])

            # High error rate
            if failed_count / len(queries) > 0.1:
                pattern = WorkloadPattern(
                    pattern_type="high_error_rate",
                    description=f"User '{user}' has {failed_count/len(queries)*100:.1f}% query failure rate",
                    affected_items=[user],
                    observation=f"{failed_count} failures out of {len(queries)} queries",
                    recommendation="Review failed queries for syntax errors, permission issues, or missing tables. May need training or access corrections.",
                    impact_level="medium"
                )
                patterns.append(pattern)

            # Power user (high credit usage)
            if total_credits > 100:
                pattern = WorkloadPattern(
                    pattern_type="power_user",
                    description=f"User '{user}' is consuming {total_credits:.0f} credits over 7 days",
                    affected_items=[user],
                    observation=f"Average query time: {avg_execution_time/1000:.2f}s, Total: {len(queries)} queries",
                    recommendation="Prioritize optimization for this user's queries. Consider dedicated small warehouse or query caching.",
                    impact_level="high"
                )
                patterns.append(pattern)

        logger.info(f"✓ Analyzed {len(user_queries)} user workloads, found {len(patterns)} patterns")
        return patterns

    def analyze_database_workloads(self) -> List[WorkloadPattern]:
        """Analyze query patterns by database."""
        query_history = self.connector.get_query_history(hours_back=168, limit=500)
        patterns = []

        # Group by database
        db_queries = defaultdict(list)
        for query in query_history:
            db = query.get("database_name")
            if db:
                db_queries[db].append(query)

        for db, queries in db_queries.items():
            total_credits = sum(q.get("credits_used", 0) for q in queries)
            avg_rows_scanned = sum(q.get("rows_scanned", 0) for q in queries) / len(queries) if queries else 0

            # Database with disproportionate credit usage
            if len(db_queries) > 1:
                avg_per_db = sum(sum(q.get("credits_used", 0) for q in qs) for qs in db_queries.values()) / len(db_queries)
                if total_credits > avg_per_db * 2:
                    pattern = WorkloadPattern(
                        pattern_type="high_usage_database",
                        description=f"Database '{db}' consuming {total_credits/avg_per_db:.1f}x average credit usage",
                        affected_items=[db],
                        observation=f"Total credits: {total_credits:.0f} (avg per DB: {avg_per_db:.0f})",
                        recommendation="Investigate queries targeting this database. Apply clustering keys, consider data compression, or query restructuring.",
                        impact_level="high"
                    )
                    patterns.append(pattern)

        logger.info(f"✓ Analyzed {len(db_queries)} database workloads, found {len(patterns)} patterns")
        return patterns

    def analyze_temporal_patterns(self) -> List[WorkloadPattern]:
        """Analyze query patterns over time."""
        query_history = self.connector.get_query_history(hours_back=168, limit=500)
        patterns = []

        # Group by hour
        hourly_queries = defaultdict(list)
        for query in query_history:
            start_time = query.get("start_time")
            if isinstance(start_time, str):
                # Extract hour
                hour = start_time.split("T")[1].split(":")[0] if "T" in start_time else "00"
            else:
                hour = start_time.hour if hasattr(start_time, 'hour') else "00"

            hourly_queries[hour].append(query)

        # Find peak hours
        peak_hour = max(hourly_queries.items(), key=lambda x: len(x[1])) if hourly_queries else None

        if peak_hour:
            hour, queries = peak_hour
            credits_in_peak = sum(q.get("credits_used", 0) for q in queries)
            avg_credits_other = sum(
                sum(q.get("credits_used", 0) for q in qs) for h, qs in hourly_queries.items() if h != hour
            ) / (len(hourly_queries) - 1) if len(hourly_queries) > 1 else 0

            if credits_in_peak > avg_credits_other * 1.5:
                pattern = WorkloadPattern(
                    pattern_type="peak_hours",
                    description=f"Hour {hour}:00 is a peak period with {len(queries)} queries",
                    affected_items=[f"Hour {hour}:00"],
                    observation=f"Credits in peak hour: {credits_in_peak:.0f} vs avg other hours: {avg_credits_other:.0f}",
                    recommendation="Consider scaling warehouse up during peak hours using auto-scaling, or distributing workloads across time.",
                    impact_level="medium"
                )
                patterns.append(pattern)

        logger.info(f"✓ Analyzed temporal patterns, found {len(patterns)} insights")
        return patterns

    def analyze_warehouse_distribution(self) -> List[WorkloadPattern]:
        """Analyze query distribution across warehouses."""
        query_history = self.connector.get_query_history(hours_back=168, limit=500)
        patterns = []

        # Group by warehouse
        wh_queries = defaultdict(list)
        for query in query_history:
            wh = query.get("warehouse_name")
            if wh:
                wh_queries[wh].append(query)

        # Identify underutilized warehouses
        for wh, queries in wh_queries.items():
            query_count = len(queries)
            total_credits = sum(q.get("credits_used", 0) for q in queries)

            if query_count < 10 and total_credits < 10:
                pattern = WorkloadPattern(
                    pattern_type="underutilized_warehouse",
                    description=f"Warehouse '{wh}' is underutilized ({query_count} queries, {total_credits:.1f} credits)",
                    affected_items=[wh],
                    observation="Low activity warehouse may be redundant or used only by specific teams",
                    recommendation="Consider consolidating queries to fewer warehouses to reduce maintenance and licensing costs.",
                    impact_level="low"
                )
                patterns.append(pattern)

        logger.info(f"✓ Analyzed warehouse distribution, found {len(patterns)} patterns")
        return patterns

    def generate_workload_summary(self) -> Dict[str, Any]:
        """Generate comprehensive workload analysis summary."""
        all_patterns = []
        all_patterns.extend(self.analyze_user_workloads())
        all_patterns.extend(self.analyze_database_workloads())
        all_patterns.extend(self.analyze_temporal_patterns())
        all_patterns.extend(self.analyze_warehouse_distribution())

        high_impact = len([p for p in all_patterns if p.impact_level == "high"])
        medium_impact = len([p for p in all_patterns if p.impact_level == "medium"])

        return {
            "total_patterns": len(all_patterns),
            "high_impact_count": high_impact,
            "medium_impact_count": medium_impact,
            "patterns": all_patterns
        }
