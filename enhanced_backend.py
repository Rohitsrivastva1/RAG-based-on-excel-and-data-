"""
Enhanced RAG Analytics Backend with LLM-powered queries
Integrates LlamaIndex, LangChain, FAISS, and dynamic visualizations
"""

import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime
import io

# Import our custom modules
from backend.embeddings import embedding_manager
from backend.llm_agent import llm_agent
from backend.database_manager import db_manager

from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced RAG Analytics API",
    description="LLM-powered data analytics with RAG, LangChain, and dynamic visualizations",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for sessions
sessions = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Enhanced RAG Analytics API is running",
        "version": "2.0.0",
        "features": [
            "LLM-powered queries",
            "FAISS vector indexing",
            "LangChain agents",
            "Dynamic visualizations",
            "Database connections"
        ]
    }

@app.get("/sessions")
async def get_sessions():
    """Get all active sessions"""
    return {
        "sessions": list(sessions.keys()),
        "count": len(sessions)
    }

@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...), session_id: str = Form(None)):
    """Upload Excel/CSV file and build vector index"""
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Determine file type and read with pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Clean data
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.fillna('')  # Fill NaN values
        
        # Store session data
        sessions[session_id] = {
            "data": df,
            "file_name": file.filename,
            "upload_time": datetime.now().isoformat(),
            "data_source": "file"
        }
        
        # Build vector index
        index_built = embedding_manager.build_index(df, session_id)
        
        # Get session info
        session_info = embedding_manager.get_session_info(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "file_info": {
                "name": file.filename,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            },
            "index_info": {
                "built": index_built,
                "document_count": session_info["document_count"],
                "embedding_model": session_info["embedding_model"]
            },
            "data_preview": df.head(5).to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/connect_database")
async def connect_database(
    db_type: str = Form(...),
    host: str = Form(...),
    port: int = Form(...),
    database: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    session_id: str = Form(None)
):
    """Connect to a database"""
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Connect to database
        success = False
        if db_type.lower() == "postgresql":
            success = db_manager.connect_postgresql(host, port, database, username, password, session_id)
        elif db_type.lower() == "mysql":
            success = db_manager.connect_mysql(host, port, database, username, password, session_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported database type")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        # Get schema information
        schema_info = db_manager.get_schema_info(session_id)
        
        # Store session data
        sessions[session_id] = {
            "db_type": db_type,
            "host": host,
            "database": database,
            "connection_time": datetime.now().isoformat(),
            "data_source": "database",
            "schema_info": schema_info
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "connection_info": {
                "type": db_type,
                "host": host,
                "database": database
            },
            "schema_info": schema_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")

@app.post("/ask_question")
async def ask_question(
    question: str = Form(...),
    session_id: str = Form(...)
):
    """Process natural language question with LLM agent"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Get context from vector index
        context = embedding_manager.get_context_for_query(session_id, question)
        
        if session["data_source"] == "file":
            # Process with file data
            df = session["data"]
            try:
                result = llm_agent.process_with_agent(df, question, context)
            except RuntimeError as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"LLM processing failed: {str(e)}"
                )
            
        elif session["data_source"] == "database":
            # Process with database
            schema_info = session["schema_info"]
            
            # Generate SQL query
            sql_query = db_manager.generate_sql_from_natural_language(question, schema_info)
            
            # Execute query
            query_result = db_manager.execute_query(session_id, sql_query)
            
            if "error" in query_result:
                result = {
                    "answer": f"Database query error: {query_result['error']}",
                    "query_type": "database_error",
                    "visualization": None
                }
            else:
                # Convert to DataFrame for visualization
                df = query_result["data"]
                
                # Process with LLM agent
                try:
                    result = llm_agent.process_with_agent(df, question, context)
                    result["sql_query"] = sql_query
                    result["row_count"] = query_result["row_count"]
                except RuntimeError as e:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"LLM processing failed: {str(e)}"
                    )
        
        else:
            raise HTTPException(status_code=400, detail="Unknown data source")
        
        # Clean data for JSON serialization
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        # Create response
        response = {
            "question": question,
            "answer": result.get("answer", "No answer generated"),
            "query_type": result.get("query_type", "unknown"),
            "data": {
                "summary": clean_for_json(result.get("data", {})),
                "context": context
            },
            "visualization": clean_for_json(result.get("visualization", None)),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add database-specific fields
        if session["data_source"] == "database":
            response["sql_query"] = result.get("sql_query", "")
            response["row_count"] = result.get("row_count", 0)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/session/{session_id}/info")
async def get_session_info(session_id: str):
    """Get detailed session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    index_info = embedding_manager.get_session_info(session_id)
    
    return {
        "session_id": session_id,
        "data_source": session["data_source"],
        "index_info": index_info,
        "session_data": session
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clean up resources"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up resources
    embedding_manager.clear_session(session_id)
    db_manager.close_connection(session_id)
    
    # Remove session
    del sessions[session_id]
    
    return {"message": f"Session {session_id} deleted successfully"}

@app.get("/database/{session_id}/tables")
async def get_database_tables(session_id: str):
    """Get list of tables in connected database"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["data_source"] != "database":
        raise HTTPException(status_code=400, detail="Session is not connected to a database")
    
    schema_info = db_manager.get_schema_info(session_id)
    return schema_info

@app.get("/database/{session_id}/table/{table_name}")
async def get_table_data(session_id: str, table_name: str, limit: int = 10):
    """Get sample data from a specific table"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = db_manager.get_sample_data(session_id, table_name, limit)
    return result

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced RAG Analytics Backend")
    print("=" * 50)
    print("Features:")
    print("✅ LLM-powered queries with LangChain")
    print("✅ FAISS vector indexing with LlamaIndex")
    print("✅ Dynamic database connections")
    print("✅ Intelligent visualizations")
    print("✅ RAG-based context retrieval")
    print("=" * 50)
    print("⚠️  REQUIRES API KEY:")
    print("   Set GOOGLE_API_KEY or OPENAI_API_KEY environment variable")
    print("   Get Gemini API key: https://makersuite.google.com/app/apikey")
    print("   Get OpenAI API key: https://platform.openai.com/account/api-keys")
    print("=" * 50)
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
