"""
Enhanced RAG Analytics Backend (Excel-only mode)
FastAPI + pandas, with graceful stubs for vector index & DB
"""

import os
import io
import uuid
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

# ---- Mode flags ------------------------------------------------------------
LLM_ENABLED = False         # No LLM agent at the moment
VECTOR_INDEX_ENABLED = False
DATABASE_ENABLED = False

# ---- Optional dependencies (disabled path) ---------------------------------
llm_agent = None
print("⚠️ Running in Excel-only mode: LLM/Vectors/DB are disabled.")

from dotenv import load_dotenv
load_dotenv()

# ---- FastAPI app -----------------------------------------------------------
app = FastAPI(
    title="Enhanced RAG Analytics API",
    description="Excel-only analytics (pandas). Vector index & DB routes are stubbed.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- In-memory session store ----------------------------------------------
sessions: Dict[str, Dict[str, Any]] = {}

# ---- Safe JSON cleaner -----------------------------------------------------
def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Handle pandas NA/NaT
    try:
        # pd.isna on scalars; will raise on dict/list so it's in try
        if pd.isna(obj):
            return None
    except Exception:
        pass
    return obj

# ---- Graceful stubs for optional components --------------------------------
class DisabledEmbeddingManager:
    def build_index(self, *_, **__):
        raise RuntimeError("Vector index is disabled in Excel-only mode.")
    def get_session_info(self, *_):
        return {"enabled": False, "document_count": 0, "embedding_model": None}
    def clear_session(self, *_):
        return None

class DisabledDBManager:
    def connect_postgresql(self, *_, **__): return False
    def connect_mysql(self, *_, **__): return False
    def get_schema_info(self, *_): return {"enabled": False, "tables": []}
    def execute_query(self, *_): return {"error": "Database support is disabled."}
    def get_sample_data(self, *_): return {"error": "Database support is disabled."}
    def close_connection(self, *_): return None

embedding_manager = DisabledEmbeddingManager()
db_manager = DisabledDBManager()

# ---- Health & sessions -----------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Enhanced RAG Analytics API is running (Excel-only mode)",
        "version": "2.0.0",
        "features": {
            "excel_upload": True,
            "excel_qna_pandas": True,
            "llm_powered_queries": LLM_ENABLED,
            "faiss_vector_index": VECTOR_INDEX_ENABLED,
            "langchain_agents": LLM_ENABLED,
            "database_connections": DATABASE_ENABLED
        }
    }

@app.get("/sessions")
async def get_sessions():
    return {"sessions": list(sessions.keys()), "count": len(sessions)}

# ---- Upload Excel/CSV ------------------------------------------------------
@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...), session_id: str = Form(None)):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        content = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")

        # Clean up obvious issues
        df = df.dropna(how="all").fillna("")

        sessions[session_id] = {
            "data": df,
            "file_name": file.filename,
            "upload_time": datetime.now().isoformat(),
            "data_source": "file"
        }

        print(f"📊 Stored Excel data for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "file_info": {
                "name": file.filename,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "column_names": list(df.columns)
            },
            "data_preview": clean_for_json(df.head(5).to_dict("records"))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ---- Simple pandas Q&A -----------------------------------------------------
