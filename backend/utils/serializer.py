"""
Safe JSON serialization utilities for converting pandas/numpy objects to JSON primitives.
Handles data type conversions and ensures all data is JSON serializable.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Union, Optional
import logging

logger = logging.getLogger(__name__)


def custom_json_encoder(obj: Any) -> Any:
    """
    Custom JSON encoder for FastAPI's jsonable_encoder.
    Handles numpy dtypes, datetime objects, and other non-serializable types.
    
    Args:
        obj: Object to encode
        
    Returns:
        JSON-serializable object
        
    Raises:
        TypeError: If object cannot be serialized
    """
    # Handle numpy dtypes (e.g. dtype('O'), dtype('int64'))
    if isinstance(obj, np.dtype):
        return str(obj)
    
    # Handle numpy datetime64
    if isinstance(obj, np.datetime64):
        return str(obj)
    
    # Handle numpy integers/floats/bools
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        if np.isnan(obj):
            return None
        if np.isinf(obj):
            return float('inf') if obj > 0 else float('-inf')
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    
    # Handle numpy arrays
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    
    # Handle numpy strings
    if isinstance(obj, np.str_):
        return str(obj)
    
    # Handle Python datetime/date/time
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    
    # Handle timedelta
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    
    # Handle pandas NA/NaT
    if pd.isna(obj):
        return None
    
    # If we can't handle it, raise TypeError
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def clean_for_json(obj: Any) -> Any:
    """
    Recursively clean an object to make it JSON serializable.
    
    Args:
        obj: Object to clean
        
    Returns:
        JSON-serializable object
    """
    if obj is None:
        return None
    
    # Handle pandas objects
    if isinstance(obj, pd.Series):
        return clean_for_json(obj.tolist())
    
    if isinstance(obj, pd.DataFrame):
        return {
            'data': clean_for_json(obj.to_dict('records')),
            'columns': clean_for_json(obj.columns.tolist()),
            'index': clean_for_json(obj.index.tolist()),
            'shape': clean_for_json(obj.shape)
        }
    
    if isinstance(obj, pd.Index):
        return clean_for_json(obj.tolist())
    
    if isinstance(obj, pd.Categorical):
        return clean_for_json(obj.tolist())
    
    # Handle numpy objects
    if isinstance(obj, np.integer):
        return int(obj)
    
    if isinstance(obj, np.floating):
        if np.isnan(obj):
            return None
        if np.isinf(obj):
            return float('inf') if obj > 0 else float('-inf')
        return float(obj)
    
    if isinstance(obj, np.bool_):
        return bool(obj)
    
    if isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    
    if isinstance(obj, np.str_):
        return str(obj)
    
    # Handle numpy dtypes - this is the key fix!
    if isinstance(obj, np.dtype):
        return str(obj)
    
    # Handle numpy datetime64
    if isinstance(obj, np.datetime64):
        return str(obj)
    
    # Handle datetime objects
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    
    # Handle Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    
    # Handle pandas NA/NaT
    try:
        if pd.isna(obj):
            return None
    except (ValueError, TypeError):
        # Handle cases where pd.isna() fails (e.g., with arrays)
        pass
    
    # Handle collections
    if isinstance(obj, dict):
        return {str(k): clean_for_json(v) for k, v in obj.items()}
    
    if isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj]
    
    # Handle pandas arrays/series
    if hasattr(obj, 'tolist'):
        try:
            return clean_for_json(obj.tolist())
        except (ValueError, TypeError):
            pass
    
    if isinstance(obj, set):
        return list(clean_for_json(item) for item in obj)
    
    # Handle basic types
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # Handle complex numbers
    if isinstance(obj, complex):
        return {
            'real': float(obj.real),
            'imag': float(obj.imag),
            'type': 'complex'
        }
    
    # Handle bytes
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            return obj.hex()
    
    # Handle functions and other non-serializable objects
    if callable(obj):
        return f"<function {obj.__name__}>"
    
    # Try to convert to string as last resort
    try:
        return str(obj)
    except Exception as e:
        logger.warning(f"Could not serialize object: {type(obj)} - {e}")
        return f"<unserializable {type(obj).__name__}>"


def serialize_dataframe(df: pd.DataFrame, include_metadata: bool = True) -> Dict[str, Any]:
    """
    Serialize a DataFrame to a JSON-serializable dictionary.
    
    Args:
        df: DataFrame to serialize
        include_metadata: Whether to include metadata
        
    Returns:
        Serialized DataFrame dictionary
    """
    result = {
        'data': clean_for_json(df.to_dict('records')),
        'columns': clean_for_json(df.columns.tolist()),
        'shape': clean_for_json(df.shape)
    }
    
    if include_metadata:
        result['metadata'] = {
            'dtypes': clean_for_json(df.dtypes.to_dict()),
            'index_name': clean_for_json(df.index.name),
            'column_names': clean_for_json(df.columns.tolist()),
            'memory_usage': clean_for_json(df.memory_usage(deep=True).to_dict()),
            'is_empty': df.empty,
            'has_duplicates': df.duplicated().any()
        }
    
    return result


def serialize_series(series: pd.Series, include_metadata: bool = True) -> Dict[str, Any]:
    """
    Serialize a Series to a JSON-serializable dictionary.
    
    Args:
        series: Series to serialize
        include_metadata: Whether to include metadata
        
    Returns:
        Serialized Series dictionary
    """
    result = {
        'data': clean_for_json(series.tolist()),
        'name': clean_for_json(series.name),
        'dtype': clean_for_json(str(series.dtype))
    }
    
    if include_metadata:
        result['metadata'] = {
            'index': clean_for_json(series.index.tolist()),
            'index_name': clean_for_json(series.index.name),
            'is_empty': series.empty,
            'has_duplicates': series.duplicated().any(),
            'memory_usage': clean_for_json(series.memory_usage(deep=True))
        }
    
    return result


def serialize_aggregation_result(result: Any, operation: str) -> Dict[str, Any]:
    """
    Serialize an aggregation result to JSON.
    
    Args:
        result: Aggregation result (Series, DataFrame, or scalar)
        operation: Name of the operation performed
        
    Returns:
        Serialized aggregation result
    """
    if isinstance(result, pd.DataFrame):
        return {
            'type': 'dataframe',
            'operation': operation,
            'data': serialize_dataframe(result)
        }
    elif isinstance(result, pd.Series):
        return {
            'type': 'series',
            'operation': operation,
            'data': serialize_series(result)
        }
    else:
        return {
            'type': 'scalar',
            'operation': operation,
            'value': clean_for_json(result)
        }


def create_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: Exception that occurred
        context: Additional context
        
    Returns:
        Error response dictionary
    """
    return {
        'error': True,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Success response dictionary
    """
    return {
        'success': True,
        'message': message,
        'data': clean_for_json(data),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def validate_json_serializable(obj: Any) -> bool:
    """
    Check if an object is JSON serializable.
    
    Args:
        obj: Object to check
        
    Returns:
        True if serializable, False otherwise
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize an object to JSON string.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    cleaned_obj = clean_for_json(obj)
    return json.dumps(cleaned_obj, **kwargs)


def safe_json_loads(json_str: str, **kwargs) -> Any:
    """
    Safely deserialize a JSON string.
    
    Args:
        json_str: JSON string to deserialize
        **kwargs: Additional arguments for json.loads
        
    Returns:
        Deserialized object
    """
    try:
        return json.loads(json_str, **kwargs)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"JSON deserialization error: {e}")
        raise ValueError(f"Invalid JSON: {e}")


