"""
Adaptive queries for different Snowflake setups and permission levels
Automatically adjusts SQL based on available views and columns
"""

class AdaptiveQueries:
    """Provides alternative queries when standard ones fail"""

    # QUERY_HISTORY alternatives
    SLOW_QUERIES_LIGHT = """
    -- Lightweight: No QUERY_HISTORY access required
    SELECT 
        t.TABLE_NAME,
        COUNT(*) as query_count,
        SUM(t.BYTES) as estimated_data_volume,
        'estimated' as source
    FROM INFORMATION_SCHEMA.TABLES t
    WHERE t.TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA', 'TEMP')
    GROUP BY t.TABLE_NAME
    ORDER BY SUM(t.BYTES) DESC
    LIMIT 50
    """

    SLOW_QUERIES_WITH_STATS = """
    -- Alternative: Uses table statistics
    SELECT 
        SCHEMA_NAME,
        TABLE_NAME,
        'TABLE_STATS' as source,
        CREATED,
        LAST_ALTERED
    FROM INFORMATION_SCHEMA.TABLES
    WHERE BYTES > 1000000000  -- > 1GB
    ORDER BY BYTES DESC
    LIMIT 50
    """

    EXPENSIVE_QUERIES_PROXY = """
    -- Proxy: Identify potentially expensive tables
    SELECT
        t.TABLE_SCHEMA,
        t.TABLE_NAME,
        t.BYTES as estimated_cost_indicator,
        COUNT(c.COLUMN_NAME) as column_count
    FROM INFORMATION_SCHEMA.TABLES t
    LEFT JOIN INFORMATION_SCHEMA.COLUMNS c 
        ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
        AND t.TABLE_NAME = c.TABLE_NAME
    WHERE t.TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA', 'TEMP')
    GROUP BY t.TABLE_SCHEMA, t.TABLE_NAME, t.BYTES
    ORDER BY t.BYTES DESC
    LIMIT 50
    """

    # Warehouse usage alternatives
    WAREHOUSE_USAGE_LIGHT = """
    -- Lightweight warehouse analysis
    SHOW WAREHOUSES;
    """

    WAREHOUSE_USAGE_DETAILS = """
    -- Warehouse configuration details
    SELECT 
        WAREHOUSE_NAME,
        WAREHOUSE_SIZE,
        STATE,
        CREATED_ON
    FROM INFORMATION_SCHEMA.APPLICABLE_ROLES
    CROSS JOIN (
        SELECT DISTINCT WAREHOUSE_NAME 
        FROM INFORMATION_SCHEMA.LOAD_HISTORY 
        LIMIT 1000
    )
    """

    # Clustering analysis alternatives  
    CLUSTERING_CANDIDATES = """
    -- Identify tables that would benefit from clustering
    SELECT
        t.TABLE_SCHEMA,
        t.TABLE_NAME,
        t.BYTES,
        t.ROW_COUNT,
        CASE 
            WHEN t.BYTES > 1000000000 THEN 'High Priority'
            WHEN t.BYTES > 100000000 THEN 'Medium Priority'
            ELSE 'Low Priority'
        END as priority
    FROM INFORMATION_SCHEMA.TABLES t
    WHERE t.TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA', 'TEMP')
    ORDER BY t.BYTES DESC
    """

    # Data type efficiency
    DATA_TYPE_ANALYSIS = """
    -- Analyze data type efficiency
    SELECT
        t.TABLE_SCHEMA,
        t.TABLE_NAME,
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.CHARACTER_MAXIMUM_LENGTH,
        COUNT(*) OVER (PARTITION BY t.TABLE_NAME) as column_count
    FROM INFORMATION_SCHEMA.TABLES t
    JOIN INFORMATION_SCHEMA.COLUMNS c 
        ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
        AND t.TABLE_NAME = c.TABLE_NAME
    WHERE t.TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA', 'TEMP')
    ORDER BY t.BYTES DESC
    LIMIT 100
    """

    @staticmethod
    def get_query(query_type: str, permission_level: str = "standard"):
        """
        Get appropriate query based on type and permission level
        
        Args:
            query_type: 'slow_queries', 'expensive_queries', 'warehouse_usage', 'clustering', 'data_types'
            permission_level: 'full', 'standard', 'light'
        
        Returns:
            SQL query string
        """
        
        if query_type == "slow_queries":
            if permission_level == "full":
                return AdaptiveQueries.SLOW_QUERIES_WITH_STATS
            else:
                return AdaptiveQueries.SLOW_QUERIES_LIGHT

        elif query_type == "expensive_queries":
            return AdaptiveQueries.EXPENSIVE_QUERIES_PROXY

        elif query_type == "warehouse_usage":
            if permission_level == "full":
                return AdaptiveQueries.WAREHOUSE_USAGE_DETAILS
            else:
                return AdaptiveQueries.WAREHOUSE_USAGE_LIGHT

        elif query_type == "clustering":
            return AdaptiveQueries.CLUSTERING_CANDIDATES

        elif query_type == "data_types":
            return AdaptiveQueries.DATA_TYPE_ANALYSIS

        return None


# Usage example
if __name__ == "__main__":
    print("Slow Queries (Light):")
    print(AdaptiveQueries.get_query("slow_queries", "light"))
    print("\n\nClustering Candidates:")
    print(AdaptiveQueries.get_query("clustering"))
