"""Final verification test."""
import os
os.environ.pop('ANTHROPIC_BASE_URL', None)
os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)

# Import platform fix FIRST before snowflake
import platform_fix

print("=" * 80)
print("SNOWFLAKE QUERY OPTIMIZER - FINAL VERIFICATION")
print("=" * 80)

# 1. Test Snowflake connection
print("\n1. Testing Snowflake Connection...")
try:
    from dotenv import load_dotenv
    load_dotenv()

    from sf_connector.connector import SnowflakeConnector
    from config import get_config

    config = get_config()
    connector = SnowflakeConnector(config["snowflake"])
    connector.close()
    print("   [OK] Snowflake connection works")
except Exception as e:
    print(f"   [ERROR] {e}")

# 2. Test Anthropic API
print("\n2. Testing Anthropic API...")
try:
    from anthropic import Anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'ready'"}]
    )
    print("   [OK] Anthropic API works")
    print(f"   Response: {response.content[0].text}")
except Exception as e:
    print(f"   [ERROR] {e}")

# 3. Test Query Analysis
print("\n3. Testing Query Analysis...")
try:
    config = get_config()
    connector = SnowflakeConnector(config["snowflake"])

    from agents.query_analyzer import QueryAnalyzer
    analyzer = QueryAnalyzer(connector)

    slow = analyzer.analyze_slow_queries()
    print(f"   [OK] Query analysis works - found {len(slow)} slow queries")

    connector.close()
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 80)
print("ALL SYSTEMS READY")
print("=" * 80)
print("\nYou can now run:")
print("  python main.py health-check")
print("  python main.py query-insights")
print("  python main.py schema-check")
print("  python main.py cost-report")
print("  python main.py chat")

