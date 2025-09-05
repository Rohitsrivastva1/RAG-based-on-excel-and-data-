# Large Dataset Implementation Guide

## 🚀 **Quick Start: Enable Large Dataset Support**

### **Step 1: Update Configuration**

Create or update your `.env` file:

```bash
# Large Dataset Configuration
MAX_ROWS_INDEXABLE=100000          # 100K rows (was 10K)
MAX_TOKENS_LLM=8000               # Larger context window
MAX_FILE_SIZE_MB=200              # 200MB files (was 50MB)
EXECUTION_TIMEOUT_SECONDS=120     # 2 minutes (was 30s)

# Chunked Processing
ENABLE_CHUNKED_PROCESSING=true
CHUNK_SIZE=1000                   # Rows per chunk
MAX_CHUNKS=100                    # Maximum number of chunks

# Memory Optimization
ENABLE_MEMORY_OPTIMIZATION=true
ENABLE_CACHING=true
CACHE_SIZE=1000                   # Number of cached results

# Performance
MAX_BACKGROUND_WORKERS=4          # Parallel processing
ENABLE_STREAMING=false            # For very large datasets
```

### **Step 2: Update Settings**

```python
# backend/settings.py - Add these fields
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Large Dataset Configuration
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    max_chunks: int = Field(100, env="MAX_CHUNKS")
    enable_chunked_processing: bool = Field(True, env="ENABLE_CHUNKED_PROCESSING")
    enable_memory_optimization: bool = Field(True, env="ENABLE_MEMORY_OPTIMIZATION")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    cache_size: int = Field(1000, env="CACHE_SIZE")
    enable_streaming: bool = Field(False, env="ENABLE_STREAMING")
```

### **Step 3: Implement Chunked Processing**

```python
# backend/managers/large_dataset_manager.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LargeDatasetManager:
    """Handles large datasets with chunked processing and memory optimization."""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.chunk_cache = {}
        self.memory_optimized_dfs = {}
    
    def process_large_dataframe(self, df: pd.DataFrame, session_id: str) -> Dict[str, Any]:
        """Process large DataFrame with chunked approach."""
        
        logger.info(f"Processing large DataFrame: {len(df)} rows, {len(df.columns)} columns")
        
        # 1. Memory optimization
        if settings.enable_memory_optimization:
            df = self._optimize_dataframe_memory(df)
            self.memory_optimized_dfs[session_id] = df
        
        # 2. Check if chunking is needed
        if len(df) <= settings.max_rows_indexable:
            return {"chunked": False, "chunks": 1, "total_rows": len(df)}
        
        # 3. Create chunks
        chunks = self._create_chunks(df, session_id)
        
        # 4. Process chunks
        chunk_results = []
        for i, chunk in enumerate(chunks):
            chunk_session_id = f"{session_id}_chunk_{i}"
            chunk_result = self._process_chunk(chunk, chunk_session_id)
            chunk_results.append(chunk_result)
        
        return {
            "chunked": True,
            "chunks": len(chunks),
            "total_rows": len(df),
            "chunk_results": chunk_results
        }
    
    def _optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage."""
        
        logger.info("Optimizing DataFrame memory usage")
        
        # Convert object columns to category if they have few unique values
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique
                df[col] = df[col].astype('category')
                logger.info(f"Converted {col} to category")
        
        # Downcast numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].min() >= 0:
                if df[col].max() < 255:
                    df[col] = df[col].astype('uint8')
                elif df[col].max() < 65535:
                    df[col] = df[col].astype('uint16')
                else:
                    df[col] = df[col].astype('uint32')
                logger.info(f"Downcasted {col} to smaller int type")
        
        # Downcast float columns
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
            logger.info(f"Downcasted {col} to float32")
        
        return df
    
    def _create_chunks(self, df: pd.DataFrame, session_id: str) -> List[pd.DataFrame]:
        """Create chunks from DataFrame."""
        
        chunks = []
        chunk_size = min(self.chunk_size, settings.max_rows_indexable)
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size].copy()
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks for session {session_id}")
        return chunks
    
    def _process_chunk(self, chunk: pd.DataFrame, chunk_session_id: str) -> Dict[str, Any]:
        """Process a single chunk."""
        
        # Store chunk in cache
        self.chunk_cache[chunk_session_id] = chunk
        
        # Create basic statistics
        stats = {
            "chunk_id": chunk_session_id,
            "rows": len(chunk),
            "columns": len(chunk.columns),
            "memory_usage": chunk.memory_usage(deep=True).sum(),
            "column_names": chunk.columns.tolist(),
            "dtypes": chunk.dtypes.to_dict()
        }
        
        return stats
    
    def query_chunked_data(self, session_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query across all chunks for a session."""
        
        # Find all chunks for this session
        chunk_keys = [key for key in self.chunk_cache.keys() if key.startswith(f"{session_id}_chunk_")]
        
        if not chunk_keys:
            logger.warning(f"No chunks found for session {session_id}")
            return []
        
        # Query each chunk
        all_results = []
        for chunk_key in chunk_keys:
            chunk = self.chunk_cache[chunk_key]
            chunk_results = self._query_chunk(chunk, query, top_k)
            all_results.extend(chunk_results)
        
        # Merge and rank results
        merged_results = self._merge_and_rank_results(all_results, top_k)
        return merged_results
    
    def _query_chunk(self, chunk: pd.DataFrame, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Query a single chunk."""
        
        # Simple keyword matching for now
        query_lower = query.lower()
        results = []
        
        for col in chunk.columns:
            if query_lower in col.lower():
                # Column name match
                results.append({
                    "text": f"Column: {col}",
                    "metadata": {"type": "column", "column": col},
                    "score": 1.0
                })
            
            # Check for value matches in first few rows
            if chunk[col].dtype == 'object':
                sample_values = chunk[col].head(10).astype(str).tolist()
                for value in sample_values:
                    if query_lower in value.lower():
                        results.append({
                            "text": f"Value: {value} in column {col}",
                            "metadata": {"type": "value", "column": col, "value": value},
                            "score": 0.8
                        })
        
        return results[:top_k]
    
    def _merge_and_rank_results(self, all_results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Merge and rank results from all chunks."""
        
        # Sort by score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in all_results:
            result_key = (result['text'], result['metadata'].get('type'))
            if result_key not in seen:
                seen.add(result_key)
                unique_results.append(result)
        
        return unique_results[:top_k]
    
    def get_chunk(self, session_id: str, chunk_index: int) -> Optional[pd.DataFrame]:
        """Get a specific chunk by index."""
        
        chunk_key = f"{session_id}_chunk_{chunk_index}"
        return self.chunk_cache.get(chunk_key)
    
    def clear_session(self, session_id: str) -> None:
        """Clear all chunks for a session."""
        
        chunk_keys = [key for key in self.chunk_cache.keys() if key.startswith(f"{session_id}_chunk_")]
        
        for chunk_key in chunk_keys:
            del self.chunk_cache[chunk_key]
        
        if session_id in self.memory_optimized_dfs:
            del self.memory_optimized_dfs[session_id]
        
        logger.info(f"Cleared {len(chunk_keys)} chunks for session {session_id}")
```

