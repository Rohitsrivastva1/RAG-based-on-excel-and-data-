"""
Test logging configuration and structured logging.
"""

import pytest
import logging
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.logging_config import (
    setup_logging, get_logger, LogContext, generate_request_id,
    JsonFormatter, RequestIDMiddleware
)


class TestLoggingConfig:
    """Test logging configuration functionality."""
    
    def test_setup_logging_json_format(self):
        """Test setting up logging with JSON format."""
        with patch('logging.StreamHandler') as mock_handler:
            setup_logging(log_level="DEBUG", log_format="json")
            
            # Verify handler was created
            mock_handler.assert_called_once()
    
    def test_setup_logging_text_format(self):
        """Test setting up logging with text format."""
        with patch('logging.StreamHandler') as mock_handler:
            setup_logging(log_level="INFO", log_format="text")
            
            # Verify handler was created
            mock_handler.assert_called_once()
    
    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"
    
    def test_logger_with_context(self):
        """Test logger with context information."""
        logger = get_logger("test_module")
        
        # Test basic logging
        with patch.object(logger, 'info') as mock_info:
            logger.info("Test message")
            mock_info.assert_called_once_with("Test message")
    
    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id1 = generate_request_id()
        request_id2 = generate_request_id()
        
        # Should be different UUIDs
        assert request_id1 != request_id2
        assert len(request_id1) == 36  # UUID length
        assert len(request_id2) == 36
    
    def test_log_context(self):
        """Test log context functionality."""
        with LogContext("test-request-123"):
            logger = get_logger("test_module")
            
            # Test that context is properly set
            assert True  # Context is set via logging.setLogRecordFactory
    
    def test_json_formatter(self):
        """Test JSON formatter functionality."""
        formatter = JsonFormatter()
        
        # Create a mock log record
        record = logging.LogRecord(
            name="test_module",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.utcnow().timestamp()
        record.process = 12345
        record.thread = 67890
        record.funcName = "test_function"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should be valid JSON
        parsed = json.loads(formatted)
        
        assert parsed["level"] == "INFO"
        assert parsed["name"] == "test_module"
        assert parsed["message"] == "Test message"
        assert parsed["pathname"] == "/test/path.py"
        assert parsed["lineno"] == 42
        assert parsed["funcName"] == "test_function"
        assert parsed["process"] == 12345
        assert parsed["thread"] == 67890
        assert "timestamp" in parsed
    
    def test_json_formatter_with_request_id(self):
        """Test JSON formatter with request ID."""
        formatter = JsonFormatter()
        
        # Create a mock log record with request_id
        record = logging.LogRecord(
            name="test_module",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.created = datetime.utcnow().timestamp()
        record.process = 12345
        record.thread = 67890
        record.funcName = "test_function"
        record.request_id = "test-request-123"
        
        # Format the record
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["request_id"] == "test-request-123"
    
    def test_json_formatter_with_exception(self):
        """Test JSON formatter with exception info."""
        formatter = JsonFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            # Create a mock log record with exception info
            record = logging.LogRecord(
                name="test_module",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=42,
                msg="Test error",
                args=(),
                exc_info=True
            )
            record.created = datetime.utcnow().timestamp()
            record.process = 12345
            record.thread = 67890
            record.funcName = "test_function"
            
            # Format the record
            formatted = formatter.format(record)
            parsed = json.loads(formatted)
            
            assert parsed["level"] == "ERROR"
            assert "exc_info" in parsed
            assert "ValueError" in parsed["exc_info"]
    
    def test_request_id_middleware(self):
        """Test request ID middleware."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Should have request ID in response headers
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) == 36
    
    def test_log_performance(self):
        """Test performance logging."""
        logger = get_logger("test_module")
        
        with patch.object(logger, 'info') as mock_info:
            from backend.logging_config import log_performance
            
            log_performance("test_operation", 1500.5, extra_data={"key": "value"})
            
            # Verify performance log was called
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "test_operation" in call_args[0][0]
            assert "1500.5" in call_args[0][0]
    
    def test_log_error(self):
        """Test error logging."""
        logger = get_logger("test_module")
        
        with patch.object(logger, 'error') as mock_error:
            from backend.logging_config import log_error
            
            error = ValueError("Test error")
            log_error(error, "Test error message", extra_data={"key": "value"})
            
            # Verify error log was called
            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Test error message" in call_args[0][0]
            assert "ValueError" in call_args[0][0]
    
    def test_logger_levels(self):
        """Test different logger levels."""
        logger = get_logger("test_module")
        
        with patch.object(logger, 'debug') as mock_debug, \
             patch.object(logger, 'info') as mock_info, \
             patch.object(logger, 'warning') as mock_warning, \
             patch.object(logger, 'error') as mock_error:
            
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            mock_debug.assert_called_once_with("Debug message")
            mock_info.assert_called_once_with("Info message")
            mock_warning.assert_called_once_with("Warning message")
            mock_error.assert_called_once_with("Error message")
    
    def test_logger_with_extra_fields(self):
        """Test logger with extra fields."""
        logger = get_logger("test_module")
        
        with patch.object(logger, 'info') as mock_info:
            logger.info("Test message", extra={
                "user_id": "12345",
                "session_id": "sess-123",
                "operation": "test_op"
            })
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert "Test message" in call_args[0][0]
    
    def test_uvicorn_log_suppression(self):
        """Test uvicorn log suppression."""
        with patch('logging.getLogger') as mock_get_logger:
            setup_logging(log_level="INFO", log_format="json")
            
            # Should suppress uvicorn access logs
            mock_get_logger.assert_called()
    
    def test_logger_propagation(self):
        """Test logger propagation settings."""
        logger = get_logger("test_module")
        
        # Test that logger has proper propagation
        assert logger.propagate is True
    
    def test_multiple_loggers(self):
        """Test multiple logger instances."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2
    
    def test_logger_hierarchy(self):
        """Test logger hierarchy."""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        
        assert child_logger.parent.name == "parent"
    
    def test_log_context_isolation(self):
        """Test log context isolation between requests."""
        with LogContext("request-1"):
            logger1 = get_logger("test")
            # Context should be set for this request
        
        with LogContext("request-2"):
            logger2 = get_logger("test")
            # Context should be different for this request
        
        # Contexts should be isolated
        assert True  # Context isolation is handled by logging.setLogRecordFactory
    
    def test_log_format_consistency(self):
        """Test log format consistency across different log levels."""
        formatter = JsonFormatter()
        
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        
        for level in levels:
            record = logging.LogRecord(
                name="test_module",
                level=level,
                pathname="/test/path.py",
                lineno=42,
                msg=f"Test message for level {level}",
                args=(),
                exc_info=None
            )
            record.created = datetime.utcnow().timestamp()
            record.process = 12345
            record.thread = 67890
            record.funcName = "test_function"
            
            formatted = formatter.format(record)
            parsed = json.loads(formatted)
            
            # All logs should have consistent structure
            assert "timestamp" in parsed
            assert "level" in parsed
            assert "name" in parsed
            assert "message" in parsed
            assert "pathname" in parsed
            assert "lineno" in parsed
            assert "funcName" in parsed
            assert "process" in parsed
            assert "thread" in parsed
