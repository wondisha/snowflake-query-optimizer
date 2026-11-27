"""LLM orchestrator for agentic analysis."""

import logging
from typing import List, Dict, Any
from anthropic import Anthropic

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
        self.last_analysis = None  # Store analysis for chat context

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

    def _prepare_analysis_context(self) -> str:
        """Prepare analysis context for chat."""
        if not self.last_analysis:
            return "No prior analysis available."

        insights = self.last_analysis.get("raw_insights", {})
        recommendations = self.last_analysis.get("llm_recommendations", "")

        context = "## Current Database Analysis:\n\n"

        # Query issues
        query_data = insights.get("query_insights", {})
        slow_queries = query_data.get("slow_queries", [])
        expensive_queries = query_data.get("expensive_queries", [])

        if slow_queries:
            context += f"**Slow Queries Found: {len(slow_queries)}**\n"
            for q in slow_queries[:3]:
                context += f"- Query: {q.get('query_id', 'N/A')} ({q.get('execution_time_seconds', 0)}s)\n"

        if expensive_queries:
            context += f"\n**Expensive Queries Found: {len(expensive_queries)}**\n"
            for q in expensive_queries[:3]:
                context += f"- Query: {q.get('query_id', 'N/A')} (${q.get('cost', 0):.2f} per run)\n"

        # Schema issues
        schema_data = insights.get("schema_insights", {})
        table_issues = schema_data.get("table_structures", [])
        clustering_issues = schema_data.get("clustering", [])

        if table_issues:
            context += f"\n**Table Optimization Opportunities: {len(table_issues)}**\n"
            for t in table_issues[:3]:
                context += f"- Table: {t.get('table_name', 'N/A')} ({t.get('size_gb', 0)}GB)\n"

        if clustering_issues:
            context += f"\n**Clustering Opportunities: {len(clustering_issues)}**\n"
            for c in clustering_issues[:3]:
                context += f"- Table: {c.get('table_name', 'N/A')} - Suggested keys: {c.get('recommended_keys', 'N/A')}\n"

        # Cost data
        cost_data = insights.get("cost_insights", {})
        weekly_savings = cost_data.get("total_potential_savings", 0)
        annual_savings = cost_data.get("total_potential_savings_annual", 0)

        if weekly_savings > 0:
            context += f"\n**Cost Optimization Potential:**\n"
            context += f"- Weekly Savings: ${weekly_savings:.2f}\n"
            context += f"- Annual Savings: ${annual_savings:.2f}\n"

        # Workload patterns
        workload_data = insights.get("workload_insights", {})
        if workload_data.get("high_impact_patterns"):
            context += f"\n**High Impact Patterns:**\n"
            for p in workload_data.get("high_impact_patterns", [])[:3]:
                context += f"- {p}\n"

        # Include LLM recommendations summary
        if recommendations:
            context += f"\n**AI Recommendations Summary:**\n{recommendations[:500]}...\n"

        return context

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

    def interactive_chat(self, user_query: str) -> str:
        """Have an interactive conversation about the analysis with context."""
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        try:
            # Build system prompt with analysis context
            system_prompt = """You are an expert Snowflake database optimization consultant.
You have access to analysis results from their database and should provide SPECIFIC, ACTIONABLE solutions.

**RESPONSE GUIDELINES:**
1. Always provide concrete SQL examples or implementation steps
2. Quantify impact (cost savings, performance improvement, time to implement)
3. Prioritize by business impact - highest ROI first
4. If asked about issues, provide exact SQL to fix them
5. Include before/after scenarios
6. Be direct and practical, not theoretical

**RESPONSE FORMAT:**
- Problem: [specific issue]
- Root Cause: [why it's happening]
- Solution: [exact SQL or steps]
- Impact: [quantified benefit]
- Time to Implement: [estimate]

NEVER just describe problems - ALWAYS provide solutions with SQL when applicable."""

            # Add analysis context if available
            if self.last_analysis:
                context = self._prepare_analysis_context()
                system_prompt += f"\n\n**ANALYSIS DATA FOR REFERENCE:**\n{context}"

            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt,
                messages=self.conversation_history
            )

            assistant_message = self._extract_text_from_response(response)
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            return "Sorry, I encountered an error. Please try again."

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