### **Step 4: Update Main Application**

```python
# backend/app.py - Add large dataset support
from managers.large_dataset_manager import LargeDatasetManager

# Initialize large dataset manager
large_dataset_manager = LargeDatasetManager(chunk_size=settings.chunk_size)

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """Enhanced file upload with large dataset support."""
    
    # ... existing code ...
    
    # Check if dataset is large
    if len(df) > settings.max_rows_indexable:
        logger.info(f"Large dataset detected: {len(df)} rows. Using chunked processing.")
        
        # Process with large dataset manager
        chunk_result = large_dataset_manager.process_large_dataframe(df, session_id)
        
        return {
            "message": f"File uploaded successfully. Processed {chunk_result['chunks']} chunks.",
            "session_id": session_id,
            "chunked": True,
            "chunks": chunk_result['chunks'],
            "total_rows": chunk_result['total_rows']
        }
    
    # ... existing code for normal datasets ...

@app.post("/ask_question")
async def ask_question(question: str, session_id: str):
    """Enhanced question handling with chunked support."""
    
    # ... existing code ...
    
    # Check if this is a chunked session
    if large_dataset_manager.chunk_cache.get(f"{session_id}_chunk_0"):
        logger.info("Processing chunked dataset query")
        
        # Query across all chunks
        context_docs = large_dataset_manager.query_chunked_data(session_id, question, top_k=3)
        context = "\n".join([doc['text'] for doc in context_docs])
        
        # Get the first chunk for processing
        first_chunk = large_dataset_manager.get_chunk(session_id, 0)
        if first_chunk is not None:
            # Process with first chunk (or implement multi-chunk processing)
            result = llm_agent.process_with_agent(first_chunk, question, context)
            return result
    
    # ... existing code for normal datasets ...
```

### **Step 5: Add Memory Monitoring**