def process_excel_question(question: str, df: pd.DataFrame, session_id: str) -> Dict[str, Any]:
    try:
        q = question.lower()
        visualization = None

        if "column" in q or "columns" in q:
            answer = f"The dataset has {len(df.columns)} columns: {', '.join(map(str, df.columns.tolist()))}"
            query_type = "pandas_agent"

        elif "first" in q and ("row" in q or "5" in q):
            n_rows = 5 if "5" in q else 3
            preview = df.head(n_rows).to_string(index=False)
            answer = f"First {n_rows} rows:\n{preview}"
            query_type = "pandas_agent"

        elif "total" in q and "revenue" in q:
            if "Revenue" in df.columns:
                if "category" in q and "Category" in df.columns:
                    revenue_by_category = df.groupby("Category")["Revenue"].sum()
                    answer = f"Total revenue by category:\n{revenue_by_category.to_string()}"
                else:
                    total_revenue = df["Revenue"].sum()
                    answer = f"Total revenue: ${float(total_revenue):,.2f}"
                query_type = "pandas_agent"
            else:
                answer = "No 'Revenue' column found in the dataset."
                query_type = "pandas_agent"

        elif "average" in q and "growth" in q:
            if "Growth_%" in df.columns:
                avg_growth = df["Growth_%"].astype(float).mean()
                answer = f"Average growth percentage: {float(avg_growth):.2f}%"
                query_type = "pandas_agent"
            else:
                answer = "No 'Growth_%' column found in the dataset."
                query_type = "pandas_agent"

        elif any(k in q for k in ["chart", "graph", "bar"]):
            # Determine which column to use based on the query
            print(f"🔍 Debug: Query = '{q}'")
            print(f"🔍 Debug: Contains 'user' = {'user' in q}")
            print(f"🔍 Debug: Contains 'users' = {'users' in q}")
            print(f"🔍 Debug: Contains 'revenue' = {'revenue' in q}")
            
            if ("user" in q or "users" in q) and "Users" in df.columns and "Category" in df.columns:
                # User requested users by category
                print("🔍 Debug: Using Users column")
                users_by_category = df.groupby("Category")["Users"].sum()
                visualization = {
                    "type": "bar",
                    "data": {
                        "x": users_by_category.index.tolist(),
                        "y": [float(v) for v in users_by_category.values.tolist()],
                        "title": "Users by Category"
                    }
                }
                answer = f"Users by category:\n{users_by_category.to_string()}"
                query_type = "pandas_agent"
            elif "revenue" in q and "Revenue" in df.columns and "Category" in df.columns:
                # User requested revenue by category
                print("🔍 Debug: Using Revenue column")
                revenue_by_category = df.groupby("Category")["Revenue"].sum()
                visualization = {
                    "type": "bar",
                    "data": {
                        "x": revenue_by_category.index.tolist(),
                        "y": [float(v) for v in revenue_by_category.values.tolist()],
                        "title": "Revenue by Category"
                    }
                }
                answer = f"Revenue by category:\n{revenue_by_category.to_string()}"
                query_type = "pandas_agent"
            elif "Revenue" in df.columns and "Category" in df.columns:
                # Default to revenue if no specific column mentioned
                print("🔍 Debug: Using default Revenue column")
                revenue_by_category = df.groupby("Category")["Revenue"].sum()
                visualization = {
                    "type": "bar",
                    "data": {
                        "x": revenue_by_category.index.tolist(),
                        "y": [float(v) for v in revenue_by_category.values.tolist()],
                        "title": "Revenue by Category"
                    }
                }
                answer = f"Revenue by category:\n{revenue_by_category.to_string()}"
                query_type = "pandas_agent"
            else:
                answer = "Cannot create chart - missing required columns (Category and either Revenue or Users)."
                query_type = "pandas_agent"

        elif "unique" in q:
            # Heuristic: if they mention a column name, try to use it; else default to 'Category' if present
            target_col = None
            for col in df.columns:
                if col.lower() in q:
                    target_col = col
                    break
            if target_col is None and "Category" in df.columns:
                target_col = "Category"

            if target_col:
                uniques = pd.Series(df[target_col].unique()).astype(str).tolist()
                answer = f"Unique values in '{target_col}': {', '.join(uniques)}"
                query_type = "pandas_agent"
            else:
                answer = "Please specify which column to get unique values from."
                query_type = "pandas_agent"

        elif "region" in q and "user" in q:
            if "Region" in df.columns and "Users" in df.columns:
                users_by_region = df.groupby("Region")["Users"].sum()
                answer = f"Users by region:\n{users_by_region.to_string()}"
                query_type = "pandas_agent"
            else:
                answer = "Cannot analyze users by region - missing required columns."
                query_type = "pandas_agent"

        elif "top" in q and "category" in q:
            if "Revenue" in df.columns and "Category" in df.columns:
                top_categories = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
                n = 3 if "3" in q else 5
                top_n = top_categories.head(n)
                answer = f"Top {n} categories by revenue:\n{top_n.to_string()}"
                query_type = "pandas_agent"
            else:
                answer = "Cannot find top categories - missing required columns."
                query_type = "pandas_agent"

        else:
            answer = (
                "Dataset summary:\n"
                f"- Rows: {len(df)}\n"
                f"- Columns: {len(df.columns)}\n"
                f"- Column names: {', '.join(map(str, df.columns.tolist()))}"
            )
            query_type = "pandas_agent"

        result = {
            "question": question,
            "answer": answer,
            "query_type": query_type,
            "data": {
                "summary": {
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "column_names": list(map(str, df.columns.tolist()))
                },
                "context": f"Excel file analysis for session {session_id}"
            }
        }
        if visualization:
            result["visualization"] = visualization

        return clean_for_json(result)

    except Exception as e:
        return {
            "question": question,
            "answer": f"Error processing Excel data: {str(e)}",
            "query_type": "pandas_agent",
            "data": {"summary": {}, "context": "Error in Excel data processing"}
        }

@app.post("/ask_question")
async def ask_question(question: str = Form(...), session_id: str = Form(...)):
    """Process natural language question with Excel data (pandas-only)."""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]
        if session.get("data_source") != "file":
            raise HTTPException(status_code=400, detail="This session is not for file data")

        df = session["data"]
        result = process_excel_question(question, df, session_id)

        # Uniform response envelope
        return {
            "question": question,
            "answer": result.get("answer", "No answer generated"),
            "query_type": result.get("query_type", "pandas_agent"),
            "data": result.get("data", {}),
            "visualization": result.get("visualization", None),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# ---- Session info / cleanup ------------------------------------------------
@app.get("/session/{session_id}/info")
async def get_session_info(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    index_info = embedding_manager.get_session_info(session_id) if VECTOR_INDEX_ENABLED else {
        "enabled": False, "document_count": 0, "embedding_model": None
    }

    return {
        "session_id": session_id,
        "data_source": session["data_source"],
        "index_info": index_info,
        "session_data": {
            **{k: v for k, v in session.items() if k != "data"},
            "file_name": session.get("file_name"),
            "upload_time": session.get("upload_time")
        }
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if VECTOR_INDEX_ENABLED:
        embedding_manager.clear_session(session_id)
    if DATABASE_ENABLED:
        db_manager.close_connection(session_id)

    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

# ---- DB routes (disabled) --------------------------------------------------
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
    raise HTTPException(status_code=501, detail="Database support is disabled in Excel-only mode.")

@app.get("/database/{session_id}/tables")
async def get_database_tables(session_id: str):
    raise HTTPException(status_code=501, detail="Database support is disabled in Excel-only mode.")

@app.get("/database/{session_id}/table/{table_name}")
async def get_table_data(session_id: str, table_name: str, limit: int = 10):
    raise HTTPException(status_code=501, detail="Database support is disabled in Excel-only mode.")

# ---- Main ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced RAG Analytics Backend (Excel-only)")
    print("=" * 50)
    print("✅ Excel/CSV upload & pandas Q&A")
    print("⛔ LLM, FAISS, DB: disabled in this build")
    print("=" * 50)
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
