"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
import tempfile
import os
import json

# Test data fixtures
@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'] * 4,
        'Revenue': [1000.50, 1500.75, 1200.25, 800.00, 900.30] * 4,
        'Users': [100, 150, 120, 80, 90] * 4,
        'Growth_%': [12.5, 8.3, 15.2, 6.7, 9.1] * 4,
        'Region': ['North', 'South', 'East', 'West'] * 5,
        'Date': pd.date_range('2024-01-01', periods=20, freq='D')
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_dataframe_large():
    """Create a larger sample DataFrame for testing."""
    np.random.seed(42)
    data = {
        'ID': range(1000),
        'Category': np.random.choice(['A', 'B', 'C', 'D', 'E'], 1000),
        'Value1': np.random.normal(100, 20, 1000),
        'Value2': np.random.normal(50, 10, 1000),
        'Value3': np.random.normal(200, 30, 1000),
        'Text': [f'Text_{i}' for i in range(1000)],
        'Date': pd.date_range('2024-01-01', periods=1000, freq='H')
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_excel_file(sample_dataframe):
    """Create a temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        sample_dataframe.to_excel(f.name, index=False)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def sample_csv_file(sample_dataframe):
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        sample_dataframe.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def sample_session_id():
    """Generate a sample session ID."""
    return "test-session-12345"

@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "What is the total revenue by category?"

@pytest.fixture
def sample_questions():
    """Multiple sample questions for testing."""
    return [
        "What columns are in this dataset?",
        "Show me the first 5 rows",
        "What is the total revenue by category?",
        "Create a bar chart showing revenue by category",
        "What is the average growth percentage?",
        "How many users are in each region?",
        "What is the correlation between revenue and users?",
        "Show me the data summary"
    ]

@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "file_name": "test_data.xlsx",
        "file_size": 1024,
        "upload_time": datetime.utcnow().isoformat(),
        "user_id": "test_user",
        "tags": ["test", "sample"]
    }

@pytest.fixture
def sample_schema():
    """Sample database schema for testing."""
    return {
        "tables": {
            "users": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "name", "type": "VARCHAR(100)", "nullable": False, "primary_key": False},
                    {"name": "email", "type": "VARCHAR(255)", "nullable": True, "primary_key": False},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False, "primary_key": False}
                ],
                "indexes": [
                    {"name": "idx_users_email", "columns": ["email"], "unique": True}
                ],
                "foreign_keys": []
            },
            "orders": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "user_id", "type": "INTEGER", "nullable": False, "primary_key": False},
                    {"name": "amount", "type": "DECIMAL(10,2)", "nullable": False, "primary_key": False},
                    {"name": "status", "type": "VARCHAR(20)", "nullable": False, "primary_key": False}
                ],
                "indexes": [
                    {"name": "idx_orders_user_id", "columns": ["user_id"], "unique": False}
                ],
                "foreign_keys": [
                    {"name": "fk_orders_user_id", "columns": ["user_id"], "referenced_table": "users", "referenced_columns": ["id"]}
                ]
            }
        },
        "table_count": 2,
        "database_type": "postgresql"
    }

@pytest.fixture
def sample_visualization_data():
    """Sample visualization data for testing."""
    return {
        "type": "bar",
        "data": {
            "x": ["Education", "Entertainment", "Finance", "Health", "Tech"],
            "y": [1000, 1500, 1200, 800, 900],
            "title": "Revenue by Category"
        },
        "title": "Revenue by Category"
    }

@pytest.fixture
def sample_plotly_config():
    """Sample Plotly configuration for testing."""
    return {
        "data": [
            {
                "x": ["Education", "Entertainment", "Finance", "Health", "Tech"],
                "y": [1000, 1500, 1200, 800, 900],
                "type": "bar",
                "name": "Revenue"
            }
        ],
        "layout": {
            "title": "Revenue by Category",
            "xaxis": {"title": "Category"},
            "yaxis": {"title": "Revenue"},
            "template": "plotly_dark"
        }
    }

@pytest.fixture
def sample_embedding_documents():
    """Sample documents for embedding testing."""
    return [
        "Education category has 1000 revenue and 100 users",
        "Entertainment category has 1500 revenue and 150 users",
        "Finance category has 1200 revenue and 120 users",
        "Health category has 800 revenue and 80 users",
        "Tech category has 900 revenue and 90 users"
    ]

@pytest.fixture
def sample_intent_analysis_result():
    """Sample intent analysis result for testing."""
    return {
        "intent": "aggregate_data",
        "confidence": 0.85,
        "entities": {
            "columns": ["Revenue", "Category"],
            "values": [],
            "operators": [],
            "aggregations": ["sum", "total"]
        },
        "suggested_operations": [
            "df.groupby('Category')['Revenue'].sum()",
            "df['Revenue'].sum()"
        ],
        "chart_type": "bar"
    }

@pytest.fixture
def sample_code_generation_result():
    """Sample code generation result for testing."""
    return {
        "code": "# Calculate total revenue by category\nresult = df.groupby('Category')['Revenue'].sum()",
        "language": "python",
        "explanation": "Groups data by Category and sums Revenue values",
        "confidence": 0.8,
        "requires_execution": True
    }

@pytest.fixture
def sample_llm_response():
    """Sample LLM response for testing."""
    return {
        "answer": "The total revenue by category is: Education: 1000, Entertainment: 1500, Finance: 1200, Health: 800, Tech: 900",
        "query_type": "llm_agent",
        "generated_code": "df.groupby('Category')['Revenue'].sum()",
        "visualization": {
            "type": "bar",
            "data": {
                "x": ["Education", "Entertainment", "Finance", "Health", "Tech"],
                "y": [1000, 1500, 1200, 800, 900],
                "title": "Revenue by Category"
            }
        },
        "confidence": 0.9,
        "processing_time_ms": 1500,
        "success": True
    }

@pytest.fixture
def sample_error_response():
    """Sample error response for testing."""
    return {
        "error": "ValidationError",
        "message": "Invalid input provided",
        "request_id": "req-12345",
        "timestamp": datetime.utcnow().isoformat()
    }

@pytest.fixture
def sample_health_response():
    """Sample health response for testing."""
    return {
        "status": "healthy",
        "message": "RAG Analytics API is running",
        "version": "1.0.0",
        "features": {
            "excel_upload": True,
            "llm_queries": True,
            "embeddings": True,
            "database_connections": True,
            "visualizations": True,
            "ai_processing": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    return {
        "test_mode": True,
        "log_level": "DEBUG",
        "max_file_size_mb": 10,
        "max_rows_indexable": 1000,
        "top_k_retrieval": 5,
        "llm_max_tokens": 2000,
        "enable_embeddings": True,
        "enable_llm": True,
        "enable_database": True,
        "enable_visualization": True
    }

# Mock fixtures for external dependencies
@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    class MockLLM:
        def __call__(self, prompt):
            return "Mock LLM response"
        
        def generate(self, prompt):
            return "Mock LLM response"
    
    return MockLLM()

@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for testing."""
    class MockEmbeddingModel:
        def embed_documents(self, texts):
            return [[0.1] * 384 for _ in texts]
        
        def embed_query(self, text):
            return [0.1] * 384
    
    return MockEmbeddingModel()

@pytest.fixture
def mock_database_engine():
    """Mock database engine for testing."""
    class MockEngine:
        def connect(self):
            return self
        
        def execute(self, query):
            return self
        
        def fetchall(self):
            return [("Education", 1000), ("Entertainment", 1500)]
    
    return MockEngine()

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    # Cleanup any temporary files created during tests
    import glob
    for file in glob.glob("test_*.xlsx") + glob.glob("test_*.csv"):
        try:
            os.unlink(file)
        except:
            pass

# Test utilities
@pytest.fixture
def assert_dataframe_equal():
    """Utility for DataFrame comparison in tests."""
    def _assert_equal(df1, df2, **kwargs):
        pd.testing.assert_frame_equal(df1, df2, **kwargs)
    return _assert_equal

@pytest.fixture
def assert_json_equal():
    """Utility for JSON comparison in tests."""
    def _assert_equal(json1, json2):
        assert json.dumps(json1, sort_keys=True) == json.dumps(json2, sort_keys=True)
    return _assert_equal
