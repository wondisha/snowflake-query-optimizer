"""Snowflake Query Optimizer Package."""

__version__ = "1.0.0"
__author__ = "Optimization Team"

from .config import get_config
from .sf_connector.connector import SnowflakeConnector
from .agents.query_analyzer import QueryAnalyzer
from .agents.schema_analyzer import SchemaAnalyzer
from .agents.cost_analyzer import CostAnalyzer
from .agents.workload_analyzer import WorkloadAnalyzer
from .agents.orchestrator import LLMOrchestrator

__all__ = [
    'get_config',
    'SnowflakeConnector',
    'QueryAnalyzer',
    'SchemaAnalyzer',
    'CostAnalyzer',
    'WorkloadAnalyzer',
    'LLMOrchestrator',
]
