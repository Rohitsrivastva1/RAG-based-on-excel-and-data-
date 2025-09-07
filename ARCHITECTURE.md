# RAG Analytics System Architecture

## Overview

This RAG (Retrieval-Augmented Generation) Analytics system combines **LlamaIndex** and **LangChain** to provide intelligent data analysis capabilities for Excel/CSV files and database queries. The system uses a hybrid architecture that leverages the strengths of both frameworks.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Analytics System                        │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React 18)  │  Backend (FastAPI)  │  Data Sources    │
│  - File Upload        │  - REST API         │  - Excel/CSV     │
│  - Chat Interface     │  - Session Mgmt     │  - Databases     │
│  - Visualizations     │  - Background Tasks │  - Vector Store  │
│  - Sidebar Navigation │  - Logging & Config │  - Redis Cache   │
│  - Dark Theme UI      │  - Error Handling   │  - HuggingFace   │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐    ┌────────▼────────┐
            │   LangChain    │    │   LlamaIndex    │
            │   (Agents)     │    │  (Embeddings)   │
            │   - Google     │    │  - FAISS Store  │
            │     Gemini     │    │  - HuggingFace  │
            │   - Pandas     │    │  - Document     │
            │     Agent      │    │    Indexing     │
            └────────────────┘    └─────────────────┘
```

## 🔧 Core Components

### 1. **LangChain Integration** (`backend/agents/`)

#### **LLM Agent** (`llm_agent.py`)
- **Purpose**: Handles natural language queries and data analysis
- **LLM Provider**: Google Gemini (ChatGoogleGenerativeAI)
- **Key Features**:
  - Pandas DataFrame agent for Excel/CSV analysis
  - Safe code execution with `allow_dangerous_code=True`
  - Enhanced question processing with data context
  - Visualization detection and generation

```python
# LangChain Agent Creation
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize Google Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.google_api_key,
    temperature=0.1,
    max_output_tokens=2000
)

# Create Pandas Agent
agent = create_pandas_dataframe_agent(
    llm=llm,
    df=dataframe,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=3,
    allow_dangerous_code=True
)
```

#### **AI Processor** (`ai_processor.py`)
- **Purpose**: Intent analysis and query understanding
- **Features**:
  - Natural language query classification
  - Intent detection (aggregation, filtering, visualization)
  - Query enhancement and context building

### 2. **LlamaIndex Integration** (`backend/managers/`)

#### **Embedding Manager** (`embedding_manager.py`)
- **Purpose**: Document indexing and semantic search
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embedding Model**: HuggingFace sentence-transformers/all-MiniLM-L6-v2

```python
# LlamaIndex Document Processing
from llama_index.core import Document as LlamaDocument, VectorStoreIndex
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Initialize embeddings
embedding_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector store
vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(384))
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Build index
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

#### **Session Store** (`session_store.py`)
- **Purpose**: Manages user sessions and data persistence
- **Features**:
  - DataFrame storage and retrieval
  - Session-based data management
  - Background indexing support

## 🔄 Data Flow

### 1. **File Upload & Processing**
```
Excel/CSV File → Pandas DataFrame → Session Store → Background Indexing
                                                      ↓
                                              LlamaIndex Vector Store
```

### 2. **Query Processing**
```
User Query → Intent Analysis (LangChain) → Agent Selection → Data Retrieval
                                                              ↓
                                                      LlamaIndex Search
                                                              ↓
                                                      LangChain Agent
                                                              ↓
                                                      Response + Visualization
```

### 3. **Hybrid Processing Pipeline**
```
1. Query Analysis (LangChain AI Processor)
   ├── Intent Detection
   ├── Context Building
   └── Query Enhancement

2. Data Retrieval (LlamaIndex)
   ├── Semantic Search
   ├── Context Extraction
   └── Relevant Data Selection

3. Agent Processing (LangChain)
   ├── Pandas Operations
   ├── Data Analysis
   └── Result Generation

4. Visualization (Custom Logic)
   ├── Chart Detection
   ├── Data Formatting
   └── Plotly JSON Generation
```

## 🛠️ Key Features

### **LangChain Capabilities**
- **Natural Language Processing**: Convert user queries to pandas operations
- **Safe Code Execution**: Execute data analysis code safely
- **Agent Orchestration**: Coordinate between different analysis tools
- **Error Handling**: Robust error management and fallbacks

### **LlamaIndex Capabilities**
- **Document Indexing**: Convert data into searchable vectors
- **Semantic Search**: Find relevant data based on meaning, not just keywords
- **Context Retrieval**: Provide relevant context for better analysis
- **Vector Storage**: Efficient storage and retrieval of embeddings

## 📁 File Structure

