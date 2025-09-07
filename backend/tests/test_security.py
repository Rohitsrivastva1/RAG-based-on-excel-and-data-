"""
Test security utilities and safe execution.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.utils.security import (
    safe_exec_pandas, validate_sql_query, sanitize_input,
    log_security_event, validate_file_size, validate_file_type
)


class TestSafeExecution:
    """Test safe code execution functionality."""
    
    def test_safe_exec_pandas_valid_code(self):
        """Test safe execution with valid pandas code."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        code = """
result = df['A'].sum()
"""
        
        result = safe_exec_pandas(code, df)
        assert result == 15
    
    def test_safe_exec_pandas_groupby(self):
        """Test safe execution with groupby operations."""
        df = pd.DataFrame({
            'Category': ['A', 'B', 'A', 'B', 'A'],
            'Value': [10, 20, 30, 40, 50]
        })
        
        code = """
result = df.groupby('Category')['Value'].sum()
"""
        
        result = safe_exec_pandas(code, df)
        expected = df.groupby('Category')['Value'].sum()
        pd.testing.assert_series_equal(result, expected)
    
    def test_safe_exec_pandas_head_operation(self):
        """Test safe execution with head operation."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        code = """
result = df.head(3)
"""
        
        result = safe_exec_pandas(code, df)
        expected = df.head(3)
        pd.testing.assert_frame_equal(result, expected)
    
    def test_safe_exec_pandas_describe(self):
        """Test safe execution with describe operation."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        code = """
result = df.describe()
"""
        
        result = safe_exec_pandas(code, df)
        expected = df.describe()
        pd.testing.assert_frame_equal(result, expected)
    
    def test_safe_exec_pandas_unsafe_operation(self):
        """Test safe execution blocks unsafe operations."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        # Test file system access
        code = """
import os
result = os.listdir('/')
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)
    
    def test_safe_exec_pandas_import_restriction(self):
        """Test safe execution blocks dangerous imports."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        # Test dangerous import
        code = """
import subprocess
result = subprocess.run(['ls'])
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)
    
    def test_safe_exec_pandas_eval_restriction(self):
        """Test safe execution blocks eval usage."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        code = """
result = eval("1 + 1")
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)
    
    def test_safe_exec_pandas_exec_restriction(self):
        """Test safe execution blocks exec usage."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        code = """
exec("result = 1 + 1")
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)
    
    def test_safe_exec_pandas_no_result_variable(self):
        """Test safe execution when no result variable is assigned."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        code = """
df['A'].sum()
# No result variable assigned
"""
        
        result = safe_exec_pandas(code, df)
        # Should return some indication that code was executed
        assert result is not None
    
    def test_safe_exec_pandas_syntax_error(self):
        """Test safe execution with syntax error."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        code = """
result = df['A'].sum(
# Missing closing parenthesis
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)
    
    def test_safe_exec_pandas_runtime_error(self):
        """Test safe execution with runtime error."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        code = """
