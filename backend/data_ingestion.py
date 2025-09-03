"""
Data ingestion module for handling Excel/CSV files and database connections
"""

import pandas as pd
import io
import json
import uuid
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, MetaData, inspect
import openpyxl
from datetime import datetime

from .database import DatabaseManager

class DataIngestionManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    async def process_excel_file(self, file_content: bytes, filename: str, session_id: Optional[str] = None) -> Dict:
        """Process uploaded Excel/CSV file"""
        try:
            # Determine file type and read accordingly
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(file_content))
            else:
                raise ValueError("Unsupported file format")
            
            # Basic validation
            if df.empty:
                raise ValueError("File is empty")
            
            if len(df.columns) == 0:
                raise ValueError("No columns found in file")
            
            # Generate schema information
            schema_info = self._generate_schema_info(df)
            
            # Create preview data (first 5 rows)
            preview = df.head(5).to_dict('records')
            
            # Create or update session
            if not session_id:
                data_source_info = {
                    "filename": filename,
                    "file_size": len(file_content),
                    "uploaded_at": datetime.utcnow().isoformat()
                }
                session_id = await self.db_manager.create_session(
                    "excel",
                    data_source_info,
                    schema_info
                )
            else:
                # Update existing session
                data_source_info = {
                    "filename": filename,
                    "file_size": len(file_content),
                    "uploaded_at": datetime.utcnow().isoformat()
                }
                # Update session logic would go here
            
            return {
                "session_id": session_id,
                "schema": schema_info,
                "preview": preview,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
        
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
    
    async def connect_database(self, connection_info: Dict) -> Dict:
        """Connect to a database and extract schema information"""
        try:
            # Build connection string
            db_type = connection_info["db_type"]
            host = connection_info["host"]
            port = connection_info["port"]
            database = connection_info["database"]
            username = connection_info["username"]
            password = connection_info["password"]
            
            if db_type == "postgresql":
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "mysql":
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "sqlite":
                connection_string = f"sqlite:///{database}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            # Test connection
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                # Test query
                conn.execute(text("SELECT 1"))
            
            # Extract schema information
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            schema_info = {
                "database_type": db_type,
                "tables": {}
            }
            
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                table_info = {
                    "columns": [],
                    "row_count": None
                }
                
                for column in columns:
                    column_info = {
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "primary_key": column.get("primary_key", False)
                    }
                    table_info["columns"].append(column_info)
                
                # Get row count (optional, might be slow for large tables)
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        table_info["row_count"] = result.scalar()
                except:
                    table_info["row_count"] = "Unknown"
                
                schema_info["tables"][table_name] = table_info
            
            # Create session
            data_source_info = {
                "host": host,
                "port": port,
                "database": database,
                "username": username,
                "db_type": db_type,
                "connected_at": datetime.utcnow().isoformat()
            }
            
            session_id = await self.db_manager.create_session(
                "database",
                data_source_info,
                schema_info
            )
            
            return {
                "session_id": session_id,
                "tables": list(tables),
                "schema": schema_info
            }
        
        except Exception as e:
            raise Exception(f"Error connecting to database: {str(e)}")
    
    def _generate_schema_info(self, df: pd.DataFrame) -> Dict:
        """Generate schema information from DataFrame"""
        schema_info = {
            "data_type": "excel",
            "columns": []
        }
        
        for column in df.columns:
            column_info = {
                "name": column,
                "type": str(df[column].dtype),
                "nullable": df[column].isnull().any(),
                "unique_values": df[column].nunique(),
                "sample_values": df[column].dropna().head(3).tolist()
            }
            
            # Add statistical info for numeric columns
            if pd.api.types.is_numeric_dtype(df[column]):
                column_info.update({
                    "min": float(df[column].min()) if not df[column].isnull().all() else None,
                    "max": float(df[column].max()) if not df[column].isnull().all() else None,
                    "mean": float(df[column].mean()) if not df[column].isnull().all() else None
                })
            
            schema_info["columns"].append(column_info)
        
        return schema_info
    
    async def get_data_sample(self, session_id: str, table_name: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get a sample of data from the session's data source"""
        session = await self.db_manager.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        
        if session["data_source_type"] == "excel":
            # For Excel files, we'd need to reload the data
            # This is a simplified version - in production, you might cache the data
            raise NotImplementedError("Excel data sampling not implemented in this version")
        
        elif session["data_source_type"] == "database":
            # Connect to database and get sample
            data_source_info = session["data_source_info"]
            db_type = data_source_info["db_type"]
            host = data_source_info["host"]
            port = data_source_info["port"]
            database = data_source_info["database"]
            username = data_source_info["username"]
            password = data_source_info["password"]
            
            if db_type == "postgresql":
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "mysql":
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            engine = create_engine(connection_string)
            
            # Get first table if none specified
            if not table_name:
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                if not tables:
                    raise ValueError("No tables found in database")
                table_name = tables[0]
            
            # Get sample data
            with engine.connect() as conn:
                query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
                result = conn.execute(query)
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
        
        else:
            raise ValueError(f"Unsupported data source type: {session['data_source_type']}")
