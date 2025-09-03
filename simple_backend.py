#!/usr/bin/env python3
"""
Simple FastAPI backend for RAG Analytics
This is a minimal version that works without complex dependencies
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import json
import os
from typing import Dict, Any
import uvicorn

app = FastAPI(title="RAG Analytics API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
sessions = {}
uploaded_files = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "RAG Analytics API is running"}

@app.get("/sessions")
async def get_sessions():
    """Get all active sessions"""
    return {"sessions": list(sessions.keys())}

@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload Excel/CSV file and return basic info"""
    try:
        # Read the file
        contents = await file.read()
        
        # Save file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Read with pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Get basic info
        file_info = {
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "sample_data": df.head(5).to_dict('records'),
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
        # Store in memory
        session_id = f"session_{len(sessions) + 1}"
        sessions[session_id] = {
            "type": "file",
            "filename": file.filename,
            "dataframe": df,
            "file_path": file_path
        }
        
        # Clean up temp file
        os.remove(file_path)
        
        return {
            "message": "File uploaded successfully",
            "session_id": session_id,
            "file_info": file_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/ask_question")
async def ask_question(question_data: Dict[str, Any]):
    """Process natural language question"""
    try:
        question = question_data.get("question", "")
        session_id = question_data.get("session_id", "")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        df = session["dataframe"]
        
        # Simple response for demo
        response = {
            "question": question,
            "answer": f"Processed question: '{question}' on dataset with {len(df)} rows and {len(df.columns)} columns",
            "data": {
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "column_names": df.columns.tolist()
                }
            },
            "visualization": {
                "type": "table",
                "data": df.head(10).to_dict('records')
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RAG Analytics API", "version": "1.0.0"}

if __name__ == "__main__":
    print("🚀 Starting Simple RAG Analytics Backend")
    print("==========================================")
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
