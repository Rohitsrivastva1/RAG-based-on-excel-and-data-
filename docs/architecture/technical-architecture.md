# Technical Architecture

## 🔧 Detailed Technical Components

This document provides in-depth technical details about each component of the RAG Analytics system.

## 🖥️ Frontend Architecture

### React Application Structure
```
src/
├── App.js                    # Main application component
├── App.css                   # Global styles and dark theme
├── components/
│   ├── ChatInterface.js      # Natural language chat interface
│   ├── FileUpload.js         # Data file upload component
│   ├── Visualization.js      # Chart display component
│   ├── SessionManager.js     # Data session management
│   ├── DatabaseConnection.js # Database connection setup
│   └── TypingAnimation.js    # ChatGPT-like typing effect
└── package.json              # Dependencies and scripts
```

### Component Architecture

#### 1. App.js - Main Application
```javascript
// Key Features:
- ConfigProvider with dark theme
- Tab-based navigation
- Session state management
- Global error handling
- Responsive layout
```

**Theme Configuration:**
```javascript
const darkTheme = {
  token: {
    colorPrimary: '#00d4aa',
    colorBgBase: '#1a1a1a',
    colorTextBase: '#ffffff',
    // ... complete dark theme tokens
  }
}
```

#### 2. ChatInterface.js - Natural Language Interface
```javascript
// Key Features:
- Real-time chat with typing animation
- Message history management
- Visualization data storage
- Copy functionality
- Error handling
```

**State Management:**
```javascript
const [messages, setMessages] = useState([]);
const [typingMessage, setTypingMessage] = useState(null);
const [copiedStates, setCopiedStates] = useState({});
```

#### 3. FileUpload.js - Data Ingestion
```javascript
// Key Features:
- Drag & drop file upload
- Progress tracking
- File validation
- Session creation
- Multiple format support (Excel, CSV)
```

#### 4. Visualization.js - Chart Display
```javascript
// Key Features:
- Plotly.js integration
- Dark theme styling
- Export functionality (CSV, PNG, PDF)
- Chart history management
- Interactive features
```

### Styling Architecture

#### CSS Architecture
```css
/* Global Dark Theme */
.dark-theme {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: #ffffff;
}

/* Component-specific styles */
.glass-effect {
  background: rgba(45, 45, 45, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid #404040;
}

/* Animation classes */
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

## ⚙️ Backend Architecture

### FastAPI Application Structure
```
backend/
├── enhanced_backend.py       # Main FastAPI application
├── llm_agent.py             # LLM processing and agent logic
├── embeddings.py            # Vector store and embeddings
├── requirements.txt         # Python dependencies
└── .env.example            # Environment configuration
```

### API Architecture

#### 1. enhanced_backend.py - Main Application
```python
# Key Features:
- FastAPI application setup
- CORS configuration
- Route definitions
- Error handling
- Session management
```

**Route Structure:**
```python
@app.post("/upload_excel")
async def upload_excel(file: UploadFile, session_id: str)

@app.post("/connect_database")
async def connect_database(connection_data: dict)

@app.post("/ask_question")
async def ask_question(question_data: dict)

@app.get("/sessions")
async def get_sessions()

@app.get("/health")
async def health_check()
```

#### 2. llm_agent.py - AI Processing Engine
```python
# Key Features:
- LangChain agent creation
- Query intent analysis
- Visualization generation
- Response processing
- Error handling and fallbacks
```

**Agent Architecture:**
```python
class LLMAgent:
    def __init__(self):
        self.llm = self.initialize_llm()
        self.embedding_manager = EmbeddingManager()
    
    def create_pandas_agent(self, df: pd.DataFrame):
        # Custom agent with pandas tool
        # Prevents matplotlib usage
        # Uses existing DataFrame
```

**Visualization Engine:**
```python
def create_visualization(self, df: pd.DataFrame, chart_type: str, query: str):
    # Smart column selection based on query
    # Clean JSON generation (no binary encoding)
    # Dark theme integration
    # Multiple chart types support
```

#### 3. embeddings.py - Vector Store Management
```python
# Key Features:
- FAISS vector store
- Multiple embedding models
- Index building and management
- Similarity search
```

**Embedding Architecture:**
```python
class EmbeddingManager:
    def __init__(self, model_type="huggingface", dimension=384):
        self.model_type = model_type
        self.dimension = dimension
        self.vector_store = None
    
    def build_index(self, documents: List[str]):
        # Create FAISS index
        # Store embeddings
        # Enable similarity search
```

## 🧠 AI Processing Architecture

### LangChain Integration

#### Agent Creation Process
```python
# 1. Initialize LLM (Google Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)

# 2. Create custom pandas tool
def pandas_tool(query: str) -> str:
    # Execute pandas operations
    # Prevent plotting libraries
    # Return clean results