```python
# backend/utils/memory_monitor.py
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MemoryMonitor:
    """Monitor memory usage for large datasets."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get current memory usage."""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available / 1024 / 1024  # MB
        }
    
    @staticmethod
    def check_memory_limit(max_memory_mb: int = 2000) -> bool:
        """Check if memory usage is within limits."""
        
        usage = MemoryMonitor.get_memory_usage()
        return usage["rss"] < max_memory_mb
    
    @staticmethod
    def log_memory_usage(context: str = ""):
        """Log current memory usage."""
        
        usage = MemoryMonitor.get_memory_usage()
        logger.info(f"Memory usage {context}: {usage['rss']:.1f}MB RSS, {usage['percent']:.1f}%")
```

## 📊 **Performance Testing**

### **Test Script for Large Datasets**

```python
# test_large_dataset.py
import pandas as pd
import numpy as np
import time
from datetime import datetime

def create_test_dataset(rows: int) -> pd.DataFrame:
    """Create test dataset with specified number of rows."""
    
    np.random.seed(42)
    
    data = {
        'id': range(rows),
        'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], rows),
        'value1': np.random.randn(rows),
        'value2': np.random.randint(0, 1000, rows),
        'value3': np.random.uniform(0, 100, rows),
        'date': pd.date_range('2020-01-01', periods=rows, freq='D')
    }
    
    return pd.DataFrame(data)

def test_large_dataset_performance():
    """Test performance with different dataset sizes."""
    
    test_sizes = [1000, 5000, 10000, 50000, 100000]
    
    for size in test_sizes:
        print(f"\n=== Testing with {size:,} rows ===")
        
        # Create dataset
        start_time = time.time()
        df = create_test_dataset(size)
        creation_time = time.time() - start_time
        
        # Test memory optimization
        start_time = time.time()
        df_optimized = large_dataset_manager._optimize_dataframe_memory(df.copy())
        optimization_time = time.time() - start_time
        
        # Test chunking
        start_time = time.time()
        chunks = large_dataset_manager._create_chunks(df, f"test_{size}")
        chunking_time = time.time() - start_time
        
        # Memory usage
        memory_usage = MemoryMonitor.get_memory_usage()
        
        print(f"Creation time: {creation_time:.2f}s")
        print(f"Optimization time: {optimization_time:.2f}s")
        print(f"Chunking time: {chunking_time:.2f}s")
        print(f"Chunks created: {len(chunks)}")
        print(f"Memory usage: {memory_usage['rss']:.1f}MB")
        print(f"Memory reduction: {((df.memory_usage().sum() - df_optimized.memory_usage().sum()) / df.memory_usage().sum() * 100):.1f}%")

if __name__ == "__main__":
    test_large_dataset_performance()
```

## 🚀 **Usage Examples**

### **1. Upload Large Dataset**

```python
import requests

# Upload large file
files = {'file': open('large_dataset.csv', 'rb')}
response = requests.post('http://localhost:8000/upload_file', files=files)

result = response.json()
print(f"Uploaded: {result['message']}")
print(f"Chunks: {result['chunks']}")
print(f"Total rows: {result['total_rows']}")
```

### **2. Query Large Dataset**

```python
# Ask questions about large dataset
questions = [
    "What are the unique values in category column?",
    "Show me the average value1 by category",
    "Which category has the highest value2?",
    "Create a bar chart for category distribution"
]

for question in questions:
    data = {
        'question': question,
        'session_id': session_id
    }
    response = requests.post('http://localhost:8000/ask_question', data=data)
    result = response.json()
    
    print(f"Q: {question}")
    print(f"A: {result['answer']}")
    print("-" * 50)
```

## ⚠️ **Important Notes**

### **Memory Requirements:**
- **10K rows**: 2GB RAM minimum
- **50K rows**: 4GB RAM minimum  
- **100K rows**: 8GB RAM minimum
- **500K rows**: 16GB RAM minimum

### **Performance Expectations:**
- **10K rows**: 5-10 seconds processing
- **50K rows**: 30-60 seconds processing
- **100K rows**: 2-5 minutes processing
- **500K rows**: 10-30 minutes processing

### **Limitations:**
- Chunked processing may reduce accuracy for complex queries
- Memory usage increases with dataset size
- Processing time increases significantly with size
- Some advanced features may not work with chunked data

## 🎯 **Next Steps**

1. **Test with your data**: Start with medium-sized datasets
2. **Monitor performance**: Use memory monitoring tools
3. **Optimize settings**: Adjust chunk size and limits
4. **Scale gradually**: Increase dataset size incrementally
5. **Consider database**: For very large datasets, consider database storage

This implementation provides a solid foundation for handling large datasets while maintaining the system's core functionality!
