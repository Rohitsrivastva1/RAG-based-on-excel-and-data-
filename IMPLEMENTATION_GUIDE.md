# LlamaIndex + LangChain Implementation Guide

## 🔧 Technical Implementation Details

### **1. LangChain Agent Implementation**

#### **Core Agent Setup**
```python
# backend/agents/llm_agent.py
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType

class LLMAgent:
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent = None
        self.callback_handler = SafeCallbackHandler()
        
    def _initialize_llm(self):
        """Initialize Google Gemini LLM"""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.google_api_key,
            temperature=0.1,
            max_output_tokens=2000
        )
    
    def _create_agent(self):
        """Create pandas agent with safe configuration"""
        dummy_df = pd.DataFrame({'dummy': [1, 2, 3]})
        self.agent = create_pandas_dataframe_agent(
            llm=self.llm,
            df=dummy_df,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            allow_dangerous_code=True  # Required for pandas operations
        )
```

#### **Query Processing Pipeline**
```python
def process_with_agent(self, df: pd.DataFrame, question: str, context: str = ""):
    """Process query with enhanced context and safety"""
    
    # 1. Create agent with actual data
    agent = create_pandas_dataframe_agent(
        llm=self.llm,
        df=df,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        max_iterations=3,
        allow_dangerous_code=True
    )
    
    # 2. Enhance question with data context
    enhanced_question = self._enhance_question(question, context, df)
    
    # 3. Execute with callback handler
    result = agent.run(enhanced_question, callbacks=[self.callback_handler])
    
    # 4. Generate visualization
    visualization = self._determine_visualization(question, result, df)
    
    return {
        'answer': str(result),
        'query_type': QueryType.LLM_AGENT.value,
        'visualization': visualization,
        'success': True
    }
```

### **2. LlamaIndex Vector Store Implementation**

#### **Document Indexing**
```python
# backend/managers/embedding_manager.py
from llama_index.core import Document as LlamaDocument, VectorStoreIndex
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class EmbeddingManager:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.index = None
    
    def build_index(self, df: pd.DataFrame, session_id: str):
        """Build vector index from DataFrame"""
        
        # 1. Convert DataFrame to documents
        documents = self._dataframe_to_documents(df, session_id)
        
        # 2. Create vector store
        self.vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(384))
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # 3. Build index
        self.index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            embed_model=self.embedding_model
        )
        
        return self.index
    
    def _dataframe_to_documents(self, df: pd.DataFrame, session_id: str):
        """Convert DataFrame to LlamaIndex documents"""
        documents = []
        
        # Create statistics document
        stats_doc = self._create_statistics_document(df, session_id)
        documents.append(stats_doc)
        
        # Create data chunk documents
        chunk_size = 10
        for i in range(0, len(df), chunk_size):
            chunk_df = df.iloc[i:i+chunk_size]
            chunk_doc = self._create_data_chunk_document(chunk_df, session_id, i)
            documents.append(chunk_doc)
        
        return documents
```

#### **Semantic Search**
```python
def search_similar(self, query: str, top_k: int = 5):
    """Search for similar content using semantic similarity"""
    
    if not self.index:
        return []
    
    # Create query engine
    query_engine = self.index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="no_text"  # Only return source nodes
    )
    
    # Execute search
    response = query_engine.query(query)
    
    # Extract relevant documents
    results = []
    for node in response.source_nodes:
        results.append({
            'text': node.text,
            'metadata': node.metadata,
            'score': node.score
        })
    
    return results
```

### **3. Hybrid Processing Architecture**

#### **Query Processing Flow**
```python
# backend/app.py
async def process_file_question(question: str, session_id: str, df: pd.DataFrame):
    """Main query processing pipeline"""
    
    # 1. Get context from LlamaIndex
    context = ""
    if embedding_manager.embeddings:
        similar_docs = embedding_manager.search_similar(question, top_k=3)
        context = "\n".join([doc['text'] for doc in similar_docs])
    
    # 2. Process with LangChain agent
    llm_agent = get_llm_agent()
    if not llm_agent.is_available():
        raise HTTPException(status_code=503, detail="LLM agent not available")
    
    # 3. Execute agent with context
    agent_result = llm_agent.process_with_agent(df, question, context)
    
    # 4. Return structured response
    return AskResponse(
        question=question,
        answer=agent_result['answer'],
        query_type=agent_result['query_type'],
        data=QueryData(
            summary=DataSummary(
                rows=len(df),
                columns=len(df.columns),
                column_names=df.columns.tolist(),
                data_types={col: str(dtype) for col, dtype in df.dtypes.to_dict().items()}
            ),
            context=context,
            generated_code=agent_result.get('generated_code'),
            visualization=agent_result.get('visualization')
        ),
        session_id=session_id,
        timestamp=datetime.utcnow(),
        duration_ms=agent_result.get('processing_time_ms', 0)
    )
```

