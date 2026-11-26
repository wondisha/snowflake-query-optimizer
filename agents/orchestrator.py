"""LLM orchestrator for agentic analysis."""

import json
import logging
import re
from typing import List, Dict, Any
from anthropic import Anthropic, AuthenticationError

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """Orchestrates analysis using LLM to provide intelligent insights."""

    def __init__(self, config, query_analyzer, schema_analyzer, cost_analyzer, workload_analyzer):
        """Initialize LLM orchestrator."""
        self.config = config
        self.query_analyzer = query_analyzer
        self.schema_analyzer = schema_analyzer
        self.cost_analyzer = cost_analyzer
        self.workload_analyzer = workload_analyzer
        self.client = Anthropic(api_key=config.api_key)
        self.conversation_history = []

    def analyze_comprehensive(self) -> Dict[str, Any]:
        """Perform comprehensive analysis and provide recommendations."""
        logger.info("🚀 Starting comprehensive Snowflake optimization analysis...")

        # Gather insights from all analyzers
        insights = {
            "query_insights": {
                "slow_queries": self.query_analyzer.analyze_slow_queries(),
                "expensive_queries": self.query_analyzer.analyze_expensive_queries(),
            },
            "schema_insights": {
                "table_structures": self.schema_analyzer.analyze_table_structures(),
                "clustering": self.schema_analyzer.analyze_clustering_efficiency(),
            },
            "cost_insights": self.cost_analyzer.generate_cost_report(),
            "workload_insights": self.workload_analyzer.generate_workload_summary(),
        }

        # Prepare prompt for LLM
        analysis_summary = self._prepare_analysis_summary(insights)

        # Get LLM recommendations
        recommendations = self._get_llm_recommendations(analysis_summary)

        return {
            "timestamp": str(__import__("datetime").datetime.now()),
            "raw_insights": insights,
            "llm_recommendations": recommendations,
            "summary": self._generate_summary(insights, recommendations)
        }

    def _prepare_analysis_summary(self, insights: Dict[str, Any]) -> str:
        """Prepare analysis data for LLM."""
        summary = "# Snowflake Database Analysis Summary\n\n"

        # Query Performance
        slow_count = len(insights["query_insights"]["slow_queries"])
        expensive_count = len(insights["query_insights"]["expensive_queries"])
        summary += f"## Query Performance\n"
        summary += f"- Slow queries found: {slow_count}\n"
        summary += f"- Expensive queries found: {expensive_count}\n\n"

        # Schema Issues
        table_issues = len(insights["schema_insights"]["table_structures"])
        clustering_issues = len(insights["schema_insights"]["clustering"])
        summary += f"## Schema Structure\n"
        summary += f"- Table optimization opportunities: {table_issues}\n"
        summary += f"- Clustering opportunities: {clustering_issues}\n\n"

        # Cost Analysis
        cost_data = insights["cost_insights"]
        summary += f"## Cost Optimization\n"
        summary += f"- Total potential savings: ${cost_data.get('total_potential_savings', 0):.2f} per week\n"
        summary += f"- Annual potential savings: ${cost_data.get('total_potential_savings_annual', 0):.2f}\n"
        summary += f"- Critical optimizations: {cost_data.get('critical_count', 0)}\n"
        summary += f"- High priority optimizations: {cost_data.get('high_count', 0)}\n\n"

        # Workload Patterns
        workload_data = insights["workload_insights"]
        summary += f"## Workload Patterns\n"
        summary += f"- Total patterns identified: {workload_data.get('total_patterns', 0)}\n"
        summary += f"- High impact patterns: {workload_data.get('high_impact_count', 0)}\n"
        summary += f"- Medium impact patterns: {workload_data.get('medium_impact_count', 0)}\n"

        return summary

    def _extract_text_from_response(self, response):
        """Extract text from response, handling thinking blocks."""
        for block in response.content:
            if hasattr(block, 'text'):
                return block.text
        # If no text block found, return empty string
        return ""

    def _get_llm_recommendations(self, analysis_summary: str) -> str:
        """Get LLM recommendations based on analysis."""
        system_prompt = """You are an expert Snowflake database optimization consultant.
Analyze the provided database analysis summary and provide:
1. Top 3 immediate actions to improve performance
2. Top 3 cost optimization opportunities
3. Priority ranking and estimated impact
4. Implementation steps for each recommendation
Be specific, actionable, and data-driven. Provide SQL examples where relevant."""

        self.conversation_history = [
            {
                "role": "user",
                "content": f"{system_prompt}\n\nAnalysis Summary:\n{analysis_summary}"
            }
        ]

        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": analysis_summary}]
            )

            recommendations = self._extract_text_from_response(response)
            self.conversation_history.append({
                "role": "assistant",
                "content": recommendations
            })

            return recommendations
        except Exception as e:
            logger.error(f"Error getting LLM recommendations: {e}")
            return "Unable to generate LLM recommendations at this time."

    TOOLS = [
        {
            "name": "run_readonly_sql",
            "description": "Run a read-only statement (SELECT, SHOW, DESCRIBE, EXPLAIN) in Snowflake to investigate an issue, e.g. query history, spilling, warehouse load, table clustering.",
            "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]},
        },
        {
            "name": "propose_fix",
            "description": "Propose a statement that changes Snowflake (ALTER, CREATE, CLUSTER BY, etc.). The user is asked to approve it before it runs. Only call after diagnosing the issue.",
            "input_schema": {
                "type": "object",
                "properties": {"sql": {"type": "string"}, "reason": {"type": "string"}},
                "required": ["sql", "reason"],
            },
        },
    ]

    READONLY_PREFIXES = ("select", "show", "describe", "desc", "explain", "with")
    FORBIDDEN_IN_READONLY = ("insert", "update", "delete", "merge", "drop", "alter", "create",
                             "truncate", "grant", "revoke", "call", "copy", "put", "remove", "use")
    BLOCKED_FIXES = ("drop database", "drop schema", "drop table", "truncate", "delete", "grant", "revoke")

    CHAT_SYSTEM = """You are an expert Snowflake optimization agent.
When the user reports a slow query, spill, error or cost problem:
1. Investigate with run_readonly_sql (e.g. INFORMATION_SCHEMA.QUERY_HISTORY, bytes_spilled_*, warehouse size, EXPLAIN).
2. State the root cause with evidence.
3. If a change would fix it, call propose_fix with the exact SQL and the reason. The user approves or rejects it; never assume approval.
4. After an approved fix runs, verify it and report. If rejected, offer alternatives.
Prefer the least invasive fix. Be concise."""

    def _is_readonly(self, sql: str) -> bool:
        cleaned = sql.strip().rstrip(";").strip().lower()
        if ";" in cleaned or not cleaned.startswith(self.READONLY_PREFIXES):
            return False
        words = set(re.findall(r"[a-z_]+", cleaned))
        return not words.intersection(self.FORBIDDEN_IN_READONLY)

    def _run_tool(self, name: str, args: Dict[str, Any], approval_callback) -> str:
        connector = self.query_analyzer.connector
        sql = args.get("sql", "")
        try:
            if name == "run_readonly_sql":
                if not self._is_readonly(sql):
                    return "Rejected: only a single read-only statement is allowed here. Use propose_fix for changes."
                rows = connector.execute_query(sql)
                return json.dumps(rows[:50], default=str)[:8000]
            if name == "propose_fix":
                if any(b in sql.lower() for b in self.BLOCKED_FIXES):
                    return "Rejected: this statement is destructive and not allowed."
                if approval_callback is None or not approval_callback(sql, args.get("reason", "")):
                    return "The user REJECTED this change. Do not run it. Suggest alternatives."
                result = connector.execute_query(sql)
                return "Executed successfully. " + json.dumps(result[:20], default=str)[:2000]
            return f"Unknown tool {name}"
        except Exception as e:
            return f"Tool error: {e}"

    def interactive_chat(self, user_query: str, approval_callback=None, max_steps: int = 8) -> str:
        """Agentic chat: investigates issues and applies fixes only after approval.

        approval_callback(sql, reason) -> bool must return True to allow execution.
        """
        start_len = len(self.conversation_history)
        self.conversation_history.append({"role": "user", "content": user_query})

        try:
            for _ in range(max_steps):
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    system=self.CHAT_SYSTEM,
                    tools=self.TOOLS,
                    messages=self.conversation_history,
                )
                self.conversation_history.append({
                    "role": "assistant",
                    "content": [b.model_dump(exclude_none=True) for b in response.content],
                })

                tool_uses = [b for b in response.content if b.type == "tool_use"]
                if not tool_uses:
                    return self._extract_text_from_response(response)

                results = [{
                    "type": "tool_result",
                    "tool_use_id": t.id,
                    "content": self._run_tool(t.name, t.input, approval_callback),
                } for t in tool_uses]
                self.conversation_history.append({"role": "user", "content": results})

            return "Stopped after reaching the step limit. Ask me to continue."
        except AuthenticationError:
            logger.error("Anthropic authentication failed")
            del self.conversation_history[start_len:]
            return "Authentication failed: ANTHROPIC_API_KEY is invalid. Update it and restart."
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            if "credit balance is too low" in str(e):
                del self.conversation_history[start_len:]
                return "Anthropic credit balance is too low. Add credits under Plans & Billing in the Anthropic Console, then retry."
            del self.conversation_history[start_len:]
            return f"Sorry, I encountered an error: {e}"

    def _generate_summary(self, insights: Dict[str, Any], recommendations: str) -> Dict[str, Any]:
        """Generate executive summary."""
        cost_data = insights["cost_insights"]

        return {
            "total_issues_found": (
                len(insights["query_insights"]["slow_queries"]) +
                len(insights["query_insights"]["expensive_queries"]) +
                len(insights["schema_insights"]["table_structures"]) +
                len(insights["schema_insights"]["clustering"]) +
                len(cost_data.get("optimizations", []))
            ),
            "critical_issues": cost_data.get("critical_count", 0),
            "potential_weekly_savings": f"${cost_data.get('total_potential_savings', 0):.2f}",
            "potential_annual_savings": f"${cost_data.get('total_potential_savings_annual', 0):.2f}",
            "recommendations_summary": recommendations[:500] + "..." if len(recommendations) > 500 else recommendations
        }
