"""Schema and table structure analyzer."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SchemaRecommendation:
    """Represents a schema optimization recommendation."""
    table_name: str
    issue_type: str
    severity: str
    description: str
    current_state: str
    recommendation: str
    estimated_impact: str


class SchemaAnalyzer:
    """Analyzes schema design and table structures."""

    def __init__(self, connector):
        """Initialize schema analyzer."""
        self.connector = connector
        self.recommendations_cache = {}

    def analyze_table_structures(self) -> List[SchemaRecommendation]:
        """Analyze all table structures for optimization opportunities."""
        tables = self.connector.get_table_metadata()
        recommendations = []

        for table in tables:
            table_name = table.get("table_name")
            bytes_size = table.get("bytes", 0)
            row_count = table.get("row_count", 0)
            created = table.get("created")
            last_altered = table.get("last_altered")

            # Skip if cached
            if table_name in self.recommendations_cache:
                continue

            # Analyze large tables
            if bytes_size > 1_000_000_000:  # > 1GB
                rec = SchemaRecommendation(
                    table_name=table_name,
                    issue_type="large_table",
                    severity="medium",
                    description=f"Large table: {bytes_size / (1024**3):.2f}GB with {row_count:,} rows",
                    current_state=f"No identified clustering or partitioning strategy",
                    recommendation="Consider adding CLUSTERING KEY on frequently filtered columns (e.g., date, region) to improve query performance",
                    estimated_impact="30-60% faster queries on filtered data, reduced full scans"
                )
                recommendations.append(rec)
                self.recommendations_cache[table_name] = rec

            # Analyze growth
            if bytes_size > 500_000_000:  # > 500MB
                rec = SchemaRecommendation(
                    table_name=table_name,
                    issue_type="medium_table",
                    severity="low",
                    description=f"Medium-sized table: {bytes_size / (1024**2):.2f}MB",
                    current_state="Table structure optimization potential",
                    recommendation="Review if table needs Time Travel retention or if archiving older data could reduce storage costs",
                    estimated_impact="Storage cost reduction, improved query performance on recent data"
                )
                recommendations.append(rec)
                self.recommendations_cache[table_name] = rec

        logger.info(f"✓ Analyzed {len(tables)} tables, found {len(recommendations)} schema optimization opportunities")
        return recommendations

    def analyze_clustering_efficiency(self) -> List[SchemaRecommendation]:
        """Identify tables that would benefit from clustering."""
        tables = self.connector.get_table_metadata()
        recommendations = []

        # Identify large tables without evident clustering strategy
        large_tables = [t for t in tables if t.get("bytes", 0) > 1_000_000_000]

        for table in large_tables:
            table_name = table.get("table_name")
            schema_name = table.get("table_schema")

            if table_name in self.recommendations_cache:
                continue

            # Check clustering info
            clustering_info = self.connector.get_table_clustering_info(table_name)

            if clustering_info and not clustering_info.get("clustering_key"):
                rec = SchemaRecommendation(
                    table_name=table_name,
                    issue_type="no_clustering",
                    severity="high",
                    description=f"{schema_name}.{table_name} has no clustering key",
                    current_state="Table scans are likely inefficient for filtered queries",
                    recommendation="Identify frequently filtered columns (date, customer_id, region) and create CLUSTERING KEY.\nExample: ALTER TABLE table_name CLUSTER BY (date_column);",
                    estimated_impact="40-70% improvement in filtered query performance, 20-30% credit savings on typical workloads"
                )
                recommendations.append(rec)
                self.recommendations_cache[table_name] = rec

        logger.info(f"✓ Analyzed clustering efficiency, found {len(recommendations)} tables needing clustering keys")
        return recommendations

    def analyze_data_types(self, schema_name: str = None) -> List[SchemaRecommendation]:
        """Identify inefficient data type usage."""
        recommendations = []

        # Query information_schema for all columns
        query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns
        WHERE table_schema NOT IN ('INFORMATION_SCHEMA', 'TEMP')
        """

        if schema_name:
            query += f" AND table_schema = '{schema_name}'"

        try:
            columns = self.connector.execute_query(query)

            for col in columns:
                table_name = col.get("table_name")
                column_name = col.get("column_name")
                data_type = col.get("data_type")

                # Check for VARCHAR with large precision
                if data_type.startswith("VARCHAR") and not table_name in self.recommendations_cache:
                    if "(" in data_type:
                        precision = int(data_type.split("(")[1].split(")")[0])
                        if precision > 1000:
                            rec = SchemaRecommendation(
                                table_name=table_name,
                                issue_type="oversized_varchar",
                                severity="low",
                                description=f"{table_name}.{column_name} uses VARCHAR({precision})",
                                current_state="Unnecessarily large VARCHAR may waste storage",
                                recommendation=f"Review actual string lengths. Consider reducing to VARCHAR({precision//10}) if appropriate",
                                estimated_impact="Minimal storage savings, potential query optimization"
                            )
                            recommendations.append(rec)
                            break

        except Exception as e:
            logger.warning(f"Could not analyze data types: {e}")

        logger.info(f"✓ Analyzed data types, found {len(recommendations)} inefficiencies")
        return recommendations

    def get_database_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics and recommendations."""
        stats = self.connector.get_database_stats()

        return {
            "total_tables": stats.get("table_count", 0),
            "total_size_gb": stats.get("total_size_bytes", 0) / (1024**3),
            "avg_table_size_mb": stats.get("avg_table_size_bytes", 0) / (1024**2),
            "recommendations": {
                "review_archiving": stats.get("total_size_bytes", 0) > 100 * (1024**9),  # > 100GB
                "implement_clustering": stats.get("avg_table_size_bytes", 0) > 500 * (1024**6),  # > 500MB avg
                "optimize_data_types": True,  # Always recommend review
            }
        }
