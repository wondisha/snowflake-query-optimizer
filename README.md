# ❄️ Snowflake Query Optimization Agent

An intelligent, agentic AI system for comprehensive Snowflake database analysis, query optimization, and cost reduction.

## 🎯 Features

### Core Analysis Capabilities
- **Query Performance Analysis**: Identify slow and expensive queries with actionable optimization recommendations
- **Schema Optimization**: Analyze table structures, clustering keys, and data type efficiency
- **Cost Optimization**: Calculate potential savings and identify cost reduction opportunities
- **Workload Pattern Detection**: Understand usage patterns, peak hours, and resource distribution
- **Anomaly Detection**: Flag unusual query patterns that could indicate issues
- **Query Insights Caching**: Avoid redundant analysis of identical queries
- **Benchmarking**: Track optimization metrics over time

### Agentic Features
- **LLM-Powered Orchestration**: Uses Claude AI to synthesize insights and provide intelligent recommendations
- **Interactive Chat Interface**: Ask questions about optimization strategies
- **Health Checks**: Verify Snowflake connectivity before analysis
- **Detailed Logging**: Track all analysis decisions for debugging and audit

## 📋 Quick Start

### 1. Installation

```bash
cd snowflake_query_optimizer
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and add your Snowflake credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SNOWFLAKE_ACCOUNT=your_account_id
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Run Analysis

#### Full Comprehensive Analysis
```bash
python main.py analyze
```

This performs complete analysis and uses Claude AI to generate prioritized recommendations.

#### Query Performance Analysis
```bash
python main.py query-insights
```

Shows:
- Slow-running queries (>5 seconds)
- Expensive queries (by credit consumption)
- Query anti-patterns (SELECT *, inefficient JOINs, etc.)

#### Schema Analysis
```bash
python main.py schema-check
```

Shows:
- Table optimization opportunities
- Clustering key recommendations
- Data type efficiency issues

#### Cost Optimization Report
```bash
python main.py cost-report
```

Shows:
- Potential weekly/annual savings
- Warehouse efficiency issues
- Storage optimization opportunities
- Per-query cost analysis

#### Workload Pattern Analysis
```bash
python main.py workload-analysis
```

Shows:
- User workload patterns
- Database usage distribution
- Peak usage hours
- Warehouse utilization trends

#### Interactive Chat
```bash
python main.py chat
```

Have an interactive conversation about Snowflake optimization strategies.

#### Health Check
```bash
python main.py health-check
```

Verify Snowflake connection is working.

## 🏗️ Architecture

### Core Components

**Snowflake Connector** (`snowflake/connector.py`)
- Connection pooling and lifecycle management
- Methods to fetch: query history, table metadata, warehouse usage
- Specialized queries for performance and cost analysis

**Analysis Agents**
- `query_analyzer.py`: Performance and anti-pattern detection
- `schema_analyzer.py`: Table structure and clustering recommendations
- `cost_analyzer.py`: Credit usage and storage cost analysis
- `workload_analyzer.py`: Usage pattern and trend analysis

**LLM Orchestrator** (`agents/orchestrator.py`)
- Coordinates all analyzers
- Uses Claude API for intelligent synthesis
- Provides interactive chat capability
- Generates prioritized recommendations

**CLI Interface** (`main.py`)
- Click-based command-line interface
- Multiple analysis modes
- Interactive chat
- Health checks

## 📊 Analysis Details

### Query Performance Analysis
- **Slow Queries**: Execution time > 5 seconds
- **Scan Efficiency**: Rows scanned vs. rows produced ratio
- **Cost Analysis**: Credits consumed per query
- **Pattern Detection**: Common anti-patterns in SQL

**Recommendations Include:**
- WHERE clause optimization
- JOIN condition improvements
- Clustering key suggestions
- Index and partitioning strategies

### Schema Analysis
- **Large Table Detection**: Tables > 1GB
- **Clustering Efficiency**: Tables that would benefit from clustering keys
- **Data Type Optimization**: Oversized VARCHARs and other inefficiencies
- **Storage Optimization**: Data archiving opportunities

### Cost Analysis
- **Warehouse Efficiency**: Idle time and auto-scaling opportunities
- **Query Costs**: Top expensive queries and cost per row
- **Storage Costs**: Size reduction through archiving
- **Projected Savings**: Weekly and annual cost reduction estimates

### Workload Analysis
- **User Patterns**: High-credit users, error rates
- **Database Distribution**: Usage by database
- **Temporal Patterns**: Peak usage hours
- **Warehouse Distribution**: Utilization across warehouses

## 🔧 Configuration Options

Edit `.env` to customize:

| Option | Default | Description |
|--------|---------|-------------|
| `DEBUG` | false | Enable debug logging |
| `LOG_LEVEL` | INFO | Logging verbosity |
| `CACHE_ENABLED` | true | Cache query insights |
| `CACHE_TTL_HOURS` | 24 | Cache expiration (hours) |
| `MAX_ANALYSIS_QUERIES` | 100 | Max queries per analysis |

## 📈 Typical Output

```
================================================================================
📊 SNOWFLAKE OPTIMIZATION ANALYSIS REPORT
================================================================================

