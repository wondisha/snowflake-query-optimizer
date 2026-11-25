"""Diagnostic script to check actual QUERY_HISTORY structure."""
import os
from dotenv import load_dotenv
import snowflake.connector
import platform as _platform

# Platform fix
_original_libc_ver = _platform.libc_ver
def patched_libc_ver():
    try:
        return _original_libc_ver()
    except (OSError, ValueError):
        return ('libc', '')
_platform.libc_ver = patched_libc_ver

load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    cursor = conn.cursor()

    # Get sample record and show all fields
    print("=" * 80)
    print("SAMPLE QUERY_HISTORY RECORD:")
    print("=" * 80)
    cursor.execute("""
        SELECT *
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        LIMIT 1
    """)

    # Get column names from cursor description
    columns = [desc[0] for desc in cursor.description]
    print(f"Total columns: {len(columns)}\n")
    for i, col in enumerate(columns):
        print(f"{i+1}. {col}")

    # Show a sample record
    result = cursor.fetchone()
    if result:
        print("\n" + "=" * 80)
        print("SAMPLE VALUES:")
        print("=" * 80)
        for col, val in zip(columns, result):
            print(f"{col}: {val}")

    conn.close()
    print("\n[OK] Diagnostic check complete!")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
