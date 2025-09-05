"""
Pydantic models and common typing interfaces for the RAG Analytics system.
Provides type safety and validation for all API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class DataSource(str, Enum):
    """Enum for data source types."""
    FILE = "file"
    DATABASE = "database"


class QueryType(str, Enum):
    """Enum for query types."""
    LLM_AGENT = "llm_agent"
    PANDAS = "pandas"
    SQL = "sql"
    DATABASE_ERROR = "database_error"


class ChartType(str, Enum):
    """Enum for chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    TABLE = "table"


class IndexStatus(str, Enum):
    """Enum for index status."""
    PENDING = "pending"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Models
class UploadRequest(BaseModel):
    """Request model for file upload."""
    session_id: Optional[str] = Field(None, description="Optional session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "optional-session-id"
            }
        }


class AskQuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    session_id: str = Field(..., description="Session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the total revenue by category?",
                "session_id": "session-123"
            }
        }


class DatabaseConnectionRequest(BaseModel):
    """Request model for database connection."""
    db_type: str = Field(..., description="Database type (postgresql, mysql)")
    host: str = Field(..., description="Database host")
    port: int = Field(..., ge=1, le=65535, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    session_id: Optional[str] = Field(None, description="Optional session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "db_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "mydb",
                "username": "user",
                "password": "password",
                "session_id": "optional-session-id"
            }
        }


# Response Models
class FileInfo(BaseModel):
    """File information model."""
    name: str = Field(..., description="File name")
    rows: int = Field(..., ge=0, description="Number of rows")
    columns: int = Field(..., ge=0, description="Number of columns")
    column_names: List[str] = Field(..., description="Column names")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "sales_data.xlsx",
                "rows": 1000,
                "columns": 5,
                "column_names": ["Date", "Category", "Revenue", "Users", "Growth_%"],
                "size_bytes": 50000
            }
        }


class DataPreview(BaseModel):
    """Data preview model."""
    rows: List[Dict[str, Any]] = Field(..., description="Preview rows")
    total_rows: int = Field(..., ge=0, description="Total number of rows")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rows": [
                    {"Date": "2023-01-01", "Category": "Education", "Revenue": 1000},
                    {"Date": "2023-01-02", "Category": "Entertainment", "Revenue": 1500}
                ],
                "total_rows": 1000
            }
        }


class UploadResponse(BaseModel):
    """Response model for file upload."""
    success: bool = Field(..., description="Upload success status")
    session_id: str = Field(..., description="Session ID")
    file_info: FileInfo = Field(..., description="File information")
    data_preview: DataPreview = Field(..., description="Data preview")
    index_status: IndexStatus = Field(..., description="Index building status")
    message: Optional[str] = Field(None, description="Additional message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "session-123",
                "file_info": {
                    "name": "sales_data.xlsx",
                    "rows": 1000,
                    "columns": 5,
                    "column_names": ["Date", "Category", "Revenue", "Users", "Growth_%"]
                },
                "data_preview": {
                    "rows": [{"Date": "2023-01-01", "Category": "Education", "Revenue": 1000}],
                    "total_rows": 1000
                },
                "index_status": "completed",
                "message": "File uploaded successfully"
            }
        }


class VisualizationData(BaseModel):
    """Visualization data model."""
    type: ChartType = Field(..., description="Chart type")
    data: Dict[str, Any] = Field(..., description="Chart data")
    title: Optional[str] = Field(None, description="Chart title")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "bar",
                "data": {
                    "x": ["Education", "Entertainment", "Finance"],
                    "y": [1000, 1500, 1200],
                    "title": "Revenue by Category"
                },
                "title": "Revenue by Category"
            }
        }


class DataSummary(BaseModel):
    """Data summary model."""
    rows: int = Field(..., ge=0, description="Number of rows")
    columns: int = Field(..., ge=0, description="Number of columns")
    column_names: List[str] = Field(..., description="Column names")
    data_types: Optional[Dict[str, str]] = Field(None, description="Column data types")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rows": 1000,
                "columns": 5,
                "column_names": ["Date", "Category", "Revenue", "Users", "Growth_%"],
                "data_types": {
                    "Date": "datetime64[ns]",
                    "Category": "object",
                    "Revenue": "float64",
                    "Users": "int64",
                    "Growth_%": "float64"
                }
            }
        }