### **4. Enhanced Question Processing**

#### **Context Building**
```python
def _enhance_question(self, question: str, context: str, df: pd.DataFrame) -> str:
    """Enhance question with detailed data context"""
    
    enhanced = question
    
    # Add LlamaIndex context
    if context:
        enhanced = f"Context: {context}\n\nQuestion: {question}"
    
    # Add detailed data information
    data_info = f"\n\nData info: {len(df)} rows, {len(df.columns)} columns. "
    data_info += f"Columns: {', '.join(df.columns.tolist())}\n"
    
    # Add sample data
    if len(df) > 0:
        data_info += f"Sample data (first 3 rows):\n{df.head(3).to_string()}\n"
        
        # Add unique values for categorical columns
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].nunique() < 10:
                unique_vals = df[col].unique()[:10]
                data_info += f"Unique values in {col}: {list(unique_vals)}\n"
        
        # Add aggregation examples
        if 'Category' in df.columns:
            category_counts = df['Category'].value_counts()
            data_info += f"\nCategory frequency: {category_counts.to_dict()}\n"
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                example_col = numeric_cols[0]
                category_sum = df.groupby('Category')[example_col].sum()
                data_info += f"Example aggregation ({example_col} by Category): {category_sum.to_dict()}\n"
    
    enhanced += data_info
    
    # Add strict instructions
    instructions = "\n\nIMPORTANT INSTRUCTIONS:\n"
    instructions += "1. Use only the data provided above - do not make up or hallucinate data\n"
    instructions += "2. Use only safe pandas operations\n"
    instructions += "3. Be precise and accurate in your analysis\n"
    instructions += "4. When aggregating data, make sure to include ALL rows\n"
    instructions += "5. For category-based queries, group by category and aggregate properly\n"
    instructions += "6. Always verify your calculations against the provided data\n"
    
    enhanced += instructions
    
    return enhanced
```

### **5. Visualization System**

#### **Smart Visualization Detection**
```python
def _determine_visualization(self, question: str, result: str, df: pd.DataFrame):
    """Improved visualization logic with priority system"""
    
    q = question.lower()
    
    # Check for visualization keywords
    viz_keywords = ['chart', 'graph', 'plot', 'visualize', 'bar', 'line', 'pie']
    if not any(keyword in q for keyword in viz_keywords):
        return None
    
    # Priority 1: Explicit visualization requests
    if "bar" in q or "bar chart" in q or "bar graph" in q:
        return self._create_category_visualization(df, question)
    
    if "line" in q or "trend" in q or "over time" in q:
        return {"type": "line", "data": {}}
    
    if "pie" in q or "pie chart" in q:
        return {"type": "pie", "data": {}}
    
    # Priority 2: Fallback detection
    if "groupby" in str(result).lower() or "sum()" in str(result).lower():
        return self._create_aggregation_visualization(df, question)
    
    # Priority 3: Default table
    return self._create_table_visualization(df)
```

#### **Category Visualization**
```python
def _create_category_visualization(self, df: pd.DataFrame, question: str):
    """Safe category aggregation with deterministic results"""
    
    q = question.lower()
    metric = None
    
    # Extract metric from question
    if "users" in q and "Users" in df.columns:
        metric = "Users"
    elif "revenue" in q and "Revenue" in df.columns:
        metric = "Revenue"
    elif "growth" in q and "Growth_%" in df.columns:
        metric = "Growth_%"
    
    if metric and "Category" in df.columns:
        # Safe aggregation - ensures ALL categories are included
        grouped = df.groupby("Category")[metric].sum().sort_values(ascending=False)
        
        return {
            "type": "bar",
            "data": {
                "x": grouped.index.tolist(),
                "y": grouped.values.tolist(),
                "x_label": "Category",
                "y_label": f"Total {metric}",
                "title": f"{metric} by Category"
            },
            "title": f"{metric} by Category"
        }
    
    return self._create_table_visualization(df)
```

### **6. Error Handling & Safety**

#### **Comprehensive Error Handling**
```python
def process_with_agent(self, df: pd.DataFrame, question: str, context: str = ""):
    """Process with comprehensive error handling"""
    
    try:
        # Agent processing logic...
        result = agent.run(enhanced_question, callbacks=[self.callback_handler])
        
    except Exception as e:
        error_msg = str(e)
        
        # Handle specific error types
        if "quota" in error_msg.lower() or "429" in error_msg:
            raise RuntimeError("Google Gemini API quota exceeded. Please try again later.")
        elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            raise RuntimeError("Invalid Google API key. Please check your GOOGLE_API_KEY.")
        else:
            raise RuntimeError(f"LLM agent processing failed: {e}")
```

