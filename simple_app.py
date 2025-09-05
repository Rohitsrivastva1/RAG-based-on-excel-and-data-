"""
Simplified FastAPI application for testing the new architecture.
Works without complex dependencies for basic functionality testing.
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Simple in-memory storage
sessions = {}
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Analytics API (Simple)",
    description="Simplified RAG Analytics for testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "RAG Analytics API is running (Simple Mode)",
        "version": "1.0.0",
        "features": {
            "excel_upload": True,
            "llm_queries": False,
            "embeddings": False,
            "database_connections": False,
            "visualizations": True,
            "ai_processing": False
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Upload Excel file endpoint
@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...), session_id: Optional[str] = Form(None)):
    """Upload Excel/CSV file."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        
        # Read file with pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(pd.io.common.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
        
        # Clean data
        df = df.dropna(how='all').fillna('')
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Store session
        sessions[session_id] = {
            "data": df,
            "metadata": {
                "file_name": file.filename,
                "file_size": len(content),
                "upload_time": datetime.utcnow().isoformat()
            }
        }
        
        # Create response
        file_info = {
            "name": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "size_bytes": len(content)
        }
        
        data_preview = {
            "rows": df.head(5).to_dict('records'),
            "total_rows": len(df)
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "file_info": file_info,
            "data_preview": data_preview,
            "index_status": "completed",
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Ask question endpoint
@app.post("/ask_question")
async def ask_question(question: str = Form(...), session_id: str = Form(...)):
    """Process natural language question with data."""
    try:
        # Get session
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[session_id]
        df = session_data["data"]
        
        # Simple rule-based processing
        question_lower = question.lower()
        
        if 'columns' in question_lower:
            answer = f"The dataset has {len(df.columns)} columns: {', '.join(df.columns.tolist())}"
            query_type = "pandas"
        elif 'first' in question_lower and 'row' in question_lower:
            n_rows = 5 if '5' in question_lower else 3
            answer = f"First {n_rows} rows:\n{df.head(n_rows).to_string()}"
            query_type = "pandas"
        elif 'total' in question_lower or 'sum' in question_lower:
            numeric_cols = df.select_dtypes(include=[pd.api.types.is_numeric_dtype]).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                total = df[col].sum()
                answer = f"Total {col}: {total:,.2f}"
            else:
                answer = "No numeric columns found for calculation"
            query_type = "pandas"
        elif 'category' in question_lower and ('revenue' in question_lower or 'users' in question_lower):
            # Check for visualization keywords
            if 'chart' in question_lower or 'graph' in question_lower or 'bar' in question_lower:
                if 'revenue' in question_lower and 'Category' in df.columns and 'Revenue' in df.columns:
                    grouped = df.groupby('Category')['Revenue'].sum()
                    answer = f"Revenue by category:\n{grouped.to_string()}"
                    visualization = {
                        "type": "bar",
                        "data": {
                            "x": grouped.index.tolist(),
                            "y": grouped.values.tolist(),
                            "title": "Revenue by Category"
                        }
                    }
                elif 'user' in question_lower and 'Category' in df.columns and 'Users' in df.columns:
                    grouped = df.groupby('Category')['Users'].sum()
                    answer = f"Users by category:\n{grouped.to_string()}"
                    visualization = {
                        "type": "bar",
                        "data": {
                            "x": grouped.index.tolist(),
                            "y": grouped.values.tolist(),
                            "title": "Users by Category"
                        }
                    }
                else:
                    answer = "Cannot create chart - missing required columns (Category and Revenue/Users)."
                    visualization = None
            else:
                answer = f"Dataset summary: {len(df)} rows, {len(df.columns)} columns. "
                answer += f"Columns: {', '.join(df.columns.tolist())}"
                visualization = None
            query_type = "pandas"
        else:
            answer = f"Dataset summary: {len(df)} rows, {len(df.columns)} columns. "
            answer += f"Columns: {', '.join(df.columns.tolist())}"
            query_type = "pandas"
            visualization = None
        
        response = {
            "question": question,
            "answer": answer,
            "query_type": query_type,
            "data": {
                "summary": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                    "data_types": df.dtypes.to_dict()
                },
                "context": "Simple processing mode",
                "row_count": len(df)
            },
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if visualization:
            response["visualization"] = visualization
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

# Session management endpoints
@app.get("/sessions")
async def get_sessions():
    """Get all active sessions."""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append({
            "session_id": session_id,
            "metadata": session_data["metadata"],
            "data_shape": str(session_data["data"].shape)
        })
    
    return {"sessions": session_list, "count": len(session_list)}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Starting Simple RAG Analytics API")
    print("=" * 50)
    print("✅ Excel/CSV upload & pandas Q&A")
    print("⛔ LLM, FAISS, DB: disabled in simple mode")
    print("=" * 50)
    print("Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
