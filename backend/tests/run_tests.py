#!/usr/bin/env python3
"""
Comprehensive test runner for the RAG Analytics system.
Runs all tests and provides detailed reporting.
"""

import pytest
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_all_tests():
    """Run all tests with comprehensive reporting."""
    print("🧪 Running RAG Analytics Test Suite")
    print("=" * 60)
    
    # Test directories
    test_dirs = [
        "backend/tests/test_settings.py",
        "backend/tests/test_logging_config.py", 
        "backend/tests/test_types.py",
        "backend/tests/test_security.py",
        "backend/tests/test_serializer.py",
        "backend/tests/test_session_store.py",
        "backend/tests/test_embedding_manager.py",
        "backend/tests/test_database_manager.py",
        "backend/tests/test_llm_agent.py",
        "backend/tests/test_ai_processor.py",
        "backend/tests/test_visualization.py",
        "backend/tests/test_app.py"
    ]
    
    # Run tests with detailed output
    pytest_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker handling
        "--disable-warnings",  # Disable warnings for cleaner output
        "--color=yes",  # Colored output
        "--durations=10",  # Show 10 slowest tests
        "--junitxml=test_results.xml",  # JUnit XML output
        "--html=test_report.html",  # HTML report
        "--self-contained-html",  # Self-contained HTML
    ]
    
    # Add test files
    pytest_args.extend(test_dirs)
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    # Generate summary report
    generate_test_summary()
    
    return exit_code

def run_specific_tests(test_pattern):
    """Run specific tests based on pattern."""
    print(f"🧪 Running tests matching: {test_pattern}")
    print("=" * 60)
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        "-k", test_pattern
    ]
    
    exit_code = pytest.main(pytest_args)
    return exit_code

def run_component_tests(component):
    """Run tests for a specific component."""
    component_tests = {
        "settings": "backend/tests/test_settings.py",
        "logging": "backend/tests/test_logging_config.py",
        "types": "backend/tests/test_types.py",
        "security": "backend/tests/test_security.py",
        "serializer": "backend/tests/test_serializer.py",
        "session": "backend/tests/test_session_store.py",
        "embedding": "backend/tests/test_embedding_manager.py",
        "database": "backend/tests/test_database_manager.py",
        "llm": "backend/tests/test_llm_agent.py",
        "ai": "backend/tests/test_ai_processor.py",
        "visualization": "backend/tests/test_visualization.py",
        "app": "backend/tests/test_app.py"
    }
    
    if component not in component_tests:
        print(f"❌ Unknown component: {component}")
        print(f"Available components: {', '.join(component_tests.keys())}")
        return 1
    
    test_file = component_tests[component]
    print(f"🧪 Running {component} tests: {test_file}")
    print("=" * 60)
    
    pytest_args = [
        "-v",
        "--tb=short",
        "--color=yes",
        test_file
    ]
    
    exit_code = pytest.main(pytest_args)
    return exit_code

def generate_test_summary():
    """Generate a test summary report."""
    print("\n📊 Test Summary Report")
    print("=" * 60)
    
    # Check if test results exist
    if os.path.exists("test_results.xml"):
        print("✅ JUnit XML report generated: test_results.xml")
    
    if os.path.exists("test_report.html"):
        print("✅ HTML report generated: test_report.html")
        print("   Open test_report.html in your browser to view detailed results")
    
    # Generate component status
    components = [
        "Settings Configuration",
        "Logging System", 
        "Type Definitions",
        "Security Utilities",
        "JSON Serialization",
        "Session Management",
        "Embedding Manager",
        "Database Manager", 
        "LLM Agent",
        "AI Processor",
        "Visualization Engine",
        "Main Application"
    ]
    
    print("\n📋 Component Test Status:")
    for component in components:
        print(f"   🔄 {component} - Run specific tests to see status")
    
    print(f"\n⏰ Test run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG Analytics Test Runner")
    parser.add_argument("--component", "-c", help="Run tests for specific component")
    parser.add_argument("--pattern", "-k", help="Run tests matching pattern")
    parser.add_argument("--all", "-a", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.component:
        return run_component_tests(args.component)
    elif args.pattern:
        return run_specific_tests(args.pattern)
    elif args.all:
        return run_all_tests()
    else:
        # Default: run all tests
        return run_all_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
