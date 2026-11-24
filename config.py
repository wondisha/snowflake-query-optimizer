"""Configuration module for Snowflake Query Optimizer."""

import os
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv()

class SnowflakeConfig:
    """Snowflake connection configuration."""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema_name = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    role = os.getenv("SNOWFLAKE_ROLE")

class LLMConfig:
    """LLM configuration."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("LLM_MODEL", "claude-3-sonnet-20240229")
    temperature = float(os.getenv("LLM_TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", 2048))

class AppConfig:
    """Application configuration."""
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO")
    cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", 24))
    max_analysis_queries = int(os.getenv("MAX_ANALYSIS_QUERIES", 100))

def get_config():
    """Get merged configuration."""
    return {
        "snowflake": SnowflakeConfig(),
        "llm": LLMConfig(),
        "app": AppConfig(),
    }
