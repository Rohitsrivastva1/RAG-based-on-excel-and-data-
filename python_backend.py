#!/usr/bin/env python3
"""
Python FastAPI backend for RAG Analytics
Simplified version that works with current dependencies
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
from typing import Dict, Any
import uvicorn
from datetime import datetime

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
            "file_path": file_path,
            "created_at": datetime.now().isoformat()
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
    """Process natural language question with basic analytics"""
    try:
        question = question_data.get("question", "")
        session_id = question_data.get("session_id", "")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        df = session["dataframe"]
        
        # Basic analytics based on question keywords
        answer = ""
        data_summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist()
        }
        
        # Simple question analysis
        question_lower = question.lower()
        
        if "average" in question_lower or "mean" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                averages = df[numeric_cols].mean().to_dict()
                answer = f"Average values: {averages}"
            else:
                answer = "No numeric columns found for averaging"
                
        elif "sum" in question_lower or "total" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                sums = df[numeric_cols].sum().to_dict()
                answer = f"Total values: {sums}"
            else:
                answer = "No numeric columns found for summing"
                
        elif "count" in question_lower:
            if "unique" in question_lower:
                unique_counts = df.nunique().to_dict()
                answer = f"Unique value counts: {unique_counts}"
            else:
                answer = f"Total count: {len(df)} rows"
                
        elif "types" in question_lower or "categories" in question_lower or "unique" in question_lower:
            # Handle questions like "types of category we have" or "what categories are there"
            text_cols = df.select_dtypes(include=['object']).columns
            
            if len(text_cols) > 0:
                # Find the column mentioned in the question
                target_col = None
                for col in text_cols:
                    if col.lower() in question_lower:
                        target_col = col
                        break
                
                if target_col is None:
                    target_col = text_cols[0]  # Use first text column
                
                unique_values = df[target_col].unique().tolist()
                unique_counts = df[target_col].value_counts().to_dict()
                
                answer = f"Unique {target_col} types: {unique_values} (Count: {len(unique_values)})"
                data_summary["unique_values"] = unique_values
                data_summary["value_counts"] = unique_counts
            else:
                answer = "No text columns found for category analysis"
                
        elif "maximum" in question_lower or "max" in question_lower or "highest" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Find the column mentioned in the question
                target_col = None
                for col in numeric_cols:
                    if col.lower() in question_lower:
                        target_col = col
                        break
                
                if target_col is None:
                    target_col = numeric_cols[0]  # Use first numeric column
                
                max_value = df[target_col].max()
                max_row = df[df[target_col] == max_value].iloc[0]
                answer = f"Maximum {target_col}: {max_value} (by {max_row.get('name', 'Unknown')})"
                data_summary["max_data"] = max_row.to_dict()
            else:
                answer = "No numeric columns found for maximum calculation"
                
        elif "minimum" in question_lower or "min" in question_lower or "lowest" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Find the column mentioned in the question
                target_col = None
                for col in numeric_cols:
                    if col.lower() in question_lower:
                        target_col = col
                        break
                
                if target_col is None:
                    target_col = numeric_cols[0]  # Use first numeric column
                
                min_value = df[target_col].min()
                min_row = df[df[target_col] == min_value].iloc[0]
                answer = f"Minimum {target_col}: {min_value} (by {min_row.get('name', 'Unknown')})"
                data_summary["min_data"] = min_row.to_dict()
            else:
                answer = "No numeric columns found for minimum calculation"
                
        elif "top" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Get top 5 rows by the first numeric column
                top_col = numeric_cols[0]
                top_data = df.nlargest(5, top_col)
                answer = f"Top 5 rows by {top_col}:"
                data_summary["top_data"] = top_data.to_dict('records')
            else:
                answer = "No numeric columns found for ranking"
                
        elif "describe" in question_lower or "summary" in question_lower:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                description = df[numeric_cols].describe().to_dict()
                answer = f"Statistical summary: {description}"
            else:
                answer = "No numeric columns found for statistical summary"
                
        elif "group" in question_lower or "by" in question_lower:
            # Handle grouping questions like "group by department" or "sales by region"
            text_cols = df.select_dtypes(include=['object']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(text_cols) > 0 and len(numeric_cols) > 0:
                # Find the group column mentioned in the question
                group_col = None
                for col in text_cols:
                    if col.lower() in question_lower:
                        group_col = col
                        break
                
                if group_col is None:
                    group_col = text_cols[0]  # Use first text column
                
                # Find the numeric column to aggregate
                agg_col = None
                for col in numeric_cols:
                    if col.lower() in question_lower:
                        agg_col = col
                        break
                
                if agg_col is None:
                    agg_col = numeric_cols[0]  # Use first numeric column
                
                grouped = df.groupby(group_col)[agg_col].agg(['sum', 'mean', 'count']).round(2)
                answer = f"Grouped by {group_col} - {agg_col} statistics:"
                data_summary["grouped_data"] = grouped.to_dict('index')
            else:
                answer = "Need both text and numeric columns for grouping analysis"
                
        else:
            # Default response
            answer = f"Processed question: '{question}' on dataset with {len(df)} rows and {len(df.columns)} columns. Available columns: {', '.join(df.columns.tolist())}"
        
        # Clean data for JSON serialization (handle NaN values)
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, float) and (obj != obj):  # Check for NaN
                return None
            elif isinstance(obj, (int, float)) and (obj == float('inf') or obj == float('-inf')):
                return None
            else:
                return obj
        
        # Create response
        response = {
            "question": question,
            "answer": answer,
            "data": {
                "summary": clean_for_json(data_summary)
            },
            "visualization": {
                "type": "table",
                "data": clean_for_json(df.head(10).to_dict('records'))
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
    print("🚀 Starting Python RAG Analytics Backend")
    print("==========================================")
    print("Backend will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