def create_visualization_data(
    chart_type: str,
    data: Dict[str, Any],
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized visualization data structure.
    
    Args:
        chart_type: Type of chart (bar, line, pie, etc.)
        data: Chart data
        title: Chart title
        
    Returns:
        Visualization data dictionary
    """
    return clean_for_json({
        'type': chart_type,
        'data': data,
        'title': title or f"{chart_type.title()} Chart",
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


def create_query_response(
    question: str,
    answer: str,
    query_type: str,
    data: Dict[str, Any],
    visualization: Optional[Dict[str, Any]] = None,
    session_id: str = "",
    duration_ms: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create standardized query response.
    
    Args:
        question: Original question
        answer: Generated answer
        query_type: Type of query executed
        data: Query data
        visualization: Optional visualization data
        session_id: Session ID
        duration_ms: Query duration in milliseconds
        
    Returns:
        Query response dictionary
    """
    response = {
        'question': question,
        'answer': answer,
        'query_type': query_type,
        'data': clean_for_json(data),
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if visualization:
        response['visualization'] = clean_for_json(visualization)
    
    if duration_ms is not None:
        response['duration_ms'] = duration_ms
    
    return response


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    
    # Test data
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10.5, 20.3, 30.1, 40.7, 50.9],
        'C': ['x', 'y', 'z', 'x', 'y'],
        'D': pd.date_range('2023-01-01', periods=5),
        'E': [True, False, True, False, True]
    })
    
    # Test serialization
    print("Testing DataFrame serialization:")
    serialized_df = serialize_dataframe(df)
    print(json.dumps(serialized_df, indent=2))
    
    # Test aggregation
    print("\nTesting aggregation serialization:")
    agg_result = df.groupby('C')['A'].sum()
    serialized_agg = serialize_aggregation_result(agg_result, 'groupby_sum')
    print(json.dumps(serialized_agg, indent=2))
    
    # Test visualization data
    print("\nTesting visualization data:")
    viz_data = create_visualization_data(
        'bar',
        {'x': ['x', 'y', 'z'], 'y': [3, 2, 1]},
        'Test Chart'
    )
    print(json.dumps(viz_data, indent=2))
    
    # Test error response
    print("\nTesting error response:")
    error_resp = create_error_response(ValueError("Test error"), "test context")
    print(json.dumps(error_resp, indent=2))
