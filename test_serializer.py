#!/usr/bin/env python3
"""Test script to verify serializer fixes."""

import sys
import os
sys.path.append('backend')

import pandas as pd
import numpy as np
from datetime import datetime
from backend.utils.serializer import clean_for_json

def test_dtype_conversion():
    """Test NumPy dtype conversion."""
    print("Testing NumPy dtype conversion:")
    
    # Test different dtypes
    dtypes = [
        np.dtype('object'),
        np.dtype('int64'),
        np.dtype('float64'),
        np.dtype('bool'),
        np.dtype('datetime64[ns]')
    ]
    
    for dtype in dtypes:
        try:
            result = clean_for_json(dtype)
            print(f"  {dtype} -> {result} (type: {type(result)})")
        except Exception as e:
            print(f"  {dtype} -> ERROR: {e}")

def test_datetime_conversion():
    """Test datetime conversion."""
    print("\nTesting datetime conversion:")
    
    # Test different datetime types
    datetimes = [
        datetime.now(),
        datetime.utcnow(),
        np.datetime64('2023-01-01'),
        pd.Timestamp('2023-01-01')
    ]
    
    for dt in datetimes:
        try:
            result = clean_for_json(dt)
            print(f"  {dt} -> {result} (type: {type(result)})")
        except Exception as e:
            print(f"  {dt} -> ERROR: {e}")

def test_dataframe_dtypes():
    """Test DataFrame dtype conversion."""
    print("\nTesting DataFrame dtype conversion:")
    
    # Create test DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z'],
        'C': [1.1, 2.2, 3.3],
        'D': [True, False, True],
        'E': pd.date_range('2023-01-01', periods=3)
    })
    
    print(f"Original dtypes: {df.dtypes.to_dict()}")
    
    # Test the conversion used in app.py
    converted_dtypes = {col: str(dtype) for col, dtype in df.dtypes.to_dict().items()}
    print(f"Converted dtypes: {converted_dtypes}")
    
    # Test clean_for_json on each dtype
    for col, dtype in df.dtypes.items():
        try:
            result = clean_for_json(dtype)
            print(f"  {col}: {dtype} -> {result}")
        except Exception as e:
            print(f"  {col}: {dtype} -> ERROR: {e}")

if __name__ == "__main__":
    test_dtype_conversion()
    test_datetime_conversion()
    test_dataframe_dtypes()
    print("\nTest completed!")
