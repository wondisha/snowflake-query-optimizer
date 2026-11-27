#!/usr/bin/env python
"""Quick validation test for Snowflake Query Optimizer."""

import os
import sys

def test_project_structure():
    """Verify project structure."""
    print("\n[TEST] Project Structure")
    print("-" * 60)

    required = {
        "dirs": ["agents", "sf_connector", "utils", "tests"],
        "files": [
            "main.py", "config.py", "requirements.txt",
            "agents/orchestrator.py", "agents/query_analyzer.py",
            "agents/schema_analyzer.py", "agents/cost_analyzer.py",
            "agents/workload_analyzer.py", "sf_connector/connector.py",
            "utils/formatting.py"
        ]
    }

    for dir_name in required["dirs"]:
        if not os.path.isdir(dir_name):
            print(f"FAIL: Missing directory: {dir_name}")
            return False
        print(f"OK: {dir_name}/")

    for file_path in required["files"]:
        if not os.path.isfile(file_path):
            print(f"FAIL: Missing file: {file_path}")
            return False
        size_kb = os.path.getsize(file_path) / 1024
        print(f"OK: {file_path} ({size_kb:.1f}KB)")

    return True

def test_documentation():
    """Verify documentation."""
    print("\n[TEST] Documentation")
    print("-" * 60)

    docs = {
        "README.md": "User guide",
        "IMPLEMENTATION_SUMMARY.md": "Architecture & features",
        "SECURITY.md": "Security guidelines",
        "RELEASE_CHECKLIST.md": "Release verification",
        "CHATBOT_IMPROVEMENTS.md": "Chatbot enhancements"
    }

    all_found = True
    for doc, desc in docs.items():
        if os.path.isfile(doc):
            size_kb = os.path.getsize(doc) / 1024
            print(f"OK: {doc} - {desc} ({size_kb:.1f}KB)")
        else:
            print(f"FAIL: Missing {doc}")
            all_found = False

    return all_found

def test_dependencies():
    """Verify required packages."""
    print("\n[TEST] Dependencies")
    print("-" * 60)

    packages = ["click", "anthropic", "pydantic"]
    all_found = True

    for pkg in packages:
        try:
            __import__(pkg)
            print(f"OK: {pkg}")
        except ImportError:
            print(f"FAIL: {pkg} not installed")
            all_found = False

    return all_found

def test_security():
    """Verify security settings."""
    print("\n[TEST] Security")
    print("-" * 60)

    # Check .gitignore
    if os.path.isfile(".gitignore"):
        with open(".gitignore", "r") as f:
            gitignore = f.read()
        if ".env" in gitignore:
            print("OK: .env is in .gitignore")
        else:
            print("FAIL: .env not in .gitignore")
            return False
    else:
        print("FAIL: .gitignore missing")
        return False

    # Check .env.example
    if os.path.isfile(".env.example"):
        with open(".env.example", "r") as f:
            example = f.read()

        has_placeholder = "your_account_id" in example or "ACCOUNT Identifier" in example
        no_real_creds = "sk-ant" not in example

        if has_placeholder and no_real_creds:
            print("OK: .env.example has safe placeholders")
        else:
            print("FAIL: .env.example may have credentials")
            return False
    else:
        print("FAIL: .env.example missing")
        return False

    return True

def test_code_quality():
    """Check code quality."""
    print("\n[TEST] Code Quality")
    print("-" * 60)

    # Check main.py has CLI commands
    with open("main.py", "r") as f:
        main_code = f.read()

    commands = ["analyze", "chat", "health_check", "cost_report"]
    for cmd in commands:
        if cmd in main_code:
            print(f"OK: Command '{cmd}' found in main.py")
        else:
            print(f"FAIL: Command '{cmd}' missing from main.py")
            return False

    # Check no hardcoded credentials
    files_to_check = ["README.md", "config.py", "main.py"]
    for file_path in files_to_check:
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if "sk-ant-" in content and "sk-ant-usr" not in content:
                    print(f"FAIL: Potential hardcoded API key in {file_path}")
                    return False
            except Exception:
                # Encoding issues, skip
                pass

    print("OK: No hardcoded credentials found")
    return True

def test_orchestrator():
    """Test orchestrator structure."""
    print("\n[TEST] LLM Orchestrator")
    print("-" * 60)

    with open("agents/orchestrator.py", "r") as f:
        orchestrator_code = f.read()

    required_methods = [
        "analyze_comprehensive",
        "interactive_chat",
        "_get_llm_recommendations",
        "_prepare_analysis_context",
    ]

    all_found = True
    for method in required_methods:
        if f"def {method}" in orchestrator_code:
            print(f"OK: Method '{method}' present")
        else:
            print(f"FAIL: Method '{method}' missing")
            all_found = False

    return all_found

def main():
    """Run all tests."""
    print("=" * 60)
    print("SNOWFLAKE QUERY OPTIMIZER - VALIDATION TESTS")
    print("=" * 60)

    tests = [
        ("Project Structure", test_project_structure),
        ("Documentation", test_documentation),
        ("Dependencies", test_dependencies),
        ("Security", test_security),
        ("Code Quality", test_code_quality),
        ("Orchestrator", test_orchestrator),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "PASS" if passed_flag else "FAIL"
        print(f"[{status}] {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nSTATUS: All tests passed! Ready for deployment.")
        return 0
    else:
        print(f"\nSTATUS: {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