📌 Issues Found: 47
🚨 Critical Issues: 3
💰 Potential Weekly Savings: $1,234.50
💰 Potential Annual Savings: $64,194.00

================================================================================

🤖 AI RECOMMENDATIONS:

Based on the comprehensive analysis of your Snowflake database, here are the
top 3 immediate actions:

1. **Add Clustering Key to `events_table`** (Critical Priority)
   - Issue: Table is 50GB with 500M+ rows, no clustering strategy
   - Action: ALTER TABLE events_table CLUSTER BY (event_date, user_id);
   - Impact: 60% faster queries, $200/week savings
   
2. **Optimize Query #q_xyz_12345** (High Priority)
   - Issue: Consumes 150 credits/run, scans 2B rows, produces 1M rows
   - Action: Add WHERE predicates to reduce scan by 90%
   - Impact: $50/week savings, 10x faster execution

3. **Reduce Warehouse Size** (High Priority)
   - Issue: Warehouse has 40% idle time
   - Action: Reduce from XLARGE to MEDIUM with auto-scaling
   - Impact: $100/week savings, same performance
```

## 🛠️ Advanced Usage

### Python API

```python
from config import get_config
from snowflake.connector import SnowflakeConnector
from agents.query_analyzer import QueryAnalyzer
from agents.orchestrator import LLMOrchestrator

config = get_config()
connector = SnowflakeConnector(config["snowflake"])

# Analyze slow queries
analyzer = QueryAnalyzer(connector)
insights = analyzer.analyze_slow_queries()
for insight in insights:
    print(f"{insight.query_id}: {insight.recommendation}")

connector.close()
```

### Extending Analyzers

Add custom analysis by extending base analyzer classes:

```python
class CustomAnalyzer:
    def __init__(self, connector):
        self.connector = connector
    
    def analyze(self):
        # Your custom analysis logic
        pass
```

## 📝 Logging

Logs are saved and printed to console. Enable debug mode in `.env`:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

View detailed logs:
```bash
tail -f snowflake_optimizer.log
```

## 🔐 Security

### Credential Management (IMPORTANT)
- ⚠️ **Never commit** `.env` file to version control
- ✅ `.env` is listed in `.gitignore` and won't be tracked
- ✅ Always use `.env.example` as your template
- ✅ Regenerate credentials if ever exposed

### Best Practices
- Snowflake connections use encrypted authentication
- API keys stored securely in environment variables only
- For production: Use Snowflake key-pair authentication (not password)
- Rotate credentials regularly
- Use separate Snowflake users per environment (dev/staging/prod)

## 🤝 Integration

### Azure Functions Deployment
Deploy as scheduled Azure Function for continuous monitoring:
```bash
func init MyOptimizer --python
cp -r snowflake_query_optimizer MyOptimizer/
# Configure function_app.py with Timer trigger
```

### CI/CD Pipeline
Run analysis in GitHub Actions or Azure Pipelines:
```yaml
- name: Run Snowflake Analysis
  run: |
    pip install -r snowflake_query_optimizer/requirements.txt
    python snowflake_query_optimizer/main.py analyze
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Specific test
python -m pytest tests/test_agents.py::test_query_analyzer
```

## 📊 Examples

### Cost Savings Example
Analysis identified:
- **5 slow queries** consuming 200 credits/day
- **Missing 3 clustering keys** causing 2B row scans
- **Oversized warehouse** running 60% idle

**Recommendation**: Add clustering + optimize queries + resize warehouse
**Potential Savings**: $500/week ($26,000/year)
**Time to Implement**: 4 hours

## 🚀 Roadmap

- [ ] Integration with Snowflake Query Acceleration
- [ ] Machine learning-based anomaly detection
- [ ] Automated query rewriting suggestions
- [ ] Real-time alerts for performance degradation
- [ ] Cost tracking dashboard
- [ ] Integration with Slack/Teams for notifications

## 📞 Support

For issues or questions:
1. Check logs: `DEBUG=true LOG_LEVEL=DEBUG python main.py analyze`
2. Verify credentials: `python main.py health-check`
3. Review Snowflake account permissions (requires ACCOUNTADMIN role for QUERY_HISTORY)

## 📄 License

MIT License - See LICENSE file for details

---

**Start optimizing your Snowflake database today! 🚀**

```bash
python main.py analyze
```
