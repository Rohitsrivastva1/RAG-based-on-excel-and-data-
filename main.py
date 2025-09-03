"""
RAG Analytics System - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import uvicorn
from dotenv import load_dotenv

from backend.database import DatabaseManager
from backend.ai_processor import AIProcessor
from backend.data_ingestion import DataIngestionManager
from backend.visualization import VisualizationEngine
from backend.query_executor import QueryExecutor

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Analytics API",
    description="AI-powered data analytics platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
ai_processor = AIProcessor()
data_ingestion = DataIngestionManager()
visualization_engine = VisualizationEngine()
query_executor = QueryExecutor()

# Pydantic models
class DatabaseConnection(BaseModel):
    host: str
    port: int
    database: str
    username: str
    password: str
    db_type: str  # postgresql, mysql, sqlite

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class DashboardRequest(BaseModel):
    session_id: str

@app.get("/")
async def root():
    return {"message": "RAG Analytics API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/upload_excel")
async def upload_excel(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """Upload Excel/CSV file and process it"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel and CSV files are allowed")
        
        # Check file size (50MB limit)
        max_size = int(os.getenv("MAX_FILE_SIZE", 52428800))
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Process the file
        result = await data_ingestion.process_excel_file(content, file.filename, session_id)
        
        return JSONResponse(content={
            "message": "File uploaded successfully",
            "session_id": result["session_id"],
            "schema": result["schema"],
            "preview": result["preview"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/connect_db")
async def connect_database(connection: DatabaseConnection):
    """Connect to a database"""
    try:
        result = await data_ingestion.connect_database(connection)
        return JSONResponse(content={
            "message": "Database connected successfully",
            "session_id": result["session_id"],
            "tables": result["tables"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_question")
async def ask_question(request: QuestionRequest):
    """Process natural language question and return results"""
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Generate query using AI
        query_result = await ai_processor.process_question(
            request.question, 
            request.session_id
        )
        
        # Execute the query
        execution_result = await query_executor.execute_query(
            query_result["query"],
            query_result["query_type"],
            request.session_id
        )
        
        # Generate visualization if applicable
        visualization = None
        if execution_result["data"] and len(execution_result["data"]) > 0:
            visualization = await visualization_engine.create_visualization(
                execution_result["data"],
                request.question,
                query_result["suggested_chart_type"]
            )
        
        return JSONResponse(content={
            "question": request.question,
            "query": query_result["query"],
            "query_type": query_result["query_type"],
            "data": execution_result["data"],
            "visualization": visualization,
            "execution_time": execution_result["execution_time"],
            "row_count": execution_result["row_count"]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_dashboard/{session_id}")
async def get_dashboard(session_id: str):
    """Get dashboard data for a session"""
    try:
        dashboard_data = await db_manager.get_dashboard_data(session_id)
        return JSONResponse(content=dashboard_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{format}")
async def export_data(
    format: str,
    session_id: str,
    query_id: Optional[str] = None
):
    """Export data in various formats"""
    try:
        if format not in ['csv', 'png', 'pdf']:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        export_result = await query_executor.export_data(format, session_id, query_id)
        
        return FileResponse(
            export_result["file_path"],
            media_type=export_result["media_type"],
            filename=export_result["filename"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = await db_manager.list_sessions()
        return JSONResponse(content={"sessions": sessions})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
