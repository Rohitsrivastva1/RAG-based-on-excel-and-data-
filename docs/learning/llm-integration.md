# LLM Integration Guide

## 🧠 Understanding AI Processing in RAG Analytics

This guide explains how the system integrates with Large Language Models (LLMs) to process natural language queries and generate intelligent responses.

## 🎯 Overview

The RAG Analytics system uses a sophisticated AI pipeline that combines:
- **LangChain**: Agent orchestration and tool management
- **LlamaIndex**: Retrieval-Augmented Generation (RAG)
- **Google Gemini**: Large Language Model for natural language understanding
- **FAISS**: Vector store for semantic search

## 🔄 AI Processing Flow

### 1. Query Reception
```
User Input → Frontend Validation → Backend Processing
```

**Code Example:**
```python
# In enhanced_backend.py
@app.post("/ask_question")
async def ask_question(question_data: dict):
    question = question_data["question"]
    session_id = question_data["session_id"]
    
    # Get session data
    session_data = get_session_data(session_id)
    df = session_data["dataframe"]
    
    # Process with AI
    result = ai_processor.process_question(df, question)
    return result
```

### 2. Intent Analysis
The system analyzes the user's query to understand what they want to do.

**Intent Types:**
- **Data Analysis**: "How many rows?", "What are unique values?"
- **Visualization**: "Show me a bar chart", "Create a pie chart"
- **Aggregation**: "What's the total revenue?", "Average growth rate"
- **Filtering**: "Show only Education category", "Revenue > 1000"

**Code Example:**
```python
def analyze_query_intent(self, query: str):
    intent = {
        "type": "general",
        "visualization": None,
        "aggregation": None
    }
    
    query_lower = query.lower()
    
    # Detect visualization requests
    if ("chart" in query_lower or "graph" in query_lower or 
        "plot" in query_lower or "visualize" in query_lower):
        intent["type"] = "visualization"
        
        # Determine chart type
        if "bar" in query_lower:
            intent["visualization"] = "bar"
        elif "pie" in query_lower:
            intent["visualization"] = "pie"
        elif "line" in query_lower:
            intent["visualization"] = "line"
    
    # Detect aggregation requests
    if "sum" in query_lower or "total" in query_lower:
        intent["aggregation"] = "sum"
    elif "average" in query_lower or "mean" in query_lower:
        intent["aggregation"] = "mean"
    
    return intent
```

### 3. LLM Agent Creation
The system creates a specialized agent that can work with pandas DataFrames.

**Agent Architecture:**
```python
class LLMAgent:
    def __init__(self):
        self.llm = self.initialize_llm()
        self.embedding_manager = EmbeddingManager()
    
    def initialize_llm(self):
        """Initialize Google Gemini LLM"""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=1000
        )
```

### 4. Custom Pandas Tool
The agent uses a custom tool that prevents it from creating charts and focuses on data analysis.

**Tool Implementation:**
```python
def pandas_tool(query: str) -> str:
    """Execute pandas operations on the existing DataFrame"""
    try:
        # Prevent plotting operations
        if any(plot_lib in query.lower() for plot_lib in 
               ['matplotlib', 'plt.', 'seaborn', 'sns.', 'plotly', 'fig.']):
            return "Error: Chart creation is not allowed. Please use pandas operations only for data analysis."
        
        # Execute the query in a controlled environment
        local_vars = {'df': df}
        result = eval(query, {"__builtins__": {}}, local_vars)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

### 5. Agent Execution
The agent processes the query with enhanced context about the DataFrame.

**Enhanced Query Construction:**
```python
def process_with_agent(self, df: pd.DataFrame, query: str, context: str = ""):
    # Create enhanced query with DataFrame information
    enhanced_query = f"""
IMPORTANT: You are working with a DataFrame called 'df' that contains the following data:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Sample data: {df.head().to_string()}

The DataFrame 'df' is already loaded and available. Do NOT create a new DataFrame.
Use the existing 'df' variable directly.

CRITICAL INSTRUCTIONS:
- DO NOT try to create charts, graphs, or visualizations
- DO NOT use matplotlib, seaborn, plotly, or any plotting libraries
- Just analyze the data and return insights as text
- Use pandas operations only for data analysis
- Return clean, concise answers without any plotting code

Question: {query}
"""
    
    # Execute with agent
    response = agent.invoke({"input": enhanced_query})
    return self.extract_clean_answer(response)