class QueryData(BaseModel):
    """Query data model."""
    summary: DataSummary = Field(..., description="Data summary")
    context: str = Field(..., description="Query context")
    generated_code: Optional[str] = Field(None, description="Generated code")
    sql_query: Optional[str] = Field(None, description="SQL query")
    row_count: Optional[int] = Field(None, description="Number of rows returned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "rows": 1000,
                    "columns": 5,
                    "column_names": ["Date", "Category", "Revenue", "Users", "Growth_%"]
                },
                "context": "Excel file analysis for session session-123",
                "generated_code": "df.groupby('Category')['Revenue'].sum()",
                "sql_query": None,
                "row_count": 5
            }
        }


class AskResponse(BaseModel):
    """Response model for asking questions."""
    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="The answer")
    query_type: QueryType = Field(..., description="Type of query executed")
    data: QueryData = Field(..., description="Query data")
    visualization: Optional[VisualizationData] = Field(None, description="Visualization data")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration_ms: Optional[float] = Field(None, description="Query duration in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the total revenue by category?",
                "answer": "The total revenue by category is: Education: $50,000, Entertainment: $75,000",
                "query_type": "llm_agent",
                "data": {
                    "summary": {
                        "rows": 1000,
                        "columns": 5,
                        "column_names": ["Date", "Category", "Revenue", "Users", "Growth_%"]
                    },
                    "context": "Excel file analysis for session session-123"
                },
                "visualization": {
                    "type": "bar",
                    "data": {
                        "x": ["Education", "Entertainment"],
                        "y": [50000, 75000],
                        "title": "Revenue by Category"
                    }
                },
                "session_id": "session-123",
                "timestamp": "2023-01-01T12:00:00Z",
                "duration_ms": 1500.5
            }
        }


class IndexInfo(BaseModel):
    """Index information model."""
    enabled: bool = Field(..., description="Whether indexing is enabled")
    document_count: int = Field(..., ge=0, description="Number of documents indexed")
    embedding_model: Optional[str] = Field(None, description="Embedding model used")
    index_size_mb: Optional[float] = Field(None, description="Index size in MB")
    created_at: Optional[datetime] = Field(None, description="Index creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "document_count": 1000,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "index_size_mb": 15.5,
                "created_at": "2023-01-01T12:00:00Z"
            }
        }


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str = Field(..., description="Session ID")
    data_source: DataSource = Field(..., description="Data source type")
    index_info: IndexInfo = Field(..., description="Index information")
    created_at: datetime = Field(..., description="Session creation time")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    file_name: Optional[str] = Field(None, description="File name (for file sessions)")
    database_info: Optional[Dict[str, Any]] = Field(None, description="Database info (for DB sessions)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "data_source": "file",
                "index_info": {
                    "enabled": True,
                    "document_count": 1000,
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
                },
                "created_at": "2023-01-01T12:00:00Z",
                "last_accessed": "2023-01-01T12:30:00Z",
                "file_name": "sales_data.xlsx"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    features: Dict[str, bool] = Field(..., description="Feature availability")
    timestamp: datetime = Field(..., description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "RAG Analytics API is running",
                "version": "1.0.0",
                "features": {
                    "excel_upload": True,
                    "llm_queries": True,
                    "visualizations": True,
                    "database_connections": False
                },
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "question", "issue": "too short"},
                "request_id": "req-123",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }


# Internal Models
class Document(BaseModel):
    """Document model for embedding storage."""
    text: str = Field(..., description="Document text")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    embedding: Optional[List[float]] = Field(None, description="Document embedding")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Row 1: Education, 1000, 12.5%",
                "metadata": {
                    "row_index": 0,
                    "column": "Category",
                    "session_id": "session-123"
                },
                "embedding": [0.1, 0.2, 0.3, ...]
            }
        }


class QueryResult(BaseModel):
    """Query result model."""
    documents: List[Document] = Field(..., description="Retrieved documents")
    scores: List[float] = Field(..., description="Relevance scores")
    total_found: int = Field(..., description="Total documents found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "text": "Row 1: Education, 1000, 12.5%",
                        "metadata": {"row_index": 0, "column": "Category"}
                    }
                ],
                "scores": [0.95],
                "total_found": 1
            }
        }


# Validation functions
def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """Validate file size is within limits."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def validate_question_length(question: str) -> bool:
    """Validate question length."""
    return 1 <= len(question) <= 1000


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format."""
    import re
    pattern = r'^[a-zA-Z0-9\-_]+$'
    return bool(re.match(pattern, session_id)) and len(session_id) <= 100
