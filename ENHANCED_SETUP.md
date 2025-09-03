# 🚀 Enhanced RAG Analytics System Setup Guide

## 🎯 Overview

This enhanced system provides **LLM-powered data analytics** with:
- **RAG (Retrieval Augmented Generation)** using LlamaIndex + FAISS
- **LangChain Agents** for intelligent query processing
- **Dynamic Database Connections** (PostgreSQL, MySQL, SQLite)
- **Intelligent Visualizations** with Plotly
- **Vector Indexing** for semantic search

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Enhanced Backend │    │   AI/ML Layer   │
│                 │    │                  │    │                 │
│ • Chat Interface│◄──►│ • FastAPI        │◄──►│ • LlamaIndex    │
│ • File Upload   │    │ • LangChain      │    │ • FAISS Vector  │
│ • Visualizations│    │ • Database Mgmt  │    │ • OpenAI GPT    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **OpenAI API Key** (for LLM features)
- **Database** (PostgreSQL/MySQL - optional)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Environment Setup

Create `.env` file:
```env
# Required for LLM features
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 3. Start the Enhanced Backend

```bash
# Option 1: Use startup script (recommended)
python start_enhanced_backend.py

# Option 2: Direct start
python enhanced_backend.py
```

### 4. Start the Frontend

```bash
# Windows
.\start_frontend.bat

# Linux/Mac
./start_frontend.sh

# Or manually
npm start
```

## 🎯 Enhanced Features

### 🧠 LLM-Powered Queries

**Before (Keyword-based):**
```
Question: "maximum salary"
Response: "Maximum salary: 70000"
```

**After (LLM-powered):**
```
Question: "What's the highest salary and who earns it?"
Response: "The highest salary is $95,000 earned by Sarah Johnson in the Engineering department. 
          This represents the 95th percentile of all salaries in the dataset."
```

### 🔍 RAG with Vector Indexing

1. **Upload Excel/CSV** → Automatically builds FAISS vector index
2. **Ask Questions** → Retrieves relevant context from vector store
3. **LLM Processing** → Uses context + question for intelligent responses
4. **Dynamic Visualizations** → Generates appropriate charts

### 🗄️ Database Integration

Connect to live databases:
- **PostgreSQL** - Full SQL support
- **MySQL** - Full SQL support  
- **SQLite** - Local file databases

```python
# Example database connection
POST /connect_database
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "analytics_db",
  "username": "user",
  "password": "password"
}
```

### 📊 Intelligent Visualizations

**Auto-suggested chart types:**
- **Bar charts** for categorical vs numeric data
- **Line charts** for trends over time
- **Pie charts** for category distributions
- **Scatter plots** for correlations
- **Histograms** for distributions

## 🔧 API Endpoints

### Enhanced Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health with feature list |
| `/upload_excel` | POST | Upload file + build vector index |
| `/connect_database` | POST | Connect to database |
| `/ask_question` | POST | LLM-powered query processing |
| `/session/{id}/info` | GET | Detailed session information |
| `/database/{id}/tables` | GET | List database tables |
| `/database/{id}/table/{name}` | GET | Get table data |

### Response Format

```json
{
  "question": "What's the average salary by department?",
  "answer": "The average salary by department is: Engineering: $85,000, Sales: $65,000, Marketing: $70,000",
  "query_type": "llm_agent",
  "data": {
    "summary": {...},
    "context": "Relevant context from vector index..."
  },
  "visualization": {
    "type": "bar",
    "data": {...},
    "title": "Average Salary by Department"
  },
  "sql_query": "SELECT department, AVG(salary) FROM employees GROUP BY department",
  "row_count": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎨 Frontend Enhancements

### Enhanced Chat Interface

- **Query Type Tags** - Shows processing method
- **SQL Query Display** - Shows generated SQL
- **Context Information** - Shows RAG context used
- **Row Count** - Shows data size
- **Enhanced Visualizations** - Better chart rendering

### New Components

- **Database Connection Form** - Connect to live databases
- **Session Management** - View detailed session info
- **Enhanced Visualizations** - Dynamic Plotly charts

## 🔍 Example Queries

### File-based Analytics

```
"Show me the top 5 highest earners"
"What's the salary distribution by department?"
"Find employees with salary above $80,000"
"Create a bar chart of average salary by department"
```

### Database Analytics

```
"Show me all customers from California"
"What's the total revenue by product category?"
"Find the top 10 products by sales volume"
"Create a trend chart of monthly sales"
```

## 🛠️ Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   ```
   Error: OPENAI_API_KEY not found
   Solution: Add your API key to .env file
   ```

2. **FAISS Installation Issues**
   ```bash
   pip install faiss-cpu
   # or for GPU support
   pip install faiss-gpu
   ```

3. **Database Connection Failed**
   ```
   Error: Failed to connect to database
   Solution: Check connection parameters and database status
   ```

4. **Memory Issues with Large Files**
   ```
   Solution: Use smaller datasets or increase system memory
   ```

### Performance Tips

- **Small datasets** (< 1000 rows) - Full row indexing
- **Large datasets** (> 1000 rows) - Schema + statistics only
- **Vector index** - Stored in memory for fast retrieval
- **Database queries** - Cached for repeated questions

## 🚀 Advanced Usage

### Custom Embeddings

```python
# Use different embedding models
embedding_manager = EmbeddingManager(
    embedding_model="huggingface",  # or "openai"
    dimension=384  # for sentence-transformers
)
```

### Custom LLM Models

```python
# Use different LLM models
llm_agent = LLMAgent(
    model_name="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.1
)
```

### Custom Visualizations

```python
# Add custom chart types
def create_custom_chart(df, query):
    # Your custom visualization logic
    return chart_json
```

## 📈 Performance Metrics

- **Vector Index Build**: ~2-5 seconds for 1000 rows
- **Query Processing**: ~1-3 seconds with LLM
- **Visualization Generation**: ~0.5-1 second
- **Database Queries**: ~0.1-2 seconds (depends on query complexity)

## 🔒 Security Considerations

- **API Keys** - Store in environment variables
- **Database Credentials** - Use secure connections
- **File Uploads** - Validate file types and sizes
- **Query Sanitization** - Prevent SQL injection

## 🎯 Next Steps

1. **Authentication** - Add user management
2. **Caching** - Redis for query results
3. **Advanced Analytics** - Statistical modeling
4. **Real-time Updates** - WebSocket connections
5. **Multi-tenant** - Support multiple users

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Check the console logs for detailed error messages

---

**🎉 You now have a fully functional LLM-powered RAG analytics system!**