```

## 🔍 RAG (Retrieval-Augmented Generation)

### Vector Store Setup
The system uses FAISS to create a vector index of the data for semantic search.

**Embedding Manager:**
```python
class EmbeddingManager:
    def __init__(self, model_type="huggingface", dimension=384):
        self.model_type = model_type
        self.dimension = dimension
        self.vector_store = None
        
    def build_index(self, documents: List[str]):
        """Build FAISS vector index from documents"""
        if self.model_type == "huggingface":
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(documents)
        elif self.model_type == "openai":
            from openai import OpenAI
            client = OpenAI()
            embeddings = [client.embeddings.create(
                input=doc, model="text-embedding-ada-002"
            ).data[0].embedding for doc in documents]
        
        # Create FAISS index
        import faiss
        index = faiss.IndexFlatIP(self.dimension)
        index.add(embeddings.astype('float32'))
        self.vector_store = index
```

### Document Processing
Data is converted into searchable documents for the vector store.

**Document Creation:**
```python
def create_documents_from_dataframe(df: pd.DataFrame):
    """Convert DataFrame rows into searchable documents"""
    documents = []
    
    for index, row in df.iterrows():
        # Create document text from row data
        doc_text = f"Row {index}: "
        for col, value in row.items():
            doc_text += f"{col}={value}, "
        doc_text = doc_text.rstrip(", ")
        
        documents.append(Document(text=doc_text))
    
    return documents
```

### Semantic Search
The system can find relevant data based on semantic similarity.

**Search Implementation:**
```python
def search_relevant_data(self, query: str, top_k: int = 5):
    """Find relevant data using semantic search"""
    if not self.vector_store:
        return []
    
    # Encode query
    query_embedding = self.encode_query(query)
    
    # Search vector store
    scores, indices = self.vector_store.search(
        query_embedding.reshape(1, -1), top_k
    )
    
    # Return relevant documents
    relevant_docs = []
    for score, idx in zip(scores[0], indices[0]):
        if score > 0.7:  # Similarity threshold
            relevant_docs.append(self.documents[idx])
    
    return relevant_docs
```

## 🤖 LangChain Agent Architecture

### Agent Types
The system uses different agent types for different tasks:

**1. ReAct Agent (Primary)**
```python
from langchain.agents import create_react_agent, AgentExecutor

# Create ReAct agent with pandas tool
agent = create_react_agent(
    llm=self.llm,
    tools=[pandas_tool_obj],
    prompt=prompt_template
)

# Execute with agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=[pandas_tool_obj],
    max_iterations=3,
    verbose=True
)
```

**2. Custom Prompt Template**
```python
prompt = PromptTemplate.from_template(f"""
You are working with a pandas DataFrame called 'df' that is already loaded in memory.

The DataFrame has the following structure:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Sample data: {df.head().to_string()}

IMPORTANT: The DataFrame 'df' is already available. Do NOT create a new DataFrame.
Use the existing 'df' variable directly for all operations.

CRITICAL: DO NOT create charts, graphs, or visualizations. Only perform data analysis operations.

Question: {{input}}

Use the pandas_analysis tool to execute your operations on the existing DataFrame.
Always use 'df' to refer to the DataFrame.
Only perform data analysis - no plotting or visualization.

{{agent_scratchpad}}
""")
```

### Tool Integration
The agent has access to specialized tools for data manipulation.

**Tool Definition:**
```python
pandas_tool_obj = Tool(
    name="pandas_analysis",
    description="Execute pandas operations on the DataFrame. Use 'df' to refer to the DataFrame. DO NOT create charts or visualizations - only data analysis operations.",
    func=pandas_tool
)
```

## 🎨 Response Processing

### Answer Extraction
The system extracts clean answers from the agent's response.

**Response Processing:**
```python
def extract_clean_answer(self, response):
    """Extract clean answer from agent response"""
    if not response:
        return "No response generated"
    
    # Handle different response types
    if hasattr(response, 'output'):
        answer = response.output
    elif isinstance(response, dict):
        if 'output' in response:
            answer = response['output']
        elif 'input' in response and 'output' in response:
            # Extract from input/output format
            answer = response['output']
        else:
            answer = str(response)
    else:
        answer = str(response)
    
    # Clean up the answer
    answer = self.clean_response(answer)
    return answer

def clean_response(self, answer: str) -> str:
    """Clean up the response text"""
    # Remove extra formatting
    answer = answer.strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "The answer is:",
        "Based on the data:",
        "Here's the result:",
        "The result is:"
    ]
    
    for prefix in prefixes_to_remove:
        if answer.startswith(prefix):
            answer = answer[len(prefix):].strip()
    
    return answer
