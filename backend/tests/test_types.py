"""
Test Pydantic models and type definitions.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List
from backend.utils.types import (
    FileInfo, UploadResponse, AskResponse, HealthResponse, ErrorResponse,
    DataPreview, DataSummary, QueryData, VisualizationData,
    DataSource, QueryType, IndexStatus, ChartType,
    DBConnectionInfo, DBSchemaInfo, DBConnectResponse,
    SessionInfo, IndexInfo
)


class TestFileInfo:
    """Test FileInfo model."""
    
    def test_file_info_creation(self):
        """Test creating FileInfo instance."""
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1", "col2", "col3", "col4", "col5"],
            size_bytes=1024
        )
        
        assert file_info.name == "test.xlsx"
        assert file_info.rows == 100
        assert file_info.columns == 5
        assert file_info.column_names == ["col1", "col2", "col3", "col4", "col5"]
        assert file_info.size_bytes == 1024
    
    def test_file_info_validation(self):
        """Test FileInfo validation."""
        # Valid data
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            size_bytes=1024
        )
        assert file_info.rows == 100
        
        # Invalid data should raise validation error
        with pytest.raises(ValueError):
            FileInfo(
                name="test.xlsx",
                rows=-1,  # Negative rows should fail
                columns=5,
                column_names=["col1", "col2"],
                size_bytes=1024
            )
    
    def test_file_info_serialization(self):
        """Test FileInfo serialization."""
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            size_bytes=1024
        )
        
        # Test dict conversion
        data = file_info.dict()
        assert data["name"] == "test.xlsx"
        assert data["rows"] == 100
        assert data["columns"] == 5
        assert data["column_names"] == ["col1", "col2"]
        assert data["size_bytes"] == 1024
        
        # Test JSON serialization
        json_data = file_info.json()
        assert "test.xlsx" in json_data
        assert "100" in json_data


class TestUploadResponse:
    """Test UploadResponse model."""
    
    def test_upload_response_creation(self):
        """Test creating UploadResponse instance."""
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            size_bytes=1024
        )
        
        data_preview = DataPreview(
            rows=[{"col1": 1, "col2": 2}],
            total_rows=100
        )
        
        response = UploadResponse(
            success=True,
            session_id="test-session-123",
            file_info=file_info,
            data_preview=data_preview,
            index_status=IndexStatus.COMPLETED,
            message="Upload successful"
        )
        
        assert response.success is True
        assert response.session_id == "test-session-123"
        assert response.file_info.name == "test.xlsx"
        assert response.data_preview.total_rows == 100
        assert response.index_status == IndexStatus.COMPLETED
        assert response.message == "Upload successful"
    
    def test_upload_response_serialization(self):
        """Test UploadResponse serialization."""
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            size_bytes=1024
        )
        
        data_preview = DataPreview(
            rows=[{"col1": 1, "col2": 2}],
            total_rows=100
        )
        
        response = UploadResponse(
            success=True,
            session_id="test-session-123",
            file_info=file_info,
            data_preview=data_preview,
            index_status=IndexStatus.COMPLETED,
            message="Upload successful"
        )
        
        # Test dict conversion
        data = response.dict()
        assert data["success"] is True
        assert data["session_id"] == "test-session-123"
        assert data["index_status"] == "completed"
        
        # Test JSON serialization
        json_data = response.json()
        assert "test-session-123" in json_data
        assert "Upload successful" in json_data


class TestAskResponse:
    """Test AskResponse model."""
    
    def test_ask_response_creation(self):
        """Test creating AskResponse instance."""
        data_summary = DataSummary(
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            data_types={"col1": "int64", "col2": "object"}
        )
        
        query_data = QueryData(
            summary=data_summary,
            context="Test context",
            generated_code="df.head()",
            row_count=100
        )
        
        visualization = VisualizationData(
            chart_type=ChartType.BAR,
            config={"data": {"x": [1, 2, 3], "y": [4, 5, 6]}},
            title="Test Chart"
        )
        
        response = AskResponse(
            question="What is the data?",
            answer="The data shows...",
            query_type=QueryType.PANDAS,
            data=query_data,
            visualization=visualization,
            session_id="test-session-123",
            timestamp=datetime.utcnow(),
            duration_ms=1500.5
        )
        
        assert response.question == "What is the data?"
        assert response.answer == "The data shows..."
        assert response.query_type == QueryType.PANDAS
        assert response.data.summary.rows == 100
        assert response.visualization.chart_type == ChartType.BAR
        assert response.session_id == "test-session-123"
        assert response.duration_ms == 1500.5
    
    def test_ask_response_optional_fields(self):
        """Test AskResponse with optional fields."""
        data_summary = DataSummary(
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            data_types={"col1": "int64", "col2": "object"}
        )
        
        query_data = QueryData(
            summary=data_summary,
            context="Test context"
        )
        
        response = AskResponse(
            question="What is the data?",
            answer="The data shows...",
            query_type=QueryType.PANDAS,
            data=query_data,
            session_id="test-session-123",
            timestamp=datetime.utcnow()
        )
        
        assert response.visualization is None
        assert response.duration_ms is None
        assert response.sql_query is None
        assert response.row_count is None


class TestHealthResponse:
    """Test HealthResponse model."""
    
    def test_health_response_creation(self):
        """Test creating HealthResponse instance."""
        features = {
            "excel_upload": True,
            "llm_queries": True,
            "embeddings": True,
            "database_connections": True,
            "visualizations": True,
            "ai_processing": True
        }
        
        response = HealthResponse(
            status="healthy",
            message="API is running",
            version="1.0.0",
            features=features,
            timestamp=datetime.utcnow()
        )
        
        assert response.status == "healthy"
        assert response.message == "API is running"
        assert response.version == "1.0.0"
        assert response.features["excel_upload"] is True
        assert response.features["llm_queries"] is True
    
    def test_health_response_unhealthy(self):
        """Test HealthResponse for unhealthy status."""
        response = HealthResponse(
            status="unhealthy",
            message="Database connection failed",
            version="1.0.0",
            features={},
            timestamp=datetime.utcnow()
        )
        
        assert response.status == "unhealthy"
        assert response.message == "Database connection failed"
        assert response.features == {}


class TestErrorResponse:
    """Test ErrorResponse model."""
    
    def test_error_response_creation(self):
        """Test creating ErrorResponse instance."""
        response = ErrorResponse(
            error="ValidationError",
            message="Invalid input provided",
            request_id="req-12345",
            timestamp=datetime.utcnow()
        )
        
        assert response.error == "ValidationError"
        assert response.message == "Invalid input provided"
        assert response.request_id == "req-12345"
    
    def test_error_response_optional_fields(self):
        """Test ErrorResponse with optional fields."""
        response = ErrorResponse(
            error="ValidationError",
            message="Invalid input provided"
        )
        
        assert response.request_id is None
        assert response.timestamp is None


class TestDataPreview:
    """Test DataPreview model."""
    
    def test_data_preview_creation(self):
        """Test creating DataPreview instance."""
        rows = [
            {"col1": 1, "col2": "A"},
            {"col1": 2, "col2": "B"},
            {"col1": 3, "col2": "C"}
        ]
        
        preview = DataPreview(
            rows=rows,
            total_rows=1000
        )
        
        assert len(preview.rows) == 3
        assert preview.rows[0]["col1"] == 1
        assert preview.rows[1]["col2"] == "B"
        assert preview.total_rows == 1000


class TestDataSummary:
    """Test DataSummary model."""
    
    def test_data_summary_creation(self):
        """Test creating DataSummary instance."""
        summary = DataSummary(
            rows=1000,
            columns=5,
            column_names=["col1", "col2", "col3", "col4", "col5"],
            data_types={"col1": "int64", "col2": "object", "col3": "float64"}
        )
        
        assert summary.rows == 1000
        assert summary.columns == 5
        assert len(summary.column_names) == 5
        assert summary.data_types["col1"] == "int64"
        assert summary.data_types["col2"] == "object"


class TestQueryData:
    """Test QueryData model."""
    
    def test_query_data_creation(self):
        """Test creating QueryData instance."""
        summary = DataSummary(
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            data_types={"col1": "int64", "col2": "object"}
        )
        
        query_data = QueryData(
            summary=summary,
            context="Test context",
            generated_code="df.head()",
            row_count=100
        )
        
        assert query_data.summary.rows == 100
        assert query_data.context == "Test context"
        assert query_data.generated_code == "df.head()"
        assert query_data.row_count == 100
    
    def test_query_data_optional_fields(self):
        """Test QueryData with optional fields."""
        summary = DataSummary(
            rows=100,
            columns=5,
            column_names=["col1", "col2"],
            data_types={"col1": "int64", "col2": "object"}
        )
        
        query_data = QueryData(summary=summary)
        
        assert query_data.context is None
        assert query_data.generated_code is None
        assert query_data.row_count is None


class TestVisualizationData:
    """Test VisualizationData model."""
    
    def test_visualization_data_creation(self):
        """Test creating VisualizationData instance."""
        config = {
            "data": {
                "x": [1, 2, 3, 4, 5],
                "y": [10, 20, 30, 40, 50]
            },
            "layout": {
                "title": "Test Chart",
                "xaxis": {"title": "X Axis"},
                "yaxis": {"title": "Y Axis"}
            }
        }
        
        viz_data = VisualizationData(
            chart_type=ChartType.BAR,
            config=config,
            title="Test Bar Chart"
        )
        
        assert viz_data.chart_type == ChartType.BAR
        assert viz_data.config["data"]["x"] == [1, 2, 3, 4, 5]
        assert viz_data.title == "Test Bar Chart"
    
    def test_visualization_data_optional_fields(self):
        """Test VisualizationData with optional fields."""
        config = {"data": {"x": [1, 2, 3], "y": [4, 5, 6]}}
        
        viz_data = VisualizationData(
            chart_type=ChartType.LINE,
            config=config
        )
        
        assert viz_data.title is None


class TestEnums:
    """Test enum types."""
    
    def test_data_source_enum(self):
        """Test DataSource enum."""
        assert DataSource.FILE.value == "file"
        assert DataSource.DATABASE.value == "database"
    
    def test_query_type_enum(self):
        """Test QueryType enum."""
        assert QueryType.PANDAS.value == "pandas"
        assert QueryType.LLM_AGENT.value == "llm_agent"
        assert QueryType.DATABASE.value == "database"
    
    def test_index_status_enum(self):
        """Test IndexStatus enum."""
        assert IndexStatus.BUILDING.value == "building"
        assert IndexStatus.COMPLETED.value == "completed"
        assert IndexStatus.FAILED.value == "failed"
        assert IndexStatus.DISABLED.value == "disabled"
    
    def test_chart_type_enum(self):
        """Test ChartType enum."""
        assert ChartType.BAR.value == "bar"
        assert ChartType.LINE.value == "line"
        assert ChartType.PIE.value == "pie"
        assert ChartType.SCATTER.value == "scatter"
        assert ChartType.HEATMAP.value == "heatmap"
        assert ChartType.TABLE.value == "table"


class TestDatabaseTypes:
    """Test database-related types."""
    
    def test_db_connection_info(self):
        """Test DBConnectionInfo model."""
        conn_info = DBConnectionInfo(
            type="postgresql",
            host="localhost",
            database="test_db"
        )
        
        assert conn_info.type == "postgresql"
        assert conn_info.host == "localhost"
        assert conn_info.database == "test_db"
    
    def test_db_schema_info(self):
        """Test DBSchemaInfo model."""
        schema_info = DBSchemaInfo(
            enabled=True,
            tables=["users", "orders"],
            schema_map={"users": {"columns": ["id", "name"]}}
        )
        
        assert schema_info.enabled is True
        assert len(schema_info.tables) == 2
        assert schema_info.schema_map["users"]["columns"] == ["id", "name"]
    
    def test_db_connect_response(self):
        """Test DBConnectResponse model."""
        conn_info = DBConnectionInfo(
            type="postgresql",
            host="localhost",
            database="test_db"
        )
        
        schema_info = DBSchemaInfo(
            enabled=True,
            tables=["users", "orders"]
        )
        
        response = DBConnectResponse(
            success=True,
            session_id="test-session-123",
            connection_info=conn_info,
            schema_info=schema_info
        )
        
        assert response.success is True
        assert response.session_id == "test-session-123"
        assert response.connection_info.type == "postgresql"
        assert response.schema_info.enabled is True


class TestSessionTypes:
    """Test session-related types."""
    
    def test_index_info(self):
        """Test IndexInfo model."""
        index_info = IndexInfo(
            enabled=True,
            document_count=1000,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        assert index_info.enabled is True
        assert index_info.document_count == 1000
        assert index_info.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_session_info(self):
        """Test SessionInfo model."""
        index_info = IndexInfo(
            enabled=True,
            document_count=1000
        )
        
        session_info = SessionInfo(
            session_id="test-session-123",
            data_source=DataSource.FILE,
            index_info=index_info,
            session_data={"key": "value"}
        )
        
        assert session_info.session_id == "test-session-123"
        assert session_info.data_source == DataSource.FILE
        assert session_info.index_info.enabled is True
        assert session_info.session_data["key"] == "value"


class TestModelValidation:
    """Test model validation and error handling."""
    
    def test_required_fields_validation(self):
        """Test validation of required fields."""
        with pytest.raises(ValueError):
            FileInfo(
                name="test.xlsx",
                # Missing required fields
            )
    
    def test_type_validation(self):
        """Test type validation."""
        with pytest.raises(ValueError):
            FileInfo(
                name="test.xlsx",
                rows="not_a_number",  # Should be int
                columns=5,
                column_names=["col1"],
                size_bytes=1024
            )
    
    def test_enum_validation(self):
        """Test enum validation."""
        with pytest.raises(ValueError):
            AskResponse(
                question="Test",
                answer="Test answer",
                query_type="invalid_type",  # Should be QueryType enum
                data=QueryData(summary=DataSummary(rows=100, columns=5, column_names=["col1"], data_types={})),
                session_id="test-session",
                timestamp=datetime.utcnow()
            )
    
    def test_optional_field_defaults(self):
        """Test optional field defaults."""
        file_info = FileInfo(
            name="test.xlsx",
            rows=100,
            columns=5,
            column_names=["col1"],
            size_bytes=1024
        )
        
        # Optional fields should have None as default
        assert file_info.size_bytes == 1024  # This is required
        # Other fields are required, so no defaults to test
