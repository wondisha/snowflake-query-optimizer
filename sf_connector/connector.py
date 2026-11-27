"""Snowflake connector module for database operations."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError

logger = logging.getLogger(__name__)


class SnowflakeConnector:
    """Manages Snowflake connections and queries."""

    def __init__(self, config):
        """Initialize Snowflake connector."""
        self.config = config
        self.connection = None
        self._verify_connection()

    def _verify_connection(self):
        """Verify connection to Snowflake."""
        try:
            self.connection = snowflake.connector.connect(
                user=self.config.user,
                password=self.config.password,
                account=self.config.account,
                database=self.config.database,
                schema=self.config.schema_name,
                warehouse=self.config.warehouse,
                role=self.config.role,
            )
            logger.info("[OK] Successfully connected to Snowflake")
            return True
        except DatabaseError as e:
            logger.error(f"[ERROR] Failed to connect to Snowflake: {e}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        except ProgrammingError as e:
            logger.error(f"Query execution error: {e}")
            raise

    def get_query_history(self, limit: int = 100, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Fetch recent query history from QUERY_HISTORY."""
        query = f"""
        SELECT
            query_id,
            query_text,
            database_name,
            schema_name,
            user_name,
            role_name,
            warehouse_name,
            query_type,
            execution_time,
            total_elapsed_time,
            bytes_scanned as rows_scanned,
            rows_produced,
            execution_status,
            start_time,
            end_time,
            credits_used
        FROM snowflake.account_usage.query_history
        WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '{hours_back} hours'
        ORDER BY start_time DESC
        LIMIT {limit}
        """
        return self.execute_query(query)

    def get_table_metadata(self) -> List[Dict[str, Any]]:
        """Fetch metadata about tables in the current database."""
        query = f"""
        SELECT
            table_catalog,
            table_schema,
            table_name,
            table_type,
            row_count,
            bytes,
            created,
            last_altered
        FROM information_schema.tables
        WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
        ORDER BY bytes DESC
        """
        return self.execute_query(query)

    def get_warehouse_usage(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Fetch warehouse usage metrics."""
        query = f"""
        SELECT
            warehouse_name,
            DATE_TRUNC('HOUR', start_time) as hour,
            SUM(credits_used) as credits_used
        FROM snowflake.account_usage.warehouse_metering_history
        WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL '{hours_back} hours'
        GROUP BY warehouse_name, DATE_TRUNC('HOUR', start_time)
        ORDER BY hour DESC
        """
        return self.execute_query(query)

    def get_slow_queries(self, threshold_ms: int = 5000, limit: int = 50) -> List[Dict[str, Any]]:
        """Identify slow running queries."""
        query = f"""
        SELECT
            query_id,
            query_text,
            database_name,
            schema_name,
            user_name,
            warehouse_name,
            execution_time,
            bytes_scanned,
            rows_produced,
            start_time,
            credits_used_cloud_services as credits_used
        FROM snowflake.account_usage.query_history
        WHERE execution_time >= {threshold_ms}
        AND execution_status = 'SUCCESS'
        AND start_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        ORDER BY execution_time DESC
        LIMIT {limit}
        """
        return self.execute_query(query)

    def get_expensive_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Identify expensive queries by credit usage."""
        query = f"""
        SELECT
            query_id,
            query_text,
            database_name,
            schema_name,
            user_name,
            warehouse_name,
            execution_time,
            credits_used_cloud_services as credits_used,
            rows_produced,
            start_time
        FROM snowflake.account_usage.query_history
        WHERE credits_used_cloud_services > 0
        AND execution_status = 'SUCCESS'
        AND start_time >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        ORDER BY credits_used_cloud_services DESC
        LIMIT {limit}
        """
        return self.execute_query(query)

    def get_table_clustering_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get clustering information for a specific table."""
        query = f"""
        SELECT
            table_name,
            clustering_key,
            bytes_scanned,
            bytes_scanned_by_subquery_predicate,
            bytes_scanned_by_external_predicate
        FROM snowflake.account_usage.tables
        WHERE table_name = '{table_name}'
        """
        results = self.execute_query(query)
        return results[0] if results else None

    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        queries = {
            "table_count": "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema NOT IN ('INFORMATION_SCHEMA')",
            "total_size_bytes": "SELECT SUM(bytes) as total FROM information_schema.tables WHERE table_schema NOT IN ('INFORMATION_SCHEMA')",
            "avg_table_size_bytes": "SELECT AVG(bytes) as avg FROM information_schema.tables WHERE table_schema NOT IN ('INFORMATION_SCHEMA')",
        }

        stats = {}
        for key, query in queries.items():
            result = self.execute_query(query)
            stats[key] = result[0].get(result[0].keys().__iter__().__next__()) if result else 0

        return stats

    def close(self):
        """Close the Snowflake connection."""
        if self.connection:
            self.connection.close()
            logger.info("Snowflake connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