result = df['NonExistentColumn'].sum()
"""
        
        with pytest.raises(ValueError, match="Code execution failed"):
            safe_exec_pandas(code, df)


class TestSQLValidation:
    """Test SQL query validation."""
    
    def test_validate_sql_query_select(self):
        """Test validation of SELECT queries."""
        query = "SELECT * FROM users"
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_validate_sql_query_select_with_where(self):
        """Test validation of SELECT queries with WHERE clause."""
        query = "SELECT name, email FROM users WHERE age > 18"
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_validate_sql_query_select_with_join(self):
        """Test validation of SELECT queries with JOIN."""
        query = "SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id"
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_validate_sql_query_aggregation(self):
        """Test validation of aggregation queries."""
        query = "SELECT category, SUM(amount) FROM orders GROUP BY category"
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_validate_sql_query_dangerous_operations(self):
        """Test validation blocks dangerous SQL operations."""
        dangerous_queries = [
            "DROP TABLE users",
            "DELETE FROM users",
            "UPDATE users SET password = 'hacked'",
            "INSERT INTO users VALUES ('hacker', 'hack@evil.com')",
            "TRUNCATE TABLE users",
            "ALTER TABLE users ADD COLUMN hacked BOOLEAN"
        ]
        
        for query in dangerous_queries:
            is_valid, error = validate_sql_query(query)
            assert is_valid is False
            assert "not allowed" in error.lower()
    
    def test_validate_sql_query_empty_query(self):
        """Test validation of empty query."""
        query = ""
        is_valid, error = validate_sql_query(query)
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_sql_query_whitespace_only(self):
        """Test validation of whitespace-only query."""
        query = "   \n\t  "
        is_valid, error = validate_sql_query(query)
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_sql_query_comments(self):
        """Test validation of queries with comments."""
        query = """
        -- This is a comment
        SELECT * FROM users
        /* Another comment */
        WHERE age > 18
        """
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_validate_sql_query_case_insensitive(self):
        """Test validation is case insensitive."""
        query = "select * from users"
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None


class TestInputSanitization:
    """Test input sanitization functionality."""
    
    def test_sanitize_input_normal_text(self):
        """Test sanitization of normal text."""
        input_text = "What is the total revenue?"
        sanitized = sanitize_input(input_text)
        assert sanitized == "What is the total revenue?"
    
    def test_sanitize_input_html_tags(self):
        """Test sanitization removes HTML tags."""
        input_text = "What is the <script>alert('xss')</script> total revenue?"
        sanitized = sanitize_input(input_text)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "What is the" in sanitized
        assert "total revenue?" in sanitized
    
    def test_sanitize_input_sql_injection(self):
        """Test sanitization prevents SQL injection."""
        input_text = "'; DROP TABLE users; --"
        sanitized = sanitize_input(input_text)
        assert "DROP TABLE" not in sanitized
        assert "users" not in sanitized
    
    def test_sanitize_input_whitespace(self):
        """Test sanitization handles whitespace."""
        input_text = "  \n\t  What is the total revenue?  \n\t  "
        sanitized = sanitize_input(input_text)
        assert sanitized == "What is the total revenue?"
    
    def test_sanitize_input_special_characters(self):
        """Test sanitization handles special characters."""
        input_text = "What is the total revenue? @#$%^&*()"
        sanitized = sanitize_input(input_text)
        assert sanitized == "What is the total revenue? @#$%^&*()"
    
    def test_sanitize_input_empty_string(self):
        """Test sanitization of empty string."""
        input_text = ""
        sanitized = sanitize_input(input_text)
        assert sanitized == ""
    
    def test_sanitize_input_none(self):
        """Test sanitization of None input."""
        input_text = None
        sanitized = sanitize_input(input_text)
        assert sanitized is None


class TestFileValidation:
    """Test file validation functionality."""
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        file_size = 5 * 1024 * 1024  # 5MB
        max_size = 10  # 10MB
        is_valid = validate_file_size(file_size, max_size)
        assert is_valid is True
    
    def test_validate_file_size_too_large(self):
        """Test file size validation with too large file."""
        file_size = 15 * 1024 * 1024  # 15MB
        max_size = 10  # 10MB
        is_valid = validate_file_size(file_size, max_size)
        assert is_valid is False
    
    def test_validate_file_size_exact_limit(self):
        """Test file size validation at exact limit."""
        file_size = 10 * 1024 * 1024  # 10MB
        max_size = 10  # 10MB
        is_valid = validate_file_size(file_size, max_size)
        assert is_valid is True
    
    def test_validate_file_type_valid(self):
        """Test file type validation with valid types."""
        valid_types = ['.xlsx', '.xls', '.csv']
        
        for file_type in valid_types:
            is_valid = validate_file_type(f"test{file_type}", valid_types)
            assert is_valid is True
    
    def test_validate_file_type_invalid(self):
        """Test file type validation with invalid type."""
        valid_types = ['.xlsx', '.xls', '.csv']
        is_valid = validate_file_type("test.txt", valid_types)
        assert is_valid is False
    
    def test_validate_file_type_case_insensitive(self):
        """Test file type validation is case insensitive."""
        valid_types = ['.xlsx', '.xls', '.csv']
        is_valid = validate_file_type("test.XLSX", valid_types)
        assert is_valid is True
    
    def test_validate_file_type_no_extension(self):
        """Test file type validation with no extension."""
        valid_types = ['.xlsx', '.xls', '.csv']
        is_valid = validate_file_type("test", valid_types)
        assert is_valid is False


class TestSecurityLogging:
    """Test security event logging."""
    
    @patch('backend.utils.security.logger')
    def test_log_security_event(self, mock_logger):
        """Test security event logging."""
        event_type = "invalid_sql_query"
        details = {"query": "DROP TABLE users", "user_id": "12345"}
        
        log_security_event(event_type, details)
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "invalid_sql_query" in call_args
        assert "DROP TABLE users" in call_args
    
    @patch('backend.utils.security.logger')
    def test_log_security_event_with_session(self, mock_logger):
        """Test security event logging with session info."""
        event_type = "suspicious_activity"
        details = {
            "activity": "multiple_failed_attempts",
            "session_id": "sess-12345",
            "ip_address": "192.168.1.1"
        }
        
        log_security_event(event_type, details)
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "suspicious_activity" in call_args
        assert "sess-12345" in call_args


class TestSecurityEdgeCases:
    """Test security edge cases and boundary conditions."""
    
    def test_safe_exec_pandas_very_long_code(self):
        """Test safe execution with very long code."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        # Create very long code
        long_code = "result = df['A'].sum()\n" * 1000
        
        result = safe_exec_pandas(long_code, df)
        assert result == 6
    
    def test_safe_exec_pandas_nested_operations(self):
        """Test safe execution with nested operations."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        
        code = """
result = df[df['A'] > 2]['B'].mean()
"""
        
        result = safe_exec_pandas(code, df)
        expected = df[df['A'] > 2]['B'].mean()
        assert result == expected
    
    def test_validate_sql_query_nested_select(self):
        """Test validation of nested SELECT queries."""
        query = """
        SELECT * FROM (
            SELECT name, age FROM users WHERE age > 18
        ) AS adults
        WHERE adults.age < 65
        """
        is_valid, error = validate_sql_query(query)
        assert is_valid is True
        assert error is None
    
    def test_sanitize_input_unicode(self):
        """Test sanitization with Unicode characters."""
        input_text = "What is the total revenue? 测试中文 🚀"
        sanitized = sanitize_input(input_text)
        assert sanitized == "What is the total revenue? 测试中文 🚀"
    
    def test_safe_exec_pandas_memory_intensive(self):
        """Test safe execution with memory-intensive operations."""
        df = pd.DataFrame({
            'A': range(1000),
            'B': range(1000, 2000)
        })
        
        code = """
result = df.groupby(df['A'] // 10)['B'].sum()
"""
        
        result = safe_exec_pandas(code, df)
        assert len(result) == 100  # 100 groups
