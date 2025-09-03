"""
Database Connection Manager
Handles dynamic connections to PostgreSQL, MySQL, SQLite
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import sqlite3

from dotenv import load_dotenv
load_dotenv()

class DatabaseManager:
    """Manages database connections and query execution"""
    
    def __init__(self):
        self.connections = {}  # Store connections by session_id
        self.engines = {}  # Store SQLAlchemy engines by session_id
    
    def connect_postgresql(self, host: str, port: int, database: str, username: str, password: str, session_id: str) -> bool:
        """Connect to PostgreSQL database"""
        try:
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.engines[session_id] = engine
            print(f"Connected to PostgreSQL database: {database}")
            return True
            
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False
    
    def connect_mysql(self, host: str, port: int, database: str, username: str, password: str, session_id: str) -> bool:
        """Connect to MySQL database"""
        try:
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.engines[session_id] = engine
            print(f"Connected to MySQL database: {database}")
            return True
            
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def connect_sqlite(self, file_path: str, session_id: str) -> bool:
        """Connect to SQLite database"""
        try:
            if not os.path.exists(file_path):
                print(f"SQLite file not found: {file_path}")
                return False
            
            connection_string = f"sqlite:///{file_path}"
            engine = create_engine(connection_string)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.engines[session_id] = engine
            print(f"Connected to SQLite database: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return False
    
    def get_schema_info(self, session_id: str) -> Dict[str, Any]:
        """Get database schema information"""
        if session_id not in self.engines:
            return {"error": "No database connection found"}
        
        try:
            engine = self.engines[session_id]
            inspector = inspect(engine)
            
            schema_info = {
                "tables": [],
                "columns": {},
                "relationships": []
            }
            
            # Get all tables
            tables = inspector.get_table_names()
            schema_info["tables"] = tables
            
            # Get columns for each table
            for table in tables:
                columns = inspector.get_columns(table)
                schema_info["columns"][table] = [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "primary_key": col.get("primary_key", False)
                    }
                    for col in columns
                ]
            
            return schema_info
            
        except Exception as e:
            return {"error": f"Error getting schema info: {e}"}
    
    def execute_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        if session_id not in self.engines:
            return {"error": "No database connection found"}
        
        try:
            engine = self.engines[session_id]
            
            # Execute query and get results as DataFrame
            df = pd.read_sql_query(query, engine)
            
            return {
                "success": True,
                "data": df,
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "query": query
            }
            
        except SQLAlchemyError as e:
            return {"error": f"SQL Error: {e}"}
        except Exception as e:
            return {"error": f"Error executing query: {e}"}
    
    def get_sample_data(self, session_id: str, table_name: str, limit: int = 10) -> Dict[str, Any]:
        """Get sample data from a table"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(session_id, query)
    
    def get_table_info(self, session_id: str, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        if session_id not in self.engines:
            return {"error": "No database connection found"}
        
        try:
            engine = self.engines[session_id]
            
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = pd.read_sql_query(count_query, engine)
            row_count = count_result['count'].iloc[0]
            
            # Get sample data
            sample_query = f"SELECT * FROM {table_name} LIMIT 5"
            sample_data = pd.read_sql_query(sample_query, engine)
            
            # Get column info
            inspector = inspect(engine)
            columns = inspector.get_columns(table_name)
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"]
                    }
                    for col in columns
                ],
                "sample_data": sample_data.to_dict('records')
            }
            
        except Exception as e:
            return {"error": f"Error getting table info: {e}"}
    
    def generate_sql_from_natural_language(self, query: str, schema_info: Dict[str, Any]) -> str:
        """Generate SQL query from natural language (basic implementation)"""
        query_lower = query.lower()
        
        # Basic keyword-based SQL generation
        if "select" in query_lower and "from" in query_lower:
            # Already looks like SQL
            return query
        
        # Get available tables
        tables = schema_info.get("tables", [])
        if not tables:
            return "SELECT 1"  # Fallback
        
        # Simple pattern matching
        if "count" in query_lower:
            table = tables[0]  # Use first table
            return f"SELECT COUNT(*) FROM {table}"
        
        elif "show" in query_lower or "display" in query_lower:
            table = tables[0]
            return f"SELECT * FROM {table} LIMIT 10"
        
        elif "max" in query_lower or "maximum" in query_lower:
            table = tables[0]
            columns = schema_info.get("columns", {}).get(table, [])
            numeric_cols = [col["name"] for col in columns if "int" in col["type"].lower() or "float" in col["type"].lower()]
            if numeric_cols:
                return f"SELECT MAX({numeric_cols[0]}) FROM {table}"
        
        # Default query
        return f"SELECT * FROM {tables[0]} LIMIT 10"
    
    def close_connection(self, session_id: str):
        """Close database connection"""
        if session_id in self.engines:
            self.engines[session_id].dispose()
            del self.engines[session_id]
            print(f"Closed database connection for session {session_id}")
    
    def list_connections(self) -> List[str]:
        """List all active connections"""
        return list(self.engines.keys())

# Global instance
db_manager = DatabaseManager()
