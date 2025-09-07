"""
Main FastAPI application with orchestration pattern.
Implements the complete RAG Analytics system according to the architecture specification.
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import json

# Import our modules
try:
    from .settings import settings
    from .logging_config import setup_logging, get_logger, LogContext, generate_request_id
    from .utils.types import (
        UploadResponse, AskResponse, HealthResponse, ErrorResponse,
        FileInfo, DataPreview, DataSummary, QueryData, VisualizationData,
        DataSource, QueryType, IndexStatus
    )
    from .utils.serializer import clean_for_json, create_query_response, custom_json_encoder
    from .utils.security import sanitize_input

    # Import managers and agents
    from .managers.session_store import initialize_session_store, get_session_store
    from .managers.embedding_manager import initialize_embedding_manager, get_embedding_manager
    from .managers.database_manager import initialize_database_manager, get_database_manager
    from .agents.llm_agent import initialize_llm_agent, get_llm_agent
    from .agents.ai_processor import initialize_ai_processor, get_ai_processor
    from .viz.visualization import initialize_visualization_engine, get_visualization_engine
except ImportError:
    # Fallback for direct execution
    from settings import settings
    from logging_config import setup_logging, get_logger, LogContext, generate_request_id
    from utils.types import (
        UploadResponse, AskResponse, HealthResponse, ErrorResponse,
        FileInfo, DataPreview, DataSummary, QueryData, VisualizationData,
        DataSource, QueryType, IndexStatus
    )
    from utils.serializer import clean_for_json, create_query_response, custom_json_encoder
    from utils.security import sanitize_input

    # Import managers and agents
    from managers.session_store import initialize_session_store, get_session_store
    from managers.embedding_manager import initialize_embedding_manager, get_embedding_manager
    from managers.database_manager import initialize_database_manager, get_database_manager
    from agents.llm_agent import initialize_llm_agent, get_llm_agent
    from agents.ai_processor import initialize_ai_processor, get_ai_processor
    from viz.visualization import initialize_visualization_engine, get_visualization_engine

logger = get_logger(__name__)

# Custom JSONResponse that uses our custom encoder
class CustomJSONResponse(JSONResponse):
    """Custom JSONResponse that handles numpy dtypes and datetime objects."""
    
    def render(self, content: Any) -> bytes:
        """Render content using our custom encoder."""
        try:
            # Use our custom encoder for problematic types
            cleaned_content = jsonable_encoder(content, custom_encoder=custom_json_encoder)
            return json.dumps(
                cleaned_content,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")
        except Exception as e:
            logger.error(f"JSON serialization error: {e}")
            # Fallback to string representation
            return json.dumps(
                {"error": "Serialization failed", "message": str(e)},
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")

# Simple file validation function
def validate_file_size(file_size_bytes: int, max_size_mb: int) -> bool:
    """Validate file size against maximum allowed size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG Analytics API")
    
    # Initialize all components
    try:
        # Initialize session store
        session_store = initialize_session_store(
            redis_url=settings.redis_url,
            max_sessions=1000,
            session_ttl_hours=24
        )
        
        # Initialize embedding manager
        embedding_manager = initialize_embedding_manager()
        
        # Initialize database manager
        database_manager = initialize_database_manager()
        
        # Initialize LLM agent - MANDATORY
        llm_agent = initialize_llm_agent()
        if not llm_agent.is_available():
            raise RuntimeError("LLM agent initialization failed. LlamaIndex and LangChain are required.")
        
        # Initialize AI processor
        ai_processor = initialize_ai_processor()
        
        # Initialize visualization engine
        visualization_engine = initialize_visualization_engine()
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Analytics API")


