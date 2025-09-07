"""
Centralized logging configuration with structured JSON logs.
Provides request ID injection and different log levels.
"""

import logging
import json
import sys
import time
import uuid
from typing import Dict, Any, Optional
from contextvars import ContextVar
from datetime import datetime
import traceback

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add trace ID if available
        if hasattr(record, 'trace_id'):
            log_entry["trace_id"] = record.trace_id
        
        # Add custom fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'session_id'):
            log_entry["session_id"] = record.session_id
        
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        if hasattr(record, 'step'):
            log_entry["step"] = record.step
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage',
                'exc_info', 'exc_text', 'stack_info'
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request ID to log record."""
        record.request_id = request_id_var.get()
        return True


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    enable_console: bool = True,
    enable_file: bool = False,
    log_file: str = "app.log"
) -> None:
    """
    Setup application logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)
        enable_console: Enable console logging
        enable_file: Enable file logging
        log_file: Log file path
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create formatter
    if log_format.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(console_handler)
    
    # File handler
    if enable_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


def set_request_id(request_id: str) -> None:
    """Set the current request ID in context."""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_var.get()


def generate_request_id() -> str:
    """Generate a new request ID."""
    return str(uuid.uuid4())


class LogContext:
    """Context manager for logging with request ID."""
    
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or generate_request_id()
        self.old_request_id: Optional[str] = None
    
    def __enter__(self):
        self.old_request_id = get_request_id()
        set_request_id(self.request_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_request_id:
            set_request_id(self.old_request_id)
        else:
            request_id_var.set(None)


def log_function_call(func_name: str, **kwargs) -> None:
    """Log a function call with parameters."""
    logger = get_logger("function_calls")
    logger.info(f"Calling {func_name}", extra={
        "function": func_name,
        "parameters": kwargs
    })


def log_performance(step: str, duration_ms: float, **extra) -> None:
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(f"Performance: {step}", extra={
        "step": step,
        "duration_ms": duration_ms,
        **extra
    })


def log_error(error: Exception, context: str = "", **extra) -> None:
    """Log an error with context."""
    logger = get_logger("errors")
    logger.error(f"Error in {context}: {str(error)}", extra={
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        **extra
    }, exc_info=True)


# Initialize logging on import
if __name__ == "__main__":
    setup_logging(log_level="DEBUG", log_format="json")
    logger = get_logger(__name__)
    
    # Test logging
    with LogContext("test-request-123"):
        logger.info("Test log message", extra={"test": True})
        log_performance("test_step", 150.5, rows=1000)
        log_error(ValueError("Test error"), "test_context", user_id="test_user")