#### **Safe Code Execution**
```python
# backend/utils/security.py
from RestrictedPython import compile_restricted, safe_globals

def safe_exec_pandas(code: str, df: pd.DataFrame) -> Any:
    """Safely execute pandas code with restrictions"""
    
    # Compile with restrictions
    compiled_code = compile_restricted(code, '<inline>', 'eval')
    
    if compiled_code is None:
        raise ValueError("Code compilation failed")
    
    # Safe globals (only pandas and numpy)
    safe_globals_dict = {
        'pd': pd,
        'np': np,
        'df': df,
        '__builtins__': {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round
        }
    }
    
    # Execute safely
    result = eval(compiled_code, safe_globals_dict)
    return result
```

### **7. Configuration Management**

#### **Settings with Pydantic**
```python
# backend/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API Keys
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    
    # Embedding Configuration
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    faiss_dim: int = Field(384, env="FAISS_DIM")
    
    # Resource Limits
    max_rows_indexable: int = Field(10000, env="MAX_ROWS_INDEXABLE")
    max_tokens_llm: int = Field(2000, env="MAX_TOKENS_LLM")
    
    # Feature Flags
    enable_llm_agent: bool = Field(True, env="ENABLE_LLM_AGENT")
    enable_embeddings: bool = Field(True, env="ENABLE_EMBEDDINGS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

## 🚀 Usage Examples

### **1. Basic Setup**
```python
# Initialize the system
from backend.agents.llm_agent import LLMAgent
from backend.managers.embedding_manager import EmbeddingManager

# Create agents
llm_agent = LLMAgent()
embedding_manager = EmbeddingManager()

# Process a file
df = pd.read_excel('data.xlsx')
session_id = "user_session_123"

# Build index
index = embedding_manager.build_index(df, session_id)
```

### **2. Query Processing**
```python
# Ask questions
questions = [
    "What are the unique values in Category column?",
    "Show me bar graph related to category and users",
    "What is the average revenue by category?",
    "Which category has the highest growth rate?"
]

for question in questions:
    # Get context from LlamaIndex
    context_docs = embedding_manager.search_similar(question, top_k=3)
    context = "\n".join([doc['text'] for doc in context_docs])
    
    # Process with LangChain
    result = llm_agent.process_with_agent(df, question, context)
    
    print(f"Question: {question}")
    print(f"Answer: {result['answer']}")
    print(f"Visualization: {result.get('visualization', 'None')}")
    print("-" * 50)
```

### **3. Advanced Analysis**
```python
# Complex data analysis
complex_queries = [
    "Find the correlation between users and revenue",
    "Show me the top 3 categories by total revenue",
    "Which categories have revenue above the average?",
    "Create a line chart showing revenue trends over time"
]

for query in complex_queries:
    result = llm_agent.process_with_agent(df, query, context)
    
    if result['visualization']:
        # Handle visualization data
        viz_data = result['visualization']
        print(f"Chart Type: {viz_data['type']}")
        print(f"Data: {viz_data['data']}")
```

## 🔧 Troubleshooting

### **Common Issues**

1. **Agent Not Available**
   ```python
   # Check if agent is properly initialized
   if not llm_agent.is_available():
       print("LLM agent not available. Check API key and dependencies.")
   ```

2. **Quota Exceeded**
   ```python
   # Handle API quota issues
   try:
       result = llm_agent.process_with_agent(df, question, context)
   except RuntimeError as e:
       if "quota" in str(e).lower():
           print("API quota exceeded. Please try again later.")
   ```

3. **Embedding Issues**
   ```python
   # Check embedding model
   if not embedding_manager.embeddings:
       print("Embedding model not available. Check HuggingFace model.")
   ```

### **Performance Optimization**

1. **Batch Processing**
   ```python
   # Process multiple queries efficiently
   def batch_process(queries, df, context):
       results = []
       for query in queries:
           result = llm_agent.process_with_agent(df, query, context)
           results.append(result)
       return results
   ```

2. **Caching**
   ```python
   # Cache frequently used data
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_cached_embeddings(text):
       return embedding_manager.embed_text(text)
   ```

## 📊 Monitoring & Logging

### **Performance Monitoring**
```python
import time
from backend.logging_config import log_performance

def process_with_monitoring(df, question, context):
    start_time = time.time()
    
    try:
        result = llm_agent.process_with_agent(df, question, context)
        
        # Log performance
        duration = (time.time() - start_time) * 1000
        log_performance("query_processing", duration, 
                       question_length=len(question),
                       df_shape=df.shape)
        
        return result
        
    except Exception as e:
        log_error(e, "Query processing failed", 
                 question=question, df_shape=df.shape)
        raise
```

This implementation guide provides the technical details for building a robust RAG Analytics system using LlamaIndex and LangChain. The hybrid architecture ensures maximum flexibility while maintaining reliability and accuracy.
