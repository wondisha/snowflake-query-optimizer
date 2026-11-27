"""Cost optimization analyzer."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CostOptimization:
    """Represents a cost optimization opportunity."""
    category: str
    issue: str
    current_cost: float
    potential_savings: float
    savings_percentage: float
    priority: str
    description: str
    action_items: List[str]


class CostAnalyzer:
    """Analyzes Snowflake costs and identifies optimization opportunities."""

    def __init__(self, connector):
        """Initialize cost analyzer."""
        self.connector = connector
        self.credit_price = 2.0  # Default: $2 per credit (can be adjusted based on plan)

    def set_credit_price(self, price: float):
        """Set the price per credit for cost calculations."""
        self.credit_price = price

    def analyze_warehouse_efficiency(self) -> List[CostOptimization]:
        """Analyze warehouse usage and efficiency."""
        warehouse_data = self.connector.get_warehouse_usage(hours_back=168)  # 7 days
        optimizations = []

        if not warehouse_data:
            logger.warning("No warehouse usage data available")
            return optimizations

        # Group by warehouse
        warehouses = {}
        for record in warehouse_data:
            wh_name = record.get("warehouse_name")
            if wh_name not in warehouses:
                warehouses[wh_name] = []
            warehouses[wh_name].append(record)

        for wh_name, records in warehouses.items():
            total_credits = sum(r.get("credits_used", 0) for r in records)
            total_compute = sum(r.get("compute_time", 0) for r in records)
            total_waiting = sum(r.get("waiting_time", 0) for r in records)

            if total_compute > 0:
                waiting_ratio = total_waiting / (total_compute + total_waiting)

                # High waiting time suggests over-sized warehouse
                if waiting_ratio > 0.3:
                    potential_savings = total_credits * waiting_ratio * 0.4  # 40% of waiting time could be saved

                    opt = CostOptimization(
                        category="warehouse_sizing",
                        issue=f"Warehouse '{wh_name}' has {waiting_ratio*100:.1f}% idle time",
                        current_cost=total_credits * self.credit_price,
                        potential_savings=potential_savings * self.credit_price,
                        savings_percentage=(potential_savings / total_credits * 100) if total_credits > 0 else 0,
                        priority="high",
                        description=f"High wait time indicates queries queuing or warehouse over-provisioned",
                        action_items=[
                            f"1. Review warehouse '{wh_name}' cluster count",
                            "2. Consider auto-suspend settings (reduce to 1-2 minutes if currently higher)",
                            "3. Use multi-cluster warehouse with auto-scaling for variable loads",
                            f"4. Potential savings: ${potential_savings * self.credit_price:.2f}/week"
                        ]
                    )
                    optimizations.append(opt)

        logger.info(f"✓ Analyzed warehouse efficiency, found {len(optimizations)} optimization opportunities")
        return optimizations

    def analyze_query_costs(self) -> List[CostOptimization]:
        """Analyze per-query costs and identify expensive patterns."""
        expensive_queries = self.connector.get_expensive_queries(limit=20)
        optimizations = []

        if not expensive_queries:
            return optimizations

        total_cost = sum(q.get("credits_used", 0) for q in expensive_queries)
        top_query = expensive_queries[0] if expensive_queries else None

        if top_query:
            top_cost = top_query.get("credits_used", 0)
            other_cost = total_cost - top_cost

            cost_percentage = (top_cost/total_cost*100) if total_cost > 0 else 0

            opt = CostOptimization(
                category="query_optimization",
                issue=f"Top query alone costs {cost_percentage:.1f}% of these queries' total cost",
                current_cost=total_cost * self.credit_price,
                potential_savings=(top_cost * 0.5) * self.credit_price,  # 50% improvement potential
                savings_percentage=50.0,
                priority="critical",
                description="Single query consuming disproportionate resources",
                action_items=[
                    "1. Review top query's execution plan",
                    "2. Check if adding clustering keys would reduce scans",
                    "3. Consider result caching for repeated queries",
                    f"4. Potential savings: ${(top_cost * 0.5) * self.credit_price:.2f}/week"
                ]
            )
            optimizations.append(opt)

        logger.info(f"✓ Analyzed query costs, found {len(optimizations)} high-impact optimizations")
        return optimizations

    def analyze_storage_costs(self) -> List[CostOptimization]:
        """Analyze storage usage and archiving opportunities."""
        tables = self.connector.get_table_metadata()
        optimizations = []

        total_size = sum(t.get("bytes", 0) for t in tables)

        # Assuming $23 per TB per month for on-demand storage
        storage_price_per_tb_month = 23.0
        monthly_storage_cost = (total_size / (1024**4)) * storage_price_per_tb_month

        # Identify large tables that might benefit from archiving
        large_tables = sorted(
            [t for t in tables if t.get("bytes", 0) > 100 * (1024**6)],  # > 100MB
            key=lambda x: x.get("bytes", 0),
            reverse=True
        )

        if large_tables:
            largest = large_tables[0]
            largest_size_gb = largest.get("bytes", 0) / (1024**3)
            potential_archive = largest_size_gb * 0.3  # Assume 30% could be archived

            opt = CostOptimization(
                category="storage_archiving",
                issue=f"Large table '{largest.get('table_name')}' is {largest_size_gb:.1f}GB",
                current_cost=monthly_storage_cost,
                potential_savings=(potential_archive * storage_price_per_tb_month / 1024),
                savings_percentage=(potential_archive / largest_size_gb * 100) if largest_size_gb > 0 else 0,
                priority="medium",
                description="Consider archiving older data to reduce storage costs",
                action_items=[
                    f"1. Identify if {potential_archive:.1f}GB of old data can be archived",
                    "2. Use COPY INTO S3 to export historical data",
                    "3. Consider Iceberg tables with time-based partitioning",
                    f"4. Monthly storage savings: ${(potential_archive * storage_price_per_tb_month / 1024):.2f}"
                ]
            )
            optimizations.append(opt)

        logger.info(f"✓ Analyzed storage, found {len(optimizations)} archiving opportunities")
        return optimizations

    def generate_cost_report(self) -> Dict[str, Any]:
        """Generate comprehensive cost optimization report."""
        all_optimizations = []
        all_optimizations.extend(self.analyze_warehouse_efficiency())
        all_optimizations.extend(self.analyze_query_costs())
        all_optimizations.extend(self.analyze_storage_costs())

        total_potential_savings = sum(o.potential_savings for o in all_optimizations)

        return {
            "total_potential_savings": total_potential_savings,
            "total_potential_savings_annual": total_potential_savings * 52,  # Weekly to annual
            "optimizations_count": len(all_optimizations),
            "critical_count": len([o for o in all_optimizations if o.priority == "critical"]),
            "high_count": len([o for o in all_optimizations if o.priority == "high"]),
            "optimizations": all_optimizations
        }