# Create FastAPI app
app = FastAPI(
    title="RAG Analytics API",
    description="LLM-powered data analytics with RAG, embeddings, and dynamic visualizations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request, call_next):
    """Add request ID to all requests."""
    request_id = generate_request_id()
    
    with LogContext(request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check component availability
        session_store = get_session_store()
        embedding_manager = get_embedding_manager()
        database_manager = get_database_manager()
        llm_agent = get_llm_agent()
        ai_processor = get_ai_processor()
        visualization_engine = get_visualization_engine()
        
        # MANDATORY: LLM agent must be available
        if not llm_agent.is_available():
            return HealthResponse(
                status="unhealthy",
                message="LLM agent not available. LlamaIndex and LangChain are required.",
                version="1.0.0",
                features={},
                timestamp=datetime.utcnow()
            )
        
        features = {
            "excel_upload": True,
            "llm_queries": True,  # Always true since we check availability above
            "embeddings": embedding_manager.embeddings is not None,
            "database_connections": True,
            "visualizations": True,
            "ai_processing": True
        }
        
        return HealthResponse(
            status="healthy",
            message="RAG Analytics API is running",
            version="1.0.0",
            features=features,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            version="1.0.0",
            features={},
            timestamp=datetime.utcnow()
        )


# Upload Excel file endpoint
@app.post("/upload_excel", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload Excel/CSV file and build vector index."""
    print(f"\n📁 UPLOAD EXCEL ENDPOINT")
    print(f"   Filename: {file.filename}")
    print(f"   Content type: {file.content_type}")
    print(f"   Session ID provided: {session_id}")
    
    try:
        with LogContext():
            # Validate file
            if not file.filename:
                print(f"   ❌ No file provided")
                raise HTTPException(status_code=400, detail="No file provided")
            
            print(f"   ✅ File provided: {file.filename}")
            
            # Check file size
            print(f"   📏 Reading file content...")
            content = await file.read()
            file_size_mb = len(content) / (1024 * 1024)
            print(f"   📏 File size: {file_size_mb:.2f} MB")
            
            if not validate_file_size(len(content), settings.max_file_size_mb):
                print(f"   ❌ File too large: {file_size_mb:.2f} MB > {settings.max_file_size_mb} MB")
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
                )
            
            print(f"   ✅ File size validation passed")
            
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
                print(f"   🆔 Generated new session ID: {session_id}")
            else:
                print(f"   🆔 Using provided session ID: {session_id}")
            
            # Read file with pandas
            print(f"   📊 Reading file with pandas...")
            if file.filename.endswith('.csv'):
                print(f"   📄 Detected CSV file")
                df = pd.read_csv(pd.io.common.BytesIO(content))
            elif file.filename.endswith(('.xlsx', '.xls')):
                print(f"   📊 Detected Excel file")
                df = pd.read_excel(pd.io.common.BytesIO(content))
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Use CSV or Excel."
                )
            
            # Clean data
            df = df.dropna(how='all').fillna('')
            
            # Check row limit
            if len(df) > settings.max_rows_indexable:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too many rows. Maximum: {settings.max_rows_indexable}"
                )
            
            # Store session
            session_store = get_session_store()
            session_store.create(
                session_id=session_id,
                data=df,
                data_source=DataSource.FILE.value,
                metadata={
                    "file_name": file.filename,
                    "file_size": len(content),
                    "upload_time": datetime.utcnow().isoformat()
                }
            )
            
            # Build index in background if enabled
            index_status = IndexStatus.COMPLETED
            if settings.enable_embeddings and settings.enable_background_indexing:
                background_tasks.add_task(build_index_background, session_id, df)
                index_status = IndexStatus.BUILDING
            
            # Create response
            file_info = FileInfo(
                name=file.filename,
                rows=len(df),
                columns=len(df.columns),
                column_names=df.columns.tolist(),
                size_bytes=len(content)
            )
            
            data_preview = DataPreview(
                rows=df.head(5).to_dict('records'),
                total_rows=len(df)
            )
            
            return UploadResponse(
                success=True,
                session_id=session_id,
                file_info=file_info,
                data_preview=data_preview,
                index_status=index_status,
                message="File uploaded successfully"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def build_index_background(session_id: str, df: pd.DataFrame):
    """Build index in background task."""
    try:
        with LogContext():
            embedding_manager = get_embedding_manager()
            success = embedding_manager.build_index(df, session_id)
            
            if success:
                logger.info(f"Background index building completed for session {session_id}")
            else:
                logger.warning(f"Background index building failed for session {session_id}")
                
    except Exception as e:
        logger.error(f"Background index building error: {e}")


# Ask question endpoint
@app.post("/ask_question", response_model=AskResponse)
async def ask_question(
    question: str = Form(...),
    session_id: str = Form(...)
):
    """Process natural language question with data."""
    print(f"\n🎯 ASK QUESTION ENDPOINT")
    print(f"   Question: '{question}'")
    print(f"   Session ID: {session_id}")
    
    try:
        with LogContext():
            # Sanitize input
            question = sanitize_input(question)
            print(f"   Sanitized question: '{question}'")
            
            # Get session
            print(f"🔍 Getting session data...")
            session_store = get_session_store()
            session_data = session_store.get(session_id)
            
            if not session_data:
                print(f"   ❌ Session not found: {session_id}")
                raise HTTPException(status_code=404, detail="Session not found")
            
            print(f"   ✅ Session found:")
            print(f"     - Data source: {session_data.data_source}")
            print(f"     - Data type: {type(session_data.data)}")
            print(f"     - Data shape: {session_data.data.shape if hasattr(session_data.data, 'shape') else 'N/A'}")
            
            # Process based on data source
            if session_data.data_source == DataSource.FILE.value:
                print(f"📁 Processing FILE data source")
                print(f"   DataFrame info:")
                print(f"     - Shape: {session_data.data.shape}")
                print(f"     - Columns: {list(session_data.data.columns)}")
                print(f"     - Data types: {dict(session_data.data.dtypes)}")
                
                result = await process_file_question(question, session_id, session_data.data)
                
            elif session_data.data_source == DataSource.DATABASE.value:
                print(f"🗄️ Processing DATABASE data source")
                result = await process_database_question(question, session_id)
            else:
                print(f"   ❌ Unknown data source: {session_data.data_source}")
                raise HTTPException(status_code=400, detail="Unknown data source")
            
            print(f"✅ ASK QUESTION COMPLETE")
            print(f"   Result type: {type(result)}")
            print(f"   Result question: {result.question}")
            print(f"   Result answer preview: {str(result.answer)[:100]}...")
            
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")


async def process_file_question(
    question: str,
    session_id: str,
    df: pd.DataFrame
) -> AskResponse:
    """Process question for file data."""
    print(f"\n🚀 PROCESSING FILE QUESTION")
    print(f"   Question: '{question}'")
    print(f"   Session ID: {session_id}")
    print(f"   DataFrame shape: {df.shape}")
    print(f"   DataFrame columns: {list(df.columns)}")
    
    try:
        start_time = datetime.utcnow()
        print(f"   Start time: {start_time}")
        print(f"   Embeddings enabled: {settings.enable_embeddings}")
        # Get relevant context using embeddings
        print(f"🔍 Getting context from embeddings...")
        context = ""
        if settings.enable_embeddings:
            embedding_manager = get_embedding_manager()
            print(f"   Embedding manager: {embedding_manager}")
            docs = embedding_manager.query_index(session_id, question, settings.top_k)
            print(f"   Retrieved {len(docs) if docs else 0} documents")
            if docs:
                context_parts = []
                for doc in docs:
                    context_parts.append(doc['text'])
                context = "\n".join(context_parts)
                print(f"   Context length: {len(context)} characters")
                print(f"   Context preview: {context[:200]}...")
            else:
                print(f"   No context documents found")
        else:
            print(f"   Embeddings disabled, skipping context retrieval")
        
        # Process with LLM agent if available
        print(f"🤖 Processing with LLM agent...")
        try:
            llm_agent = get_llm_agent()
            print(f"   LLM agent: {llm_agent}")
            if not llm_agent.is_available():
                print(f"   ❌ LLM agent not available")
                raise HTTPException(
                    status_code=503, 
                    detail="LLM agent not available. LlamaIndex and LangChain are required for this system."
                )
            
            print(f"   ✅ LLM agent available, processing...")
            logger.info(f"Using LLM agent for question: {question}")
            agent_result = llm_agent.process_with_agent(df, question, context)
            
            print(f"   Agent result received:")
            print(f"   - Success: {agent_result['success']}")
            print(f"   - Query type: {agent_result['query_type']}")
            print(f"   - Answer type: {type(agent_result['answer'])}")
            print(f"   - Answer preview: {str(agent_result['answer'])[:200]}...")
            print(f"   - Visualization: {agent_result.get('visualization')}")
            print(f"   - Generated code: {agent_result.get('generated_code')}")
            
            if not agent_result['success']:
                print(f"   ❌ Agent processing failed")
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM agent processing failed: {agent_result.get('error', 'Unknown error')}"
                )
            
            if agent_result['success']:
                duration = (datetime.utcnow() - start_time).total_seconds()
                print(f"   ⏱️ Total processing duration: {duration:.2f} seconds")
                print(f"   📊 DataFrame info:")
                print(f"     - Rows: {len(df)}")
                print(f"     - Columns: {len(df.columns)}")
                print(f"     - Column names: {list(df.columns)}")
                print(f"   📤 Response details:")
                print(f"     - Answer: {str(agent_result['answer'])[:100]}...")
                print(f"     - Query type: {agent_result['query_type']}")
                print(f"     - Generated code: {agent_result.get('generated_code')}")
                print(f"     - Visualization: {agent_result.get('visualization')}")
                print(f"     - Session ID: {session_id}")
                print(f"     - Duration: {duration * 1000:.2f}ms")
                
                return AskResponse(
                        question=question,
                        answer=agent_result['answer'],
                        query_type=agent_result['query_type'],
                        data=QueryData(
                            summary=DataSummary(
                                rows=len(df),
                                columns=len(df.columns),
                                column_names=df.columns.tolist(),
                                data_types={col: str(dtype) for col, dtype in df.dtypes.to_dict().items()}
                            ),
                            context=context,
                            generated_code=agent_result.get('generated_code'),
                            row_count=len(df)
                        ),
                   
                        visualization=agent_result.get('visualization'),
                        session_id=session_id,
                        timestamp=datetime.utcnow(),
                        duration_ms=duration * 1000
                    )
        except Exception as e:
            print("Exception")
            print(e)
            raise HTTPException(
                status_code=500,
                detail=f"LLM agent processing failed: {str(e)}"
            )
        
    except Exception as e:
        logger.error(f"File question processing failed: {e}")
        raise


async def process_database_question(question: str, session_id: str) -> AskResponse:
    """Process question for database data."""
    try:
        # This would implement database query processing
        # For now, return a placeholder
        raise HTTPException(status_code=501, detail="Database processing not implemented yet")
        
    except Exception as e:
        logger.error(f"Database question processing failed: {e}")
        raise


# REMOVED: Simple processing function - LLM agent is now mandatory


# Session management endpoints
@app.get("/sessions")
async def get_sessions():
    """Get all active sessions."""
    try:
        session_store = get_session_store()
        sessions = session_store.list_sessions()
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")


@app.get("/session/{session_id}/info")
async def get_session_info(session_id: str):
    """Get detailed session information."""
    try:
        session_store = get_session_store()
        session_info = session_store.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session info")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clean up resources."""
    try:
        session_store = get_session_store()
        embedding_manager = get_embedding_manager()
        database_manager = get_database_manager()
        
        # Clean up resources
        embedding_manager.clear_session(session_id)
        database_manager.close_connection(session_id)
        
        # Delete session
        success = session_store.delete(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


# Database connection endpoints (stubs for now)
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
    """Connect to a database."""
    raise HTTPException(status_code=501, detail="Database connections not implemented yet")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return CustomJSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="NotFound",
            message="Resource not found",
            request_id=getattr(request.state, 'request_id', None),
            timestamp=datetime.utcnow()
        ).dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return CustomJSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalError",
            message="Internal server error",
            request_id=getattr(request.state, 'request_id', None),
            timestamp=datetime.utcnow()
        ).dict()
    )


# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Setup logging
    setup_logging(
        log_level=settings.log_level,
        log_format=settings.log_format,
        enable_console=True,
        enable_file=True
    )
    
    # Validate configuration
    warnings = settings.validate_configuration()
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    # Start server
    logger.info("Starting RAG Analytics API server")
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
