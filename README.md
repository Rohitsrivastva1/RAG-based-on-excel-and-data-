# RAG Analytics System

A comprehensive data analytics platform that enables users to upload Excel/CSV files or connect to databases, then ask natural language questions to generate insights, visualizations, and dashboards.

## Features

- **Data Ingestion**: Upload Excel/CSV files (up to 50MB) or connect to SQL databases
- **AI Processing**: Natural language to SQL/Pandas query generation using LlamaIndex and LangChain
- **Visualization**: Automatic chart generation (bar, line, pie, scatter, KPIs)
- **Dashboard**: Interactive React-based dashboard with chat interface
- **Export**: Download results as CSV, PNG, or PDF

## Architecture

- **Frontend**: React 18 with Ant Design, Plotly.js for visualizations, modern dark theme UI
- **Backend**: FastAPI with modular architecture, Pydantic for validation, comprehensive logging
- **AI Layer**: LlamaIndex + LangChain for query generation, Google Gemini integration
- **Data Layer**: Pandas for Excel/CSV processing, FAISS for vector storage
- **Storage**: Redis for session management, HuggingFace for embeddings

## Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the backend server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open http://localhost:3000 in your browser

## API Endpoints

- `POST /upload_excel` - Upload Excel/CSV files with background indexing
- `POST /ask_question` - Ask natural language questions with AI processing
- `GET /sessions` - Get all active sessions
- `GET /session/{id}/info` - Get detailed session information
- `DELETE /session/{id}` - Delete session and cleanup resources
- `GET /health` - Health check with component status

## Environment Variables

See `.env.example` for required environment variables including:
- `GOOGLE_API_KEY` - Google Gemini API key (required)
- `REDIS_URL` - Redis connection for session storage (optional)
- `DATABASE_URL` - Database connection string (optional)
- `EMBEDDING_MODEL` - HuggingFace embedding model (default: sentence-transformers/all-MiniLM-L6-v2)
- `MAX_FILE_SIZE_MB` - Maximum file upload size (default: 50)
- `MAX_ROWS_INDEXABLE` - Maximum rows for indexing (default: 10000)

## Security

- Sandboxed query execution environment
- Input validation and sanitization
- File size limits and type restrictions
- SQL injection prevention
