# RAG Analytics System

A comprehensive data analytics platform that enables users to upload Excel/CSV files or connect to databases, then ask natural language questions to generate insights, visualizations, and dashboards.

## Features

- **Data Ingestion**: Upload Excel/CSV files (up to 50MB) or connect to SQL databases
- **AI Processing**: Natural language to SQL/Pandas query generation using LlamaIndex and LangChain
- **Visualization**: Automatic chart generation (bar, line, pie, scatter, KPIs)
- **Dashboard**: Interactive React-based dashboard with chat interface
- **Export**: Download results as CSV, PNG, or PDF

## Architecture

- **Frontend**: React with Ant Design, Plotly.js for visualizations
- **Backend**: FastAPI with SQLAlchemy for database operations
- **AI Layer**: LlamaIndex + LangChain for query generation
- **Data Layer**: Pandas for Excel/CSV, SQLAlchemy for databases

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

- `POST /upload_excel` - Upload Excel/CSV files
- `POST /connect_db` - Connect to database
- `POST /ask_question` - Ask natural language questions
- `GET /get_dashboard` - Get dashboard data
- `GET /export/{format}` - Export results

## Environment Variables

See `.env.example` for required environment variables including:
- Database connection strings
- OpenAI/Anthropic API keys
- Redis configuration (optional)

## Security

- Sandboxed query execution environment
- Input validation and sanitization
- File size limits and type restrictions
- SQL injection prevention