```
backend/
├── agents/
│   ├── llm_agent.py          # LangChain Pandas Agent
│   └── ai_processor.py       # LangChain Intent Analysis
├── managers/
│   ├── embedding_manager.py  # LlamaIndex Vector Store
│   ├── session_store.py      # Session Management
│   └── database_manager.py   # Database Connections
├── utils/
│   ├── types.py              # Pydantic Models
│   ├── security.py           # Safe Execution
│   └── serializer.py         # JSON Serialization
├── viz/
│   └── visualization.py      # Plotly Charts
├── tests/
│   ├── conftest.py           # Test Configuration
│   ├── test_*.py             # Test Files
│   └── run_tests.py          # Test Runner
├── cache/
│   ├── huggingface/          # HuggingFace Model Cache
│   └── indices/              # FAISS Index Storage
├── app.py                    # FastAPI Application
├── settings.py               # Configuration Management
├── logging_config.py         # Logging Setup
└── requirements.txt          # Dependencies
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_DIM=384
MAX_ROWS_INDEXABLE=10000
MAX_TOKENS_LLM=2000
```

### **Dependencies**
```python
# Backend Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pandas==2.1.3
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pymysql==1.1.0
openpyxl==3.1.2
xlrd==2.0.1

# AI/ML Dependencies
llama-index==0.9.15
langchain==0.1.0
langchain-community==0.0.20
langchain-google-genai==1.0.6
openai==1.3.7
anthropic==0.7.8
faiss-cpu==1.12.0
sentence-transformers==2.2.2
chromadb==0.4.15

# Visualization
plotly==5.17.0
kaleido==0.2.1

# Database
redis==5.0.1
alembic==1.12.1

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
aiofiles==23.2.1
```

## 🚀 Usage Examples

### **1. Basic Query Processing**
```python
# Upload file and ask questions
response = requests.post('/upload_file', files={'file': open('data.xlsx', 'rb')})
session_id = response.json()['session_id']

# Ask questions
query = "What are the unique values in Category column?"
response = requests.post('/ask_question', data={
    'question': query,
    'session_id': session_id
})
```

### **2. Visualization Requests**
```python
# Bar chart request
query = "Show me bar graph related to category and users"
response = requests.post('/ask_question', data={
    'question': query,
    'session_id': session_id
})

# Response includes visualization data
visualization = response.json()['visualization']
# {
#   "type": "bar",
#   "data": {
#     "x": ["Category1", "Category2", "Category3"],
#     "y": [100, 200, 150],
#     "x_label": "Category",
#     "y_label": "Total Users"
#   }
# }
```

### **3. Advanced Analysis**
```python
# Complex queries
queries = [
    "What is the average revenue by category?",
    "Which category has the highest growth rate?",
    "Show me the correlation between users and revenue",
    "Find categories with revenue above 1000"
]
```

## 🔒 Security Features

### **Safe Code Execution**
- Restricted Python execution environment
- Input validation and sanitization
- SQL injection prevention
- File type validation

### **Resource Limits**
- Maximum file size limits
- Execution timeout controls
- Memory usage monitoring
- API rate limiting

## 📊 Performance Optimizations

### **Caching Strategy**
- Session-based data caching
- Embedding vector caching
- Query result caching

### **Background Processing**
- Asynchronous file indexing
- Non-blocking query processing
- Background data preparation

## 🐛 Error Handling

### **LangChain Errors**
- Agent initialization failures
- LLM API quota exceeded
- Code execution errors
- Parsing errors

### **LlamaIndex Errors**
- Embedding generation failures
- Vector store errors
- Document indexing issues
- Search failures

## 🔄 Integration Benefits

### **Why Both LangChain and LlamaIndex?**

1. **LangChain Strengths**:
   - Excellent agent orchestration
   - Rich ecosystem of tools
   - Natural language to code conversion
   - Flexible prompt engineering

2. **LlamaIndex Strengths**:
   - Superior document indexing
   - Advanced semantic search
   - Efficient vector operations
   - Better context retrieval

3. **Combined Benefits**:
   - LangChain handles the "how" (agent execution)
   - LlamaIndex handles the "what" (data retrieval)
   - Better accuracy and context understanding
   - More robust error handling

## 🚀 Future Enhancements

### **Planned Features**
- Database query agents
- Multi-modal analysis (images, text)
- Real-time data streaming
- Advanced visualization types
- Custom model fine-tuning

### **Scalability Improvements**
- Distributed vector stores
- Multi-tenant architecture
- Load balancing
- Horizontal scaling

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Plotly Documentation](https://plotly.com/python/)

---

**Note**: This system is designed to be production-ready with proper error handling, security measures, and performance optimizations. The hybrid architecture ensures maximum flexibility while maintaining reliability and accuracy.