```

### Fallback Logic
The system has intelligent fallback mechanisms when the agent fails.

**Fallback Implementation:**
```python
def process_with_fallback(self, df: pd.DataFrame, query: str):
    """Process query with fallback logic"""
    try:
        # Try agent processing first
        result = self.process_with_agent(df, query)
        if result and result.get("answer"):
            return result
    except Exception as e:
        print(f"Agent processing failed: {e}")
    
    # Fallback to direct pandas operations
    try:
        answer = self.direct_pandas_processing(df, query)
        return {
            "answer": answer,
            "query_type": "fallback_pandas",
            "visualization": None
        }
    except Exception as e:
        return {
            "answer": f"Error processing query: {str(e)}",
            "query_type": "error",
            "visualization": None
        }
```

## 🔧 Configuration and Tuning

### LLM Parameters
Fine-tune the LLM behavior for better results.

**Configuration Options:**
```python
# Temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
temperature = 0.1  # Low for consistent data analysis

# Max tokens: Limits response length
max_tokens = 1000

# Top-p: Controls diversity of responses
top_p = 0.9

# Frequency penalty: Reduces repetition
frequency_penalty = 0.0

# Presence penalty: Encourages new topics
presence_penalty = 0.0
```

### Agent Parameters
Configure agent behavior for optimal performance.

**Agent Configuration:**
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=3,        # Limit agent iterations
    max_execution_time=30,   # Timeout in seconds
    early_stopping_method="generate",  # Stop early if possible
    verbose=True             # Enable debugging
)
```

## 🚀 Advanced Features

### Multi-Model Support
The system can be extended to support multiple LLM providers.

**Provider Abstraction:**
```python
class LLMProvider:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self.llm = self.initialize_llm()
    
    def initialize_llm(self):
        if self.provider == "gemini":
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=self.api_key
            )
        elif self.provider == "openai":
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=self.api_key
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=self.api_key
            )
```

### Custom Tools
Add specialized tools for specific data analysis tasks.

**Custom Tool Example:**
```python
def statistical_analysis_tool(query: str) -> str:
    """Perform statistical analysis on the DataFrame"""
    try:
        if "describe" in query.lower():
            return str(df.describe())
        elif "correlation" in query.lower():
            return str(df.corr())
        elif "missing" in query.lower():
            return str(df.isnull().sum())
        else:
            return "Statistical analysis not supported for this query"
    except Exception as e:
        return f"Error in statistical analysis: {str(e)}"

# Add to agent tools
statistical_tool = Tool(
    name="statistical_analysis",
    description="Perform statistical analysis on the DataFrame",
    func=statistical_analysis_tool
)
```

## 🐛 Troubleshooting

### Common Issues

#### Agent Not Responding
```python
# Check agent configuration
print(f"Agent tools: {[tool.name for tool in agent.tools]}")
print(f"LLM model: {agent.llm.model_name}")

# Test with simple query
test_response = agent.invoke({"input": "What is the shape of the DataFrame?"})
print(f"Test response: {test_response}")
```

#### Poor Response Quality
```python
# Adjust temperature
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,  # Lower for more consistent results
    max_tokens=1000
)

# Improve prompt clarity
enhanced_prompt = f"""
You are a data analyst. Analyze the following DataFrame and answer the question.

DataFrame Info:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Sample: {df.head()}

Question: {query}

Provide a clear, concise answer based on the data.
"""
```

#### Memory Issues
```python
# Limit DataFrame size for large datasets
if len(df) > 10000:
    df_sample = df.sample(n=1000)  # Use sample for analysis
    result = process_with_agent(df_sample, query)
else:
    result = process_with_agent(df, query)
```

## 📚 Best Practices

### 1. Query Optimization
- Use specific, clear questions
- Include context about what you want to know
- Avoid ambiguous terms

**Good Examples:**
```
"What is the total revenue for each category?"
"Show me the average growth rate by category"
"How many rows have revenue greater than 5000?"
```

**Poor Examples:**
```
"Tell me about the data"
"What's here?"
"Make a chart"
```

### 2. Error Handling
- Always provide fallback mechanisms
- Log errors for debugging
- Give users helpful error messages

### 3. Performance Optimization
- Cache agent instances
- Limit DataFrame size for large datasets
- Use efficient pandas operations

---

*This guide covers the core LLM integration. For more details on specific components, see the other learning guides.*
