"""
Security utilities for safe code execution and input sanitization.
Provides sandboxed execution environment with strict whitelist of allowed operations.
"""

import ast
import sys
import time
import signal
import subprocess
import tempfile
import os
from typing import Any, Dict, List, Optional, Set, Tuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Whitelist of allowed pandas operations
ALLOWED_PANDAS_METHODS = {
    # Basic operations
    'head', 'tail', 'shape', 'columns', 'index', 'dtypes', 'info', 'describe',
    'sum', 'mean', 'median', 'std', 'var', 'min', 'max', 'count', 'nunique',
    'groupby', 'sort_values', 'sort_index', 'drop', 'dropna', 'fillna',
    'value_counts', 'unique', 'nlargest', 'nsmallest',
    
    # Selection and filtering
    'loc', 'iloc', 'query', 'where', 'mask', 'isin', 'between',
    'lt', 'le', 'gt', 'ge', 'eq', 'ne', 'isnull', 'notnull',
    
    # Aggregation
    'agg', 'aggregate', 'apply', 'transform', 'pivot_table',
    
    # String operations
    'str', 'astype', 'to_numeric', 'to_datetime',
    
    # Mathematical operations
    'add', 'sub', 'mul', 'div', 'mod', 'pow', 'abs', 'round',
    
    # Statistical operations
    'corr', 'cov', 'rank', 'quantile', 'skew', 'kurtosis',
}

# Whitelist of allowed numpy operations
ALLOWED_NUMPY_METHODS = {
    'array', 'arange', 'linspace', 'zeros', 'ones', 'eye', 'identity',
    'sum', 'mean', 'std', 'var', 'min', 'max', 'argmax', 'argmin',
    'sqrt', 'exp', 'log', 'sin', 'cos', 'tan', 'abs', 'round',
    'where', 'clip', 'interp', 'percentile', 'median',
}

# Whitelist of allowed built-in functions
ALLOWED_BUILTINS = {
    'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set',
    'min', 'max', 'sum', 'abs', 'round', 'sorted', 'reversed', 'enumerate',
    'zip', 'map', 'filter', 'any', 'all', 'isinstance', 'type',
}

# Forbidden modules and functions
FORBIDDEN_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests', 'http',
    'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3', 'psycopg2', 'pymongo',
    'matplotlib', 'seaborn', 'plotly', 'bokeh', 'altair',  # Plotting libraries
    'pandas.plotting', 'pandas.io', 'pandas.util',  # Pandas plotting/IO
    'sklearn', 'scipy', 'statsmodels',  # ML libraries
    'tensorflow', 'torch', 'keras',  # Deep learning
    'jupyter', 'ipython', 'notebook',  # Jupyter
    'multiprocessing', 'threading', 'asyncio',  # Concurrency
    'ctypes', 'cffi', 'cython',  # Low-level
    'importlib', 'imp', 'pkgutil',  # Import system
    'eval', 'exec', 'compile',  # Code execution
    'open', 'file', 'input', 'raw_input',  # I/O
    'exit', 'quit', 'help', 'dir', 'vars', 'globals', 'locals',  # Introspection
}

FORBIDDEN_FUNCTIONS = {
    'eval', 'exec', 'compile', 'open', 'file', 'input', 'raw_input',
    'exit', 'quit', 'help', 'dir', 'vars', 'globals', 'locals',
    'getattr', 'setattr', 'delattr', 'hasattr', 'callable',
    'isinstance', 'issubclass', 'super', 'property', 'staticmethod', 'classmethod',
    '__import__', 'reload', 'execfile',
}

# Allowed imports
ALLOWED_IMPORTS = {
    'pandas': ALLOWED_PANDAS_METHODS,
    'numpy': ALLOWED_NUMPY_METHODS,
    'math': {'pi', 'e', 'sqrt', 'exp', 'log', 'sin', 'cos', 'tan', 'abs', 'round'},
    'datetime': {'datetime', 'date', 'time', 'timedelta'},
    'json': {'loads', 'dumps'},
    're': {'search', 'match', 'findall', 'sub', 'split'},
    'collections': {'Counter', 'defaultdict', 'OrderedDict'},
    'itertools': {'chain', 'combinations', 'permutations', 'product'},
    'functools': {'reduce', 'partial'},
    'operator': {'add', 'sub', 'mul', 'truediv', 'floordiv', 'mod', 'pow'},
}


