# RAG Analytics System - Setup Guide

This guide will help you set up and run the RAG Analytics system on your local machine.

## Prerequisites

### Required Software
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/)

### Required API Keys
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key** (optional) - Get from [Anthropic Console](https://console.anthropic.com/)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository (if from git)
git clone <repository-url>
cd RAG_LLM

# Copy environment template
cp env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your configuration:

```env
# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./rag_analytics.db
REDIS_URL=redis://localhost:6379

# AI/LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LLM_MODEL=gpt-3.5-turbo

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_DIR=./uploads

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Start the Backend

**Option A: Using the start script (Recommended)**
```bash
python start_backend.py
```

**Option B: Manual setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### 4. Start the Frontend

**Option A: Using the start script (Recommended)**

**Windows:**
```cmd
start_frontend.bat
```

**Linux/Mac:**
```bash
./start_frontend.sh
```

**Option B: Manual setup**
```bash
# Install Node.js dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at: http://localhost:3000

## Usage Guide

### 1. Upload Data

1. Open http://localhost:3000 in your browser
2. Go to the "Upload Data" tab
3. Drag and drop an Excel (.xlsx, .xls) or CSV file
4. Wait for the file to be processed

### 2. Connect to Database

1. Go to the "Connect Database" tab
2. Fill in your database connection details:
   - Database Type: PostgreSQL, MySQL, or SQLite
   - Host: Database server address
   - Port: Database port
   - Database Name: Name of your database
   - Username/Password: Your credentials
3. Click "Connect to Database"

### 3. Ask Questions

1. Go to the "Ask Questions" tab
2. Type your question in natural language, such as:
   - "What are the top 10 sales by region?"
   - "Show me trends over time"
   - "What's the average salary by department?"
   - "Create a pie chart of product categories"
3. Press Enter or click Send
4. View the generated query and results
5. See the automatic visualization

### 4. Export Results

1. After asking a question, you can export the results
2. Click the export buttons (CSV, PNG, PDF) in the visualization section
3. The file will be downloaded to your computer

## Features

### Data Sources
- **Excel/CSV Files**: Upload files up to 50MB
- **Databases**: Connect to PostgreSQL, MySQL, SQLite
- **Automatic Schema Detection**: System automatically detects data structure

### AI Capabilities
- **Natural Language Processing**: Ask questions in plain English
- **Query Generation**: Automatically generates SQL or Pandas queries
- **Smart Visualizations**: Suggests appropriate chart types
- **Error Handling**: Provides helpful error messages and suggestions

### Visualizations
- **Chart Types**: Bar, Line, Pie, Scatter, KPI dashboards
- **Interactive**: Zoom, pan, hover for details
- **Export Options**: CSV, PNG, PDF formats
- **Responsive**: Works on desktop and mobile

### Security
- **Read-Only Access**: Only SELECT queries allowed for databases
- **File Validation**: Checks file types and sizes
- **Input Sanitization**: Prevents malicious code execution
- **Session Management**: Secure session handling

## Troubleshooting

### Common Issues

**1. Backend won't start**
- Check if Python 3.8+ is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify your `.env` file is configured correctly

**2. Frontend won't start**
- Check if Node.js 16+ is installed
- Install dependencies: `npm install`
- Check if port 3000 is available
- Clear npm cache: `npm cache clean --force`

**3. API Key Issues**
- Verify your OpenAI API key is valid and has credits
- Check the API key in your `.env` file
- Ensure you have sufficient API quota

**4. Database Connection Issues**
- Verify database credentials
- Check if database server is running
- Ensure network connectivity
- For SQLite, check file permissions

**5. File Upload Issues**
- Check file size (must be under 50MB)
- Verify file format (Excel or CSV only)
- Ensure file is not corrupted
- Check upload directory permissions

### Getting Help

1. Check the API documentation at http://localhost:8000/docs
2. Review the browser console for frontend errors
3. Check the backend logs in the terminal
4. Verify all environment variables are set correctly

## Development

### Project Structure
```
RAG_LLM/
├── backend/                 # Backend modules
│   ├── __init__.py
│   ├── database.py         # Database management
│   ├── data_ingestion.py   # File and DB ingestion
│   ├── ai_processor.py     # AI query generation
│   ├── query_executor.py   # Query execution
│   └── visualization.py    # Chart generation
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── App.js             # Main app component
│   └── index.js           # Entry point
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
└── README.md             # Project documentation
```

### Adding New Features

1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create new components in `src/components/`
3. **AI Processing**: Extend `backend/ai_processor.py`
4. **Visualizations**: Add chart types in `backend/visualization.py`

### Testing

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test
```

## Production Deployment

For production deployment, consider:

1. **Environment**: Use production-grade database (PostgreSQL)
2. **Security**: Set strong SECRET_KEY and disable DEBUG
3. **Scaling**: Use Redis for caching and session management
4. **Monitoring**: Add logging and monitoring tools
5. **HTTPS**: Use SSL certificates for secure connections
6. **Load Balancing**: Use nginx or similar for multiple instances

## License

This project is licensed under the MIT License.
