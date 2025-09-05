"""
Test data fixtures and utilities for comprehensive testing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import json

class TestDataGenerator:
    """Generate various types of test data for comprehensive testing."""
    
    @staticmethod
    def create_sales_data(rows: int = 100) -> pd.DataFrame:
        """Create realistic sales data for testing."""
        np.random.seed(42)
        
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty', 'Toys', 'Automotive']
        regions = ['North', 'South', 'East', 'West', 'Central']
        products = ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E']
        
        data = {
            'Date': pd.date_range('2024-01-01', periods=rows, freq='D'),
            'Category': np.random.choice(categories, rows),
            'Product': np.random.choice(products, rows),
            'Region': np.random.choice(regions, rows),
            'Sales': np.random.normal(1000, 300, rows).round(2),
            'Quantity': np.random.randint(1, 50, rows),
            'Price': np.random.normal(50, 15, rows).round(2),
            'Discount': np.random.uniform(0, 0.3, rows).round(2),
            'Customer_ID': np.random.randint(1000, 9999, rows),
            'Rating': np.random.uniform(1, 5, rows).round(1)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_financial_data(rows: int = 100) -> pd.DataFrame:
        """Create financial data for testing."""
        np.random.seed(42)
        
        companies = ['Apple', 'Google', 'Microsoft', 'Amazon', 'Tesla', 'Meta', 'Netflix', 'Uber']
        sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial']
        
        data = {
            'Date': pd.date_range('2024-01-01', periods=rows, freq='D'),
            'Company': np.random.choice(companies, rows),
            'Sector': np.random.choice(sectors, rows),
            'Revenue': np.random.normal(1000000, 200000, rows).round(2),
            'Profit': np.random.normal(100000, 50000, rows).round(2),
            'Assets': np.random.normal(5000000, 1000000, rows).round(2),
            'Liabilities': np.random.normal(2000000, 500000, rows).round(2),
            'Market_Cap': np.random.normal(10000000, 2000000, rows).round(2),
            'P/E_Ratio': np.random.uniform(10, 50, rows).round(2),
            'ROE': np.random.uniform(0.05, 0.25, rows).round(3)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_time_series_data(rows: int = 365) -> pd.DataFrame:
        """Create time series data for testing."""
        np.random.seed(42)
        
        dates = pd.date_range('2024-01-01', periods=rows, freq='D')
        
        # Create trend and seasonality
        trend = np.linspace(100, 200, rows)
        seasonal = 10 * np.sin(2 * np.pi * np.arange(rows) / 365)
        noise = np.random.normal(0, 5, rows)
        
        data = {
            'Date': dates,
            'Value': trend + seasonal + noise,
            'Temperature': 20 + 10 * np.sin(2 * np.pi * np.arange(rows) / 365) + np.random.normal(0, 2, rows),
            'Humidity': 50 + 20 * np.sin(2 * np.pi * np.arange(rows) / 365) + np.random.normal(0, 5, rows),
            'Pressure': 1013 + 10 * np.sin(2 * np.pi * np.arange(rows) / 365) + np.random.normal(0, 2, rows),
            'Wind_Speed': np.random.exponential(5, rows).round(1)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_categorical_data(rows: int = 100) -> pd.DataFrame:
        """Create categorical data for testing."""
        np.random.seed(42)
        
        data = {
            'ID': range(1, rows + 1),
            'Gender': np.random.choice(['Male', 'Female', 'Other'], rows),
            'Age_Group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+'], rows),
            'Education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], rows),
            'Income_Level': np.random.choice(['Low', 'Medium', 'High'], rows),
            'Marital_Status': np.random.choice(['Single', 'Married', 'Divorced', 'Widowed'], rows),
            'Employment': np.random.choice(['Full-time', 'Part-time', 'Self-employed', 'Unemployed'], rows),
            'Satisfaction': np.random.randint(1, 6, rows),
            'Score': np.random.uniform(0, 100, rows).round(1)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_mixed_data(rows: int = 100) -> pd.DataFrame:
        """Create mixed data types for comprehensive testing."""
        np.random.seed(42)
        
        data = {
            'ID': range(1, rows + 1),
            'Name': [f'User_{i}' for i in range(1, rows + 1)],
            'Email': [f'user{i}@example.com' for i in range(1, rows + 1)],
            'Age': np.random.randint(18, 80, rows),
            'Salary': np.random.normal(50000, 15000, rows).round(2),
            'Is_Active': np.random.choice([True, False], rows),
            'Created_At': pd.date_range('2020-01-01', periods=rows, freq='D'),
            'Tags': [f'Tag_{i % 10}' for i in range(rows)],
            'Score': np.random.uniform(0, 100, rows).round(2),
            'Category': np.random.choice(['A', 'B', 'C', 'D'], rows)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_problematic_data() -> pd.DataFrame:
        """Create data with common issues for testing edge cases."""
        data = {
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', None, 'David', ''],
            'Age': [25, 30, None, 35, 0],
            'Salary': [50000, None, 60000, 70000, -1000],
            'Email': ['alice@test.com', 'bob@test.com', 'invalid-email', 'david@test.com', None],
            'Date': ['2024-01-01', 'invalid-date', '2024-01-03', None, '2024-01-05'],
            'Score': [85.5, 92.0, None, 78.5, 100.1],
            'Category': ['A', 'B', '', 'C', 'D']
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def create_large_dataset(rows: int = 10000) -> pd.DataFrame:
        """Create large dataset for performance testing."""
        np.random.seed(42)
        
        data = {
            'ID': range(1, rows + 1),
            'Category': np.random.choice(['A', 'B', 'C', 'D', 'E'], rows),
            'Value1': np.random.normal(100, 20, rows),
            'Value2': np.random.normal(50, 10, rows),
            'Value3': np.random.normal(200, 30, rows),
            'Text': [f'Text_{i}' for i in range(rows)],
            'Date': pd.date_range('2024-01-01', periods=rows, freq='H'),
            'Flag': np.random.choice([True, False], rows)
        }
        
        return pd.DataFrame(data)


class TestQueries:
    """Collection of test queries for different scenarios."""
    
    # Basic queries
    BASIC_QUERIES = [
        "What columns are in this dataset?",
        "Show me the first 5 rows",
        "How many rows are there?",
        "What is the data type of each column?",
        "Show me the data summary"
    ]
    
    # Aggregation queries
    AGGREGATION_QUERIES = [
        "What is the total revenue?",
        "What is the average salary?",
        "What is the maximum value?",
        "What is the minimum age?",
        "How many records are in each category?",
        "What is the sum of all values?",
        "What is the mean of the scores?"
    ]
    
    # Grouping queries
    GROUPING_QUERIES = [
        "What is the total revenue by category?",
        "Show me the average salary by department",
        "What is the count of records by region?",
        "Group the data by category and show the sum",
        "What is the maximum value in each group?"
    ]
    
    # Visualization queries
    VISUALIZATION_QUERIES = [
        "Create a bar chart showing revenue by category",
        "Generate a line chart of sales over time",
        "Make a pie chart of the distribution",
        "Create a scatter plot of price vs quantity",
        "Show me a histogram of the scores",
        "Generate a heatmap of the correlation matrix"
    ]
    
    # Filtering queries
    FILTERING_QUERIES = [
        "Show me records where age is greater than 30",
        "Filter data where category is 'A'",
        "Find records with salary above 50000",
        "Show me data from the last month",
        "Filter out null values"
    ]
    
    # Statistical queries
    STATISTICAL_QUERIES = [
        "What is the correlation between price and quantity?",
        "Show me the standard deviation of the scores",
        "What is the median value?",
        "Calculate the variance of the data",
        "What is the range of the values?"
    ]
    
    # Complex queries
    COMPLEX_QUERIES = [
        "What is the top 5 categories by revenue?",
        "Show me the bottom 10% of performers",
        "What is the trend of sales over the last 6 months?",
        "Which category has the highest growth rate?",
        "What is the distribution of scores by age group?"
    ]
    
    # Error-prone queries
    ERROR_QUERIES = [
        "Show me data from table that doesn't exist",
        "Calculate sum of non-numeric column",
        "Group by column that doesn't exist",
        "Filter by invalid condition",
        "Create chart with insufficient data"
    ]


class TestVisualizations:
    """Test visualization configurations."""
    
    @staticmethod
    def get_bar_chart_config():
        """Get bar chart configuration for testing."""
        return {
            "type": "bar",
            "data": {
                "x": ["Category A", "Category B", "Category C"],
                "y": [100, 150, 120],
                "title": "Sample Bar Chart"
            },
            "title": "Sample Bar Chart"
        }
    
    @staticmethod
    def get_line_chart_config():
        """Get line chart configuration for testing."""
        return {
            "type": "line",
            "data": {
                "x": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "y": [100, 120, 110],
                "title": "Sample Line Chart"
            },
            "title": "Sample Line Chart"
        }
    
    @staticmethod
    def get_pie_chart_config():
        """Get pie chart configuration for testing."""
        return {
            "type": "pie",
            "data": {
                "labels": ["A", "B", "C"],
                "values": [30, 40, 30],
                "title": "Sample Pie Chart"
            },
            "title": "Sample Pie Chart"
        }
    
    @staticmethod
    def get_scatter_plot_config():
        """Get scatter plot configuration for testing."""
        return {
            "type": "scatter",
            "data": {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10],
                "title": "Sample Scatter Plot"
            },
            "title": "Sample Scatter Plot"
        }
    
    @staticmethod
    def get_heatmap_config():
        """Get heatmap configuration for testing."""
        return {
            "type": "heatmap",
            "data": {
                "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                "labels": ["A", "B", "C"],
                "title": "Sample Heatmap"
            },
            "title": "Sample Heatmap"
        }


class TestDatabaseSchemas:
    """Test database schemas for different database types."""
    
    @staticmethod
    def get_postgresql_schema():
        """Get PostgreSQL schema for testing."""
        return {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "SERIAL", "nullable": False, "primary_key": True},
                        {"name": "username", "type": "VARCHAR(50)", "nullable": False, "primary_key": False},
                        {"name": "email", "type": "VARCHAR(255)", "nullable": False, "primary_key": False},
                        {"name": "created_at", "type": "TIMESTAMP", "nullable": False, "primary_key": False}
                    ],
                    "indexes": [
                        {"name": "idx_users_email", "columns": ["email"], "unique": True}
                    ],
                    "foreign_keys": []
                }
            },
            "table_count": 1,
            "database_type": "postgresql"
        }
    
    @staticmethod
    def get_mysql_schema():
        """Get MySQL schema for testing."""
        return {
            "tables": {
                "products": {
                    "columns": [
                        {"name": "id", "type": "INT AUTO_INCREMENT", "nullable": False, "primary_key": True},
                        {"name": "name", "type": "VARCHAR(100)", "nullable": False, "primary_key": False},
                        {"name": "price", "type": "DECIMAL(10,2)", "nullable": False, "primary_key": False},
                        {"name": "category_id", "type": "INT", "nullable": True, "primary_key": False}
                    ],
                    "indexes": [
                        {"name": "idx_products_category", "columns": ["category_id"], "unique": False}
                    ],
                    "foreign_keys": [
                        {"name": "fk_products_category", "columns": ["category_id"], "referenced_table": "categories", "referenced_columns": ["id"]}
                    ]
                }
            },
            "table_count": 1,
            "database_type": "mysql"
        }
    
    @staticmethod
    def get_sqlite_schema():
        """Get SQLite schema for testing."""
        return {
            "tables": {
                "orders": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                        {"name": "customer_id", "type": "INTEGER", "nullable": False, "primary_key": False},
                        {"name": "total", "type": "REAL", "nullable": False, "primary_key": False},
                        {"name": "status", "type": "TEXT", "nullable": False, "primary_key": False}
                    ],
                    "indexes": [
                        {"name": "idx_orders_customer", "columns": ["customer_id"], "unique": False}
                    ],
                    "foreign_keys": []
                }
            },
            "table_count": 1,
            "database_type": "sqlite"
        }


class TestAPIPayloads:
    """Test API payloads for different endpoints."""
    
    @staticmethod
    def get_upload_payload():
        """Get upload payload for testing."""
        return {
            "file": "test_file.xlsx",
            "session_id": "test-session-123"
        }
    
    @staticmethod
    def get_question_payload():
        """Get question payload for testing."""
        return {
            "question": "What is the total revenue?",
            "session_id": "test-session-123"
        }
    
    @staticmethod
    def get_database_connection_payload():
        """Get database connection payload for testing."""
        return {
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_password",
            "session_id": "test-session-123"
        }
    
    @staticmethod
    def get_visualization_payload():
        """Get visualization payload for testing."""
        return {
            "chart_type": "bar",
            "config": {
                "data": {
                    "x": ["A", "B", "C"],
                    "y": [100, 150, 120],
                    "title": "Test Chart"
                }
            }
        }


# Export all test data generators
__all__ = [
    'TestDataGenerator',
    'TestQueries', 
    'TestVisualizations',
    'TestDatabaseSchemas',
    'TestAPIPayloads'
]