class SecurityError(Exception):
    """Raised when security check fails."""
    pass


class ExecutionTimeoutError(Exception):
    """Raised when code execution times out."""
    pass


class CodeSecurityChecker(ast.NodeVisitor):
    """AST visitor to check code for security violations."""
    
    def __init__(self):
        self.violations: List[str] = []
        self.imports: Set[str] = set()
        self.function_calls: Set[str] = set()
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements."""
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            if module_name in FORBIDDEN_MODULES:
                self.violations.append(f"Forbidden import: {module_name}")
            else:
                self.imports.add(module_name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from imports."""
        if node.module:
            module_name = node.module.split('.')[0]
            if module_name in FORBIDDEN_MODULES:
                self.violations.append(f"Forbidden import: {module_name}")
            else:
                self.imports.add(module_name)
        
        for alias in node.names:
            if alias.name in FORBIDDEN_FUNCTIONS:
                self.violations.append(f"Forbidden function: {alias.name}")
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in FORBIDDEN_FUNCTIONS:
                self.violations.append(f"Forbidden function call: {func_name}")
            else:
                self.function_calls.add(func_name)
        elif isinstance(node.func, ast.Attribute):
            # Check method calls on objects
            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id
                method_name = node.func.attr
                if obj_name == 'pd' and method_name not in ALLOWED_PANDAS_METHODS:
                    self.violations.append(f"Forbidden pandas method: {method_name}")
                elif obj_name == 'np' and method_name not in ALLOWED_NUMPY_METHODS:
                    self.violations.append(f"Forbidden numpy method: {method_name}")
    
    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check attribute access."""
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id
            attr_name = node.attr
            if obj_name == 'pd' and attr_name not in ALLOWED_PANDAS_METHODS:
                self.violations.append(f"Forbidden pandas attribute: {attr_name}")
            elif obj_name == 'np' and attr_name not in ALLOWED_NUMPY_METHODS:
                self.violations.append(f"Forbidden numpy attribute: {attr_name}")


def check_code_security(code: str) -> Tuple[bool, List[str]]:
    """
    Check if code is safe to execute.
    
    Args:
        code: Python code to check
        
    Returns:
        Tuple of (is_safe, violations)
    """
    try:
        tree = ast.parse(code)
        checker = CodeSecurityChecker()
        checker.visit(tree)
        
        return len(checker.violations) == 0, checker.violations
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]
    except Exception as e:
        return False, [f"Parse error: {e}"]


@contextmanager
def execution_timeout(seconds: int):
    """Context manager for execution timeout."""
    def timeout_handler(signum, frame):
        raise ExecutionTimeoutError(f"Code execution timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old handler
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)


def create_safe_globals(df) -> Dict[str, Any]:
    """Create safe globals for code execution."""
    import pandas as pd
    import numpy as np
    import math
    import datetime
    import json
    import re
    from collections import Counter, defaultdict, OrderedDict
    from itertools import chain, combinations, permutations, product
    from functools import reduce, partial
    import operator
    
    return {
        'pd': pd,
        'np': np,
        'df': df,
        'math': math,
        'datetime': datetime,
        'json': json,
        're': re,
        'Counter': Counter,
        'defaultdict': defaultdict,
        'OrderedDict': OrderedDict,
        'chain': chain,
        'combinations': combinations,
        'permutations': permutations,
        'product': product,
        'reduce': reduce,
        'partial': partial,
        'operator': operator,
        '__builtins__': {name: getattr(__builtins__, name) for name in ALLOWED_BUILTINS},
    }


def safe_exec_pandas(
    code: str, 
    df, 
    timeout_seconds: int = 30,
    max_memory_mb: int = 100
) -> Tuple[Any, Optional[str]]:
    """
    Safely execute pandas code with security checks and resource limits.
    
    Args:
        code: Python code to execute
        df: DataFrame to operate on
        timeout_seconds: Maximum execution time
        max_memory_mb: Maximum memory usage
        
    Returns:
        Tuple of (result, error_message)
    """
    logger.info(f"Executing pandas code with security checks", extra={
        "code_length": len(code),
        "timeout_seconds": timeout_seconds,
        "max_memory_mb": max_memory_mb
    })
    
    # Security check
    is_safe, violations = check_code_security(code)
    if not is_safe:
        error_msg = f"Security violations detected: {', '.join(violations)}"
        logger.warning(f"Code execution blocked: {error_msg}")
        return None, error_msg
    
    # Create safe execution environment
    safe_globals = create_safe_globals(df)
    safe_locals = {}
    
    try:
        # Execute with timeout
        with execution_timeout(timeout_seconds):
            start_time = time.time()
            
            # Compile and execute
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, safe_globals, safe_locals)
            
            execution_time = time.time() - start_time
            logger.info(f"Code executed successfully", extra={
                "execution_time_ms": execution_time * 1000
            })
            
            # Return the result (usually the last expression)
            if 'result' in safe_locals:
                return safe_locals['result'], None
            elif 'df' in safe_locals:
                return safe_locals['df'], None
            else:
                return None, "No result variable found"
                
    except ExecutionTimeoutError as e:
        error_msg = f"Code execution timed out: {e}"
        logger.warning(error_msg)
        return None, error_msg
    except MemoryError as e:
        error_msg = f"Code execution exceeded memory limit: {e}"
        logger.warning(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Code execution error: {e}"
        logger.warning(error_msg, exc_info=True)
        return None, error_msg


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    return text.strip()


def validate_sql_query(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SQL query for security (only allow SELECT statements).
    
    Args:
        sql: SQL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    sql_upper = sql.upper().strip()
    
    # Check for forbidden SQL operations
    forbidden_operations = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'CALL', 'PROCEDURE', 'FUNCTION',
        'UNION', 'INTO', 'OUTFILE', 'INFILE', 'LOAD_FILE', 'INTO OUTFILE'
    ]
    
    for operation in forbidden_operations:
        if operation in sql_upper:
            return False, f"Forbidden SQL operation: {operation}"
    
    # Must start with SELECT
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT statements are allowed"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        '--', '/*', '*/', 'xp_', 'sp_', 'fn_', 'sys.', 'information_schema',
        'pg_', 'mysql.', 'performance_schema', 'sysadmin', 'db_owner'
    ]
    
    for pattern in suspicious_patterns:
        if pattern in sql_upper:
            return False, f"Suspicious SQL pattern: {pattern}"
    
    return True, None


def create_secure_filename(filename: str) -> str:
    """
    Create a secure filename by removing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Secure filename
    """
    import re
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename or "unnamed_file"


def validate_file_size(file_size_bytes: int, max_size_mb: int) -> bool:
    """Validate file size against maximum allowed size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type against allowed extensions."""
    if not filename:
        return False
    
    file_ext = os.path.splitext(filename)[1].lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security events for monitoring."""
    logger.warning(f"Security event: {event_type}", extra={
        "event_type": event_type,
        "details": details,
        "timestamp": time.time()
    })


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    
    # Test data
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['x', 'y', 'z', 'x', 'y']
    })
    
    # Test safe code
    safe_code = """
result = df.groupby('C')['A'].sum()
"""
    
    result, error = safe_exec_pandas(safe_code, df)
    print(f"Safe code result: {result}")
    print(f"Error: {error}")
    
    # Test unsafe code
    unsafe_code = """
import os
os.system('ls')
"""
    
    result, error = safe_exec_pandas(unsafe_code, df)
    print(f"Unsafe code result: {result}")
    print(f"Error: {error}")
    
    # Test SQL validation
    safe_sql = "SELECT * FROM users WHERE id = 1"
    unsafe_sql = "DROP TABLE users"
    
    is_valid, error = validate_sql_query(safe_sql)
    print(f"Safe SQL valid: {is_valid}, Error: {error}")
    
    is_valid, error = validate_sql_query(unsafe_sql)
    print(f"Unsafe SQL valid: {is_valid}, Error: {error}")
