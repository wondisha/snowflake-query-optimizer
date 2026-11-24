"""Output formatting utilities."""

import json
from typing import List, Dict, Any


def format_insights(insights: List[Any]) -> str:
    """Format insights for display."""
    if not insights:
        return "No insights found."

    output = []
    for i, insight in enumerate(insights, 1):
        output.append(f"{i}. {insight.description}")
        output.append(f"   Impact: {insight.impact}")
        output.append(f"   Recommendation: {insight.recommendation}\n")

    return "\n".join(output)


def format_recommendations(recommendations: str) -> str:
    """Format LLM recommendations."""
    return recommendations


def format_json(data: Dict[str, Any]) -> str:
    """Format data as JSON."""
    return json.dumps(data, indent=2, default=str)


def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Format data as a simple table."""
    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Create separator
    separator = " | ".join("-" * (w + 2) for w in widths)

    # Create header
    header_row = " | ".join(f" {str(h):<{w}} " for h, w in zip(headers, widths))

    # Create rows
    data_rows = []
    for row in rows:
        data_rows.append(" | ".join(f" {str(cell):<{w}} " for cell, w in zip(row, widths)))

    # Combine
    output = [separator, header_row, separator] + data_rows + [separator]
    return "\n".join(output)
