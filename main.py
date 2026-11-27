"""Main CLI interface for Snowflake Query Optimizer."""

# Windows AppStore Python 3.13 compatibility fix
import platform_fix

import logging
import sys
from typing import Optional
import click
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from sf_connector.connector import SnowflakeConnector
from agents.query_analyzer import QueryAnalyzer
from agents.schema_analyzer import SchemaAnalyzer
from agents.cost_analyzer import CostAnalyzer
from agents.workload_analyzer import WorkloadAnalyzer
from agents.orchestrator import LLMOrchestrator
from utils.formatting import format_insights, format_recommendations

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizationContext:
    """Context for the optimization session."""
    def __init__(self):
        self.config = get_config()
        self.connector = None
        self.orchestrator = None

    def initialize(self):
        """Initialize connection and analyzers."""
        try:
            self.connector = SnowflakeConnector(self.config["snowflake"])

            query_analyzer = QueryAnalyzer(self.connector)
            schema_analyzer = SchemaAnalyzer(self.connector)
            cost_analyzer = CostAnalyzer(self.connector)
            workload_analyzer = WorkloadAnalyzer(self.connector)

            self.orchestrator = LLMOrchestrator(
                self.config["llm"],
                query_analyzer,
                schema_analyzer,
                cost_analyzer,
                workload_analyzer
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    def cleanup(self):
        """Cleanup resources."""
        if self.connector:
            self.connector.close()


@click.group()
@click.pass_context
def cli(ctx):
    """Snowflake Query Optimization Agent.

    Analyze your Snowflake database for performance and cost optimization opportunities.
    """
    ctx.ensure_object(dict)
    ctx.obj['context'] = OptimizationContext()


@cli.command()
@click.pass_context
def analyze(ctx):
    """Run comprehensive optimization analysis."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake. Check your credentials.", err=True)
        return

    try:
        with click.progressbar(
            length=100,
            label='[ANALYZE] Analyzing your Snowflake database'
        ) as bar:
            bar.update(20)
            results = opt_ctx.orchestrator.analyze_comprehensive()
            bar.update(80)

        # Display results
        click.echo("\n" + "="*80)
        click.echo("[REPORT] SNOWFLAKE OPTIMIZATION ANALYSIS REPORT")
        click.echo("="*80 + "\n")

        summary = results["summary"]
        click.echo(f"[INFO] Issues Found: {summary['total_issues_found']}")
        click.echo(f"[CRITICAL] Critical Issues: {summary['critical_issues']}")
        click.echo(f"[SAVINGS] Potential Weekly Savings: {summary['potential_weekly_savings']}")
        click.echo(f"[SAVINGS] Potential Annual Savings: {summary['potential_annual_savings']}")
        click.echo("\n" + "="*80)

        click.echo("\n[BOT] AI RECOMMENDATIONS:\n")
        click.echo(summary['recommendations_summary'])

        click.echo("\n" + "="*80)
        click.echo("[OK] Full analysis complete. Use 'query-insights', 'cost-report', or 'chat' commands for details.\n")

    except Exception as e:
        click.echo(f"[ERROR] Analysis failed: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
@click.pass_context
def query_insights(ctx):
    """Analyze query performance issues."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake.", err=True)
        return

    try:
        click.echo("\n[REPORT] QUERY PERFORMANCE ANALYSIS\n")

        # Slow queries
        click.echo("[SLOW] SLOW QUERIES:")
        slow = opt_ctx.orchestrator.query_analyzer.analyze_slow_queries()
        for insight in slow[:5]:
            click.echo(f"\n  Query ID: {insight.query_id}")
            click.echo(f"  Issue: {insight.description}")
            click.echo(f"  Impact: {insight.impact}")
            click.echo(f"  Recommendation: {insight.recommendation}")

        # Expensive queries
        click.echo("\n\n[COST] EXPENSIVE QUERIES:")
        expensive = opt_ctx.orchestrator.query_analyzer.analyze_expensive_queries()
        for insight in expensive[:5]:
            click.echo(f"\n  Query ID: {insight.query_id}")
            click.echo(f"  Cost: {insight.description}")
            click.echo(f"  Recommendation: {insight.recommendation}")

    except Exception as e:
        click.echo(f"[ERROR] Failed to analyze queries: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
@click.pass_context
def schema_check(ctx):
    """Analyze schema design and structure."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake.", err=True)
        return

    try:
        click.echo("\n[SCHEMA] SCHEMA ANALYSIS\n")

        # Table structures
        click.echo("[BUILD] TABLE OPTIMIZATION OPPORTUNITIES:")
        tables = opt_ctx.orchestrator.schema_analyzer.analyze_table_structures()
        for rec in tables[:5]:
            click.echo(f"\n  Table: {rec.table_name}")
            click.echo(f"  Issue: {rec.description}")
            click.echo(f"  Recommendation: {rec.recommendation}")

        # Clustering
        click.echo("\n\n[CLUSTERING] CLUSTERING KEY RECOMMENDATIONS:")
        clustering = opt_ctx.orchestrator.schema_analyzer.analyze_clustering_efficiency()
        for rec in clustering[:5]:
            click.echo(f"\n  Table: {rec.table_name}")
            click.echo(f"  Recommendation: {rec.recommendation}")

    except Exception as e:
        click.echo(f"[ERROR] Failed to analyze schema: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
@click.pass_context
def cost_report(ctx):
    """Generate cost optimization report."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake.", err=True)
        return

    try:
        click.echo("\n[SAVINGS] COST OPTIMIZATION REPORT\n")

        report = opt_ctx.orchestrator.cost_analyzer.generate_cost_report()

        click.echo(f"[REPORT] Total Potential Savings: ${report['total_potential_savings']:.2f} per week")
        click.echo(f"[REPORT] Annual Potential Savings: ${report['total_potential_savings_annual']:.2f}")
        click.echo(f"[CRITICAL] Critical Optimizations: {report['critical_count']}")
        click.echo(f"[WARNING] High Priority Optimizations: {report['high_count']}\n")

        click.echo("[IDEA] TOP COST OPTIMIZATION OPPORTUNITIES:\n")
        for opt in report['optimizations'][:5]:
            click.echo(f"  Category: {opt.category}")
            click.echo(f"  Issue: {opt.issue}")
            click.echo(f"  Potential Savings: ${opt.potential_savings:.2f}")
            click.echo(f"  Action Items:")
            for item in opt.action_items:
                click.echo(f"    {item}")
            click.echo()

    except Exception as e:
        click.echo(f"[ERROR] Failed to generate cost report: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
@click.pass_context
def workload_analysis(ctx):
    """Analyze workload patterns."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake.", err=True)
        return

    try:
        click.echo("\n[TRENDS] WORKLOAD PATTERN ANALYSIS\n")

        summary = opt_ctx.orchestrator.workload_analyzer.generate_workload_summary()

        click.echo(f"[REPORT] Total Patterns Identified: {summary['total_patterns']}")
        click.echo(f"[HIGH] High Impact Patterns: {summary['high_impact_count']}")
        click.echo(f"[MEDIUM] Medium Impact Patterns: {summary['medium_impact_count']}\n")

        click.echo("[ANALYZE] WORKLOAD INSIGHTS:\n")
        for pattern in summary['patterns'][:5]:
            click.echo(f"  Type: {pattern.pattern_type}")
            click.echo(f"  Description: {pattern.description}")
            click.echo(f"  Recommendation: {pattern.recommendation}")
            click.echo()

    except Exception as e:
        click.echo(f"[ERROR] Failed to analyze workloads: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
@click.pass_context
def chat(ctx):
    """Interactive chat with AI about Snowflake optimization (runs analysis first)."""
    opt_ctx = ctx.obj['context']

    if not opt_ctx.initialize():
        click.echo("[ERROR] Failed to connect to Snowflake.", err=True)
        return

    try:
        # Run analysis first to provide context
        click.echo("\n[BOT] 🤖 SNOWFLAKE OPTIMIZATION CHATBOT")
        click.echo("[BOT] Running initial database analysis for context...\n")

        with click.progressbar(length=100, label='[ANALYZE]') as bar:
            analysis_results = opt_ctx.orchestrator.analyze_comprehensive()
            bar.update(100)

        # Store analysis in orchestrator for chat context
        opt_ctx.orchestrator.last_analysis = analysis_results

        click.echo("[BOT] ✅ Analysis complete! Ask me specific questions about your database.\n")
        click.echo("[BOT] Examples:")
        click.echo("  - 'What are my top 3 optimization priorities?'")
        click.echo("  - 'Show me SQL to optimize slow queries'")
        click.echo("  - 'How much can I save per month?'")
        click.echo("  - 'Which tables need clustering keys?'")
        click.echo("\nType 'exit' to quit.\n")

        while True:
            user_input = click.prompt("You")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                click.echo("[BOT] Goodbye! Remember to implement those optimizations! 🚀")
                break

            response = opt_ctx.orchestrator.interactive_chat(user_input)
            click.echo(f"\nAssistant: {response}\n")

    except KeyboardInterrupt:
        click.echo("\n\n[BOT] Session interrupted. Goodbye!")
    except Exception as e:
        click.echo(f"[ERROR] Chat error: {e}", err=True)
    finally:
        opt_ctx.cleanup()


@cli.command()
def health_check():
    """Check Snowflake connection health."""
    config = get_config()
    try:
        connector = SnowflakeConnector(config["snowflake"])
        connector.close()
        click.echo("[OK] Snowflake connection healthy!")
    except Exception as e:
        click.echo(f"[ERROR] Connection failed: {e}", err=True)


if __name__ == "__main__":
    cli(obj={})