# 3. Create ReAct agent
agent = create_react_agent(
    llm=llm,
    tools=[pandas_tool],
    prompt=prompt_template
)
```

#### Query Processing Flow
```python
def process_with_agent(self, df: pd.DataFrame, query: str):
    # 1. Enhanced query with DataFrame info
    enhanced_query = f"""
    DataFrame shape: {df.shape}
    Columns: {list(df.columns)}
    Sample data: {df.head()}
    Question: {query}
    """
    
    # 2. Agent execution
    response = agent.invoke({"input": enhanced_query})
    
    # 3. Response processing
    answer = self.extract_clean_answer(response)
    
    # 4. Visualization suggestion
    visualization = self.suggest_visualization(df, query)
    
    return {
        "answer": answer,
        "visualization": visualization,
        "query_type": "llm_agent"
    }
```

### LlamaIndex Integration

#### Document Processing
```python
# 1. Create documents from DataFrame
documents = []
for index, row in df.iterrows():
    doc_text = f"Row {index}: {row.to_dict()}"
    documents.append(Document(text=doc_text))

# 2. Build vector index
index = VectorStoreIndex.from_documents(documents)

# 3. Create query engine
query_engine = index.as_query_engine()
```

## 📊 Data Processing Architecture

### Pandas Integration

#### DataFrame Operations
```python
# Smart column selection
def get_smart_columns(df: pd.DataFrame, query: str):
    query_lower = query.lower()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=['object']).columns
    
    if "revenue" in query_lower:
        return "Revenue" if "Revenue" in numeric_cols else numeric_cols[0]
    elif "users" in query_lower:
        return "Users" if "Users" in numeric_cols else numeric_cols[0]
    # ... more smart selection logic
```

#### Data Validation
```python
def validate_dataframe(df: pd.DataFrame):
    # Check for required columns
    # Validate data types
    # Handle missing values
    # Ensure data quality
```

### SQLAlchemy Integration

#### Database Connection
```python
def create_database_connection(connection_data: dict):
    # Parse connection parameters
    # Create SQLAlchemy engine
    # Test connection
    # Return engine for queries
```

#### Query Execution
```python
def execute_sql_query(engine, query: str):
    # Execute SQL query
    # Return pandas DataFrame
    # Handle errors gracefully
```

## 🎨 Visualization Architecture

### Plotly Integration

#### Chart Generation Process
```python
def create_visualization(self, df: pd.DataFrame, chart_type: str, query: str):
    # 1. Determine chart type
    if chart_type == "bar":
        fig = px.bar(grouped_data, x=x_col, y=y_col)
    
    # 2. Apply dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff'}
    )
    
    # 3. Generate clean JSON
    chart_data = {
        "data": [{
            "type": "bar",
            "x": trace.x.tolist(),
            "y": trace.y.tolist(),
            "hovertemplate": "Category=%{x}<br>Revenue=%{y}"
        }],
        "layout": {
            "title": "Revenue by Category",
            "xaxis": {"title": "Category"},
            "yaxis": {"title": "Revenue"}
        }
    }
    
    return chart_data
```

#### Chart Type Detection
```python
def analyze_query_intent(self, query: str):
    intent = {
        "type": "general",
        "visualization": None,
        "aggregation": None
    }
    
    query_lower = query.lower()
    
    # Detect visualization type
    if "bar chart" in query_lower:
        intent["visualization"] = "bar"
    elif "pie chart" in query_lower:
        intent["visualization"] = "pie"
    # ... more detection logic
    
    return intent
```

## 🔄 Data Flow Architecture

### Request Processing Flow
```
1. User Input → Frontend Validation
2. HTTP Request → FastAPI Backend
3. Request Validation → Pydantic Models
4. Session Check → Data Retrieval
5. Query Processing → LLM Agent
6. Data Analysis → Pandas Operations
7. Visualization → Plotly Generation
8. Response → JSON Serialization
9. Frontend Update → React State
10. UI Rendering → User Display
```

### Error Handling Architecture
```python
# Global error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Component-specific error handling
try:
    result = process_with_agent(df, query)
except Exception as e:
    # Fallback to direct pandas operations
    result = fallback_processing(df, query)
```

## 🚀 Performance Optimizations

### Frontend Optimizations
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Debouncing**: Input debouncing for search
- **Virtual Scrolling**: For large data lists (future)

### Backend Optimizations
- **Async Operations**: Non-blocking I/O
- **Connection Pooling**: Database connection reuse
- **Caching**: Session-based data caching
- **Query Optimization**: Efficient pandas operations

### AI Processing Optimizations
- **Agent Caching**: Reuse agent instances
- **Vector Store Optimization**: FAISS indexing
- **Response Streaming**: Real-time response updates (future)
- **Model Optimization**: Quantized models (future)

## 🔐 Security Architecture

### Input Validation
```python
# File upload validation
def validate_file(file: UploadFile):
    # Check file type
    # Validate file size
    # Scan for malicious content
    # Sanitize filename

# SQL injection prevention
def execute_safe_query(engine, query: str, params: dict):
    # Use parameterized queries
    # Validate query structure
    # Limit query complexity
```

### Data Security
```python
# Session management
def create_secure_session():
    # Generate secure session ID
    # Set expiration time
    # Encrypt sensitive data
    # Log session activities
```

---

*This document provides detailed technical implementation. For system overview, see [System Overview](system-overview.md).*
