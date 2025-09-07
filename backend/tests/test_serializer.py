"""
Test JSON serialization utilities.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from backend.utils.serializer import clean_for_json


class TestCleanForJson:
    """Test JSON cleaning functionality."""
    
    def test_clean_for_json_basic_types(self):
        """Test cleaning basic Python types."""
        # Test basic types (should remain unchanged)
        assert clean_for_json("string") == "string"
        assert clean_for_json(123) == 123
        assert clean_for_json(123.45) == 123.45
        assert clean_for_json(True) == True
        assert clean_for_json(False) == False
        assert clean_for_json(None) == None
    
    def test_clean_for_json_numpy_integers(self):
        """Test cleaning numpy integers."""
        # Test numpy integers
        assert clean_for_json(np.int64(123)) == 123
        assert clean_for_json(np.int32(456)) == 456
        assert clean_for_json(np.int16(789)) == 789
        assert clean_for_json(np.int8(10)) == 10
        
        # Test numpy unsigned integers
        assert clean_for_json(np.uint64(123)) == 123
        assert clean_for_json(np.uint32(456)) == 456
        assert clean_for_json(np.uint16(789)) == 789
        assert clean_for_json(np.uint8(10)) == 10
    
    def test_clean_for_json_numpy_floats(self):
        """Test cleaning numpy floats."""
        # Test numpy floats
        assert clean_for_json(np.float64(123.45)) == 123.45
        assert clean_for_json(np.float32(67.89)) == 67.89
        
        # Test special float values
        assert clean_for_json(np.inf) == float('inf')
        assert clean_for_json(-np.inf) == float('-inf')
        assert np.isnan(clean_for_json(np.nan))
    
    def test_clean_for_json_numpy_arrays(self):
        """Test cleaning numpy arrays."""
        # Test 1D array
        arr1d = np.array([1, 2, 3, 4, 5])
        result = clean_for_json(arr1d)
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)
        
        # Test 2D array
        arr2d = np.array([[1, 2, 3], [4, 5, 6]])
        result = clean_for_json(arr2d)
        assert result == [[1, 2, 3], [4, 5, 6]]
        assert isinstance(result, list)
        assert isinstance(result[0], list)
        
        # Test array with different types
        arr_mixed = np.array([1, 2.5, 3])
        result = clean_for_json(arr_mixed)
        assert result == [1, 2.5, 3]
    
    def test_clean_for_json_pandas_na_values(self):
        """Test cleaning pandas NA values."""
        # Test pandas NA
        assert clean_for_json(pd.NA) is None
        
        # Test pandas NaT
        assert clean_for_json(pd.NaT) is None
        
        # Test numpy NaN
        assert clean_for_json(np.nan) is None
    
    def test_clean_for_json_dictionaries(self):
        """Test cleaning dictionaries."""
        # Test simple dictionary
        data = {
            "string": "value",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "none": None
        }
        result = clean_for_json(data)
        assert result == data
        
        # Test dictionary with numpy values
        data_numpy = {
            "numpy_int": np.int64(123),
            "numpy_float": np.float64(45.67),
            "numpy_array": np.array([1, 2, 3]),
            "pandas_na": pd.NA
        }
        result = clean_for_json(data_numpy)
        expected = {
            "numpy_int": 123,
            "numpy_float": 45.67,
            "numpy_array": [1, 2, 3],
            "pandas_na": None
        }
        assert result == expected
    
    def test_clean_for_json_lists(self):
        """Test cleaning lists."""
        # Test simple list
        data = [1, 2, 3, "string", True, None]
        result = clean_for_json(data)
        assert result == data
        
        # Test list with numpy values
        data_numpy = [np.int64(1), np.float64(2.5), np.array([3, 4]), pd.NA]
        result = clean_for_json(data_numpy)
        expected = [1, 2.5, [3, 4], None]
        assert result == expected
        
        # Test nested lists
        data_nested = [[1, 2], [3, 4], [np.int64(5), np.float64(6.0)]]
        result = clean_for_json(data_nested)
        expected = [[1, 2], [3, 4], [5, 6.0]]
        assert result == expected
    
    def test_clean_for_json_nested_structures(self):
        """Test cleaning nested structures."""
        data = {
            "level1": {
                "level2": {
                    "numpy_int": np.int64(123),
                    "numpy_array": np.array([1, 2, 3]),
                    "pandas_na": pd.NA
                },
                "list": [np.float64(1.5), np.int32(2), pd.NaT]
            },
            "array": np.array([[1, 2], [3, 4]])
        }
        
        result = clean_for_json(data)
        expected = {
            "level1": {
                "level2": {
                    "numpy_int": 123,
                    "numpy_array": [1, 2, 3],
                    "pandas_na": None
                },
                "list": [1.5, 2, None]
            },
            "array": [[1, 2], [3, 4]]
        }
        assert result == expected
    
    def test_clean_for_json_pandas_dataframe(self):
        """Test cleaning pandas DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [1.5, 2.5, 3.5],
            'C': ['x', 'y', 'z'],
            'D': [True, False, True]
        })
        
        # Convert DataFrame to dict
        df_dict = df.to_dict('records')
        result = clean_for_json(df_dict)
        
        # Should be cleaned but structure preserved
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(row, dict) for row in result)
    
    def test_clean_for_json_pandas_series(self):
        """Test cleaning pandas Series."""
        series = pd.Series([1, 2, 3, np.nan, 5])
        result = clean_for_json(series)
        
        # Should convert to list with NaN as None
        assert result == [1, 2, 3, None, 5]
    
    def test_clean_for_json_datetime_objects(self):
        """Test cleaning datetime objects."""
        # Test Python datetime
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = clean_for_json(dt)
        assert result == dt  # Should remain unchanged
        
        # Test Python date
        d = date(2024, 1, 15)
        result = clean_for_json(d)
        assert result == d  # Should remain unchanged
        
        # Test pandas Timestamp
        ts = pd.Timestamp('2024-01-15 10:30:45')
        result = clean_for_json(ts)
        assert result == ts  # Should remain unchanged
    
    def test_clean_for_json_empty_structures(self):
        """Test cleaning empty structures."""
        # Test empty dict
        assert clean_for_json({}) == {}
        
        # Test empty list
        assert clean_for_json([]) == []
        
        # Test empty numpy array
        empty_arr = np.array([])
        result = clean_for_json(empty_arr)
        assert result == []
    
    def test_clean_for_json_complex_nested(self):
        """Test cleaning complex nested structures."""
        data = {
            "dataframe": pd.DataFrame({
                'A': [np.int64(1), np.int64(2)],
                'B': [np.float64(1.5), pd.NA]
            }).to_dict('records'),
            "arrays": [
                np.array([1, 2, 3]),
                np.array([[1, 2], [3, 4]])
            ],
            "mixed": {
                "numpy_values": [np.int32(1), np.float32(2.5)],
                "pandas_values": [pd.NA, pd.NaT],
                "regular_values": [1, 2.5, "string"]
            }
        }
        
        result = clean_for_json(data)
        
        # Verify structure is preserved
        assert isinstance(result, dict)
        assert "dataframe" in result
        assert "arrays" in result
        assert "mixed" in result
        
        # Verify dataframe is cleaned
        assert isinstance(result["dataframe"], list)
        assert len(result["dataframe"]) == 2
        
        # Verify arrays are cleaned
        assert result["arrays"] == [[1, 2, 3], [[1, 2], [3, 4]]]
        
        # Verify mixed values are cleaned
        assert result["mixed"]["numpy_values"] == [1, 2.5]
        assert result["mixed"]["pandas_values"] == [None, None]
        assert result["mixed"]["regular_values"] == [1, 2.5, "string"]
    
    def test_clean_for_json_large_structures(self):
        """Test cleaning large structures."""
        # Create large numpy array
        large_array = np.random.rand(1000, 100)
        result = clean_for_json(large_array)
        
        assert isinstance(result, list)
        assert len(result) == 1000
        assert len(result[0]) == 100
        
        # Create large nested structure
        large_data = {
            f"key_{i}": np.array([i, i+1, i+2]) for i in range(100)
        }
        result = clean_for_json(large_data)
        
        assert len(result) == 100
        for i in range(100):
            assert result[f"key_{i}"] == [i, i+1, i+2]
    
    def test_clean_for_json_edge_cases(self):
        """Test cleaning edge cases."""
        # Test with None
        assert clean_for_json(None) is None
        
        # Test with empty string
        assert clean_for_json("") == ""
        
        # Test with zero
        assert clean_for_json(0) == 0
        assert clean_for_json(0.0) == 0.0
        
        # Test with very large numbers
        large_int = np.int64(2**63 - 1)
        result = clean_for_json(large_int)
        assert result == 2**63 - 1
        
        # Test with very small numbers
        small_float = np.float64(1e-10)
        result = clean_for_json(small_float)
        assert result == 1e-10
    
    def test_clean_for_json_preserves_original(self):
        """Test that original data is not modified."""
        original_data = {
            "numpy_int": np.int64(123),
            "numpy_float": np.float64(45.67),
            "numpy_array": np.array([1, 2, 3])
        }
        
        # Make a copy for comparison
        original_copy = {
            "numpy_int": np.int64(123),
            "numpy_float": np.float64(45.67),
            "numpy_array": np.array([1, 2, 3])
        }
        
        result = clean_for_json(original_data)
        
        # Original should be unchanged
        assert original_data["numpy_int"] == original_copy["numpy_int"]
        assert original_data["numpy_float"] == original_copy["numpy_float"]
        np.testing.assert_array_equal(original_data["numpy_array"], original_copy["numpy_array"])
        
        # Result should be cleaned
        assert result["numpy_int"] == 123
        assert result["numpy_float"] == 45.67
        assert result["numpy_array"] == [1, 2, 3]
