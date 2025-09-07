# LlamaIndex + LangChain Quick Reference

## 🚀 Quick Start

### **1. Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_google_api_key_here"

# Start the system
cd backend
python app.py
```

### **2. Basic Usage**
```python
import requests

# Upload file
files = {'file': open('data.xlsx', 'rb')}
response = requests.post('http://localhost:8000/upload_file', files=files)
session_id = response.json()['session_id']

# Ask questions
data = {
    'question': 'What are the unique values in Category column?',
    'session_id': session_id
}
response = requests.post('http://localhost:8000/ask_question', data=data)
result = response.json()
```

## 🔧 Key Components

### **LangChain (Agents)**
- **File**: `backend/agents/llm_agent.py`
- **Purpose**: Natural language to pandas code conversion
- **LLM**: Google Gemini (ChatGoogleGenerativeAI)
- **Agent**: Pandas DataFrame Agent

### **LlamaIndex (Embeddings)**
- **File**: `backend/managers/embedding_manager.py`
- **Purpose**: Document indexing and semantic search
- **Model**: HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS

## 📊 Query Types

### **Data Analysis**
```python
queries = [
    "What are the unique values in Category column?",
    "How many rows are in this dataset?",
    "What is the average revenue?",
    "Which category has the highest revenue?"
]
```

### **Visualizations**
```python
viz_queries = [
    "Show me bar graph related to category and users",
    "Create a pie chart for category distribution",
    "Plot revenue trends over time",
    "Show correlation between users and revenue"
]
```

### **Aggregations**
```python
agg_queries = [
    "What is the total revenue by category?",
    "Show me the count of records per category",
    "What is the average growth rate by category?",
    "Find categories with revenue above 1000"
]
```

## 🛠️ API Endpoints

### **File Upload**
```http
POST /upload_file
Content-Type: multipart/form-data

file: [Excel/CSV file]
```

### **Ask Question**
```http
POST /ask_question
Content-Type: application/x-www-form-urlencoded

question: "Your question here"
session_id: "session_id_from_upload"
```

### **Health Check**
```http
GET /health
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
LOG_LEVEL=INFO
```

### **Feature Flags**
```bash
ENABLE_LLM_AGENT=true
ENABLE_EMBEDDINGS=true
ENABLE_DATABASE=true
ENABLE_VISUALIZATION=true
```

## 📈 Response Format

### **Success Response**
```json
{
  "question": "What are the unique values in Category column?",
  "answer": "['Education', 'Entertainment', 'Finance', 'Health', 'Tech']",
  "query_type": "llm_agent",
  "data": {
    "summary": {
      "rows": 30,
      "columns": 5,
      "column_names": ["Date", "Category", "Users", "Revenue", "Growth_%"],
      "data_types": {
        "Date": "datetime64[ns]",
        "Category": "object",
        "Users": "int64",
        "Revenue": "float64",
        "Growth_%": "float64"
      }
    },
    "context": "Dataset statistics: 30 rows, 5 columns...",
    "generated_code": "df['Category'].unique()",
    "visualization": {
      "type": "bar",
      "data": {
        "x": ["Education", "Entertainment", "Finance", "Health", "Tech"],
        "y": [2500, 2968, 3964, 3055, 2144],
        "x_label": "Category",
        "y_label": "Total Users",
        "title": "Users by Category"
      }
    }
  },
  "session_id": "user_session_123",
  "timestamp": "2025-09-05T20:42:55.012578",
  "duration_ms": 8176.857
}
```

### **Error Response**
```json
{
  "detail": "LLM agent processing failed: Google Gemini API quota exceeded. Please try again later."
}
```

## 🔍 Troubleshooting

### **Common Issues**

1. **"LLM agent not available"**
   - Check `GOOGLE_API_KEY` is set
   - Verify API key is valid
   - Check internet connection

2. **"Quota exceeded"**
   - Google Gemini free tier: 50 requests/day
   - Wait for quota reset or upgrade plan

3. **"Invalid API key"**
   - Verify API key format
   - Check key permissions
   - Regenerate key if needed

4. **"Embedding model not available"**
   - Check HuggingFace model download
   - Verify internet connection
   - Check disk space

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python app.py
```

## 🚀 Performance Tips

### **Optimization**
- Use smaller datasets for testing
- Cache frequently used data
- Batch similar queries
- Monitor API usage

### **Resource Limits**
- Max file size: 50MB
- Max rows indexable: 10,000
- Max tokens per request: 2,000
- Execution timeout: 30 seconds

## 📚 Examples

### **Complete Workflow**
```python
import requests
import pandas as pd

# 1. Upload file
files = {'file': open('sales_data.xlsx', 'rb')}
upload_response = requests.post('http://localhost:8000/upload_file', files=files)
session_id = upload_response.json()['session_id']

# 2. Ask questions
questions = [
    "What are the unique values in Category column?",
    "Show me bar graph related to category and users",
    "What is the average revenue by category?",
    "Which category has the highest growth rate?"
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
    if result['data']['visualization']:
        print(f"Chart: {result['data']['visualization']['type']}")
    print("-" * 50)
```

### **Error Handling**
```python
import requests

def ask_question_safe(question, session_id):
    try:
        data = {'question': question, 'session_id': session_id}
        response = requests.post('http://localhost:8000/ask_question', data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json()['detail']}
            
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server"}
    except Exception as e:
        return {"error": str(e)}

# Usage
result = ask_question_safe("What are the unique values?", session_id)
if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Answer: {result['answer']}")
```

## 🔗 Useful Links

- [LangChain Documentation](https://python.langchain.com/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [HuggingFace Models](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Need Help?** Check the full documentation in `ARCHITECTURE.md` and `IMPLEMENTATION_GUIDE.md` for detailed technical information.
