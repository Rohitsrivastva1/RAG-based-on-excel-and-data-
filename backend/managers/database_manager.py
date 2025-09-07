"""
Database manager for SQLAlchemy connectors.
Handles PostgreSQL, MySQL, and SQLite connections with safe query execution.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

try:
    from ..settings import settings
    from ..utils.types import DataSource
    from ..utils.security import validate_sql_query, log_security_event
    from ..logging_config import get_logger, log_performance, log_error
except ImportError:
    from settings import settings
    from utils.types import DataSource
    from utils.security import validate_sql_query, log_security_event
    from logging_config import get_logger, log_performance, log_error

logger = get_logger(__name__)

# Optional database drivers
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("PostgreSQL driver not available")

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("MySQL driver not available")


class DatabaseConnection:
    """Represents a database connection with metadata."""
    
    def __init__(
        self,
        session_id: str,
        db_type: str,
        engine: Engine,
        connection_info: Dict[str, Any]
    ):
        self.session_id = session_id
        self.db_type = db_type
        self.engine = engine
        self.connection_info = connection_info
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.query_count = 0
    
    def touch(self):
        """Update last used timestamp and increment query count."""
        self.last_used = datetime.utcnow()
        self.query_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'db_type': self.db_type,
            'connection_info': self.connection_info,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'query_count': self.query_count
        }


class DatabaseManager:
    """Manages database connections and query execution."""
    
    def __init__(self):
        self.connections: Dict[str, DatabaseConnection] = {}
        self.max_connections = 10
        self.connection_timeout = 300  # 5 minutes
    
    def connect_postgresql(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        session_id: str
    ) -> bool:
        """
        Connect to PostgreSQL database.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Username
            password: Password
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not POSTGRES_AVAILABLE:
            logger.error("PostgreSQL driver not available")
            return False
        
        try:
            # Create connection string
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
            # Create engine
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Store connection
            connection_info = {
                'host': host,
                'port': port,
                'database': database,
                'username': username
            }
            
            connection = DatabaseConnection(
                session_id=session_id,
                db_type='postgresql',
                engine=engine,
                connection_info=connection_info
            )
            
            self.connections[session_id] = connection
            
            logger.info(f"Connected to PostgreSQL database", extra={
                'session_id': session_id,
                'host': host,
                'database': database
            })
            
            return True
            
        except Exception as e:
            log_error(e, "PostgreSQL connection failed", 
                     session_id=session_id, host=host, database=database)
            return False
    
    def connect_mysql(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        session_id: str
    ) -> bool:
        """
        Connect to MySQL database.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Username
            password: Password
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not MYSQL_AVAILABLE:
            logger.error("MySQL driver not available")
            return False
        
        try:
            # Create connection string
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            
            # Create engine
            engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Store connection
            connection_info = {
                'host': host,
                'port': port,
                'database': database,
                'username': username
            }
            
            connection = DatabaseConnection(
                session_id=session_id,
                db_type='mysql',
                engine=engine,
                connection_info=connection_info
            )
            
            self.connections[session_id] = connection
            
            logger.info(f"Connected to MySQL database", extra={
                'session_id': session_id,
                'host': host,
                'database': database
            })
            
            return True
            
        except Exception as e:
            log_error(e, "MySQL connection failed",
                     session_id=session_id, host=host, database=database)
            return False
    
    def connect_sqlite(self, database_path: str, session_id: str) -> bool:
        """
        Connect to SQLite database.
        
        Args:
            database_path: Path to SQLite database file
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create connection string
            connection_string = f"sqlite:///{database_path}"
            
            # Create engine
            engine = create_engine(
                connection_string,
                echo=False
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Store connection
            connection_info = {
                'database_path': database_path,
                'database': database_path.split('/')[-1]
            }
            
            connection = DatabaseConnection(
                session_id=session_id,
                db_type='sqlite',
                engine=engine,
                connection_info=connection_info
            )
            
            self.connections[session_id] = connection
            
            logger.info(f"Connected to SQLite database", extra={
                'session_id': session_id,
                'database_path': database_path
            })
            
            return True
            
        except Exception as e:
            log_error(e, "SQLite connection failed",
                     session_id=session_id, database_path=database_path)
            return False
    
    def get_connection(self, session_id: str) -> Optional[DatabaseConnection]:
        """Get database connection for session."""
        connection = self.connections.get(session_id)
        if connection:
            connection.touch()
        return connection
    
    def execute_query(
        self,
        session_id: str,
        sql_query: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL query safely.
        
        Args:
            session_id: Session identifier
            sql_query: SQL query to execute
            limit: Optional row limit
            
        Returns:
            Query result dictionary
        """
        connection = self.get_connection(session_id)
        if not connection:
            return {"error": "No database connection found for session"}
        
        # Validate SQL query
        is_valid, error_msg = validate_sql_query(sql_query)
        if not is_valid:
            log_security_event("invalid_sql_query", {
                "session_id": session_id,
                "query": sql_query,
                "error": error_msg
            })
            return {"error": f"Invalid SQL query: {error_msg}"}
        
        try:
            start_time = datetime.utcnow()
            
            # Add LIMIT if specified and not already present
            if limit and "LIMIT" not in sql_query.upper():
                sql_query = f"{sql_query.rstrip(';')} LIMIT {limit}"
            
            # Execute query
            with connection.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                
                # Convert to DataFrame
                df = pd.read_sql(sql_query, conn)
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                log_performance("execute_query", duration * 1000,
                              session_id=session_id,
                              query_type="SELECT",
                              row_count=len(df))
                
                logger.info(f"Executed SQL query", extra={
                    'session_id': session_id,
                    'row_count': len(df),
                    'duration_ms': duration * 1000
                })
                
                return {
                    "data": df,
                    "row_count": len(df),
                    "columns": df.columns.tolist(),
                    "dtypes": df.dtypes.to_dict(),
                    "sql_query": sql_query,
                    "execution_time_ms": duration * 1000
                }
                
        except SQLAlchemyError as e:
            log_error(e, "SQL execution failed",
                     session_id=session_id, sql_query=sql_query)
            return {"error": f"SQL execution error: {str(e)}"}
        except Exception as e:
            log_error(e, "Unexpected error during query execution",
                     session_id=session_id, sql_query=sql_query)
            return {"error": f"Unexpected error: {str(e)}"}
    
    def get_schema_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Schema information dictionary
        """
        connection = self.get_connection(session_id)
        if not connection:
            return {"error": "No database connection found for session"}
        
        try:
            with connection.engine.connect() as conn:
                inspector = inspect(conn)
                
                # Get table information
                tables = inspector.get_table_names()
                table_info = {}
                
                for table_name in tables:
                    columns = inspector.get_columns(table_name)
                    indexes = inspector.get_indexes(table_name)
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    table_info[table_name] = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col["nullable"],
                                "default": col.get("default"),
                                "primary_key": col.get("primary_key", False)
                            }
                            for col in columns
                        ],
                        "indexes": [
                            {
                                "name": idx["name"],
                                "columns": idx["column_names"],
                                "unique": idx["unique"]
                            }
                            for idx in indexes
                        ],
                        "foreign_keys": [
                            {
                                "name": fk["name"],
                                "columns": fk["constrained_columns"],
                                "referenced_table": fk["referred_table"],
                                "referenced_columns": fk["referred_columns"]
                            }
                            for fk in foreign_keys
                        ]
                    }
                
                return {
                    "tables": table_info,
                    "table_count": len(tables),
                    "database_type": connection.db_type,
                    "connection_info": connection.connection_info
                }
                
        except Exception as e:
            log_error(e, "Failed to get schema info",
                     session_id=session_id)
            return {"error": f"Failed to get schema info: {str(e)}"}
    
    def get_sample_data(
        self,
        session_id: str,
        table_name: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get sample data from a table.
        
        Args:
            session_id: Session identifier
            table_name: Name of the table
            limit: Number of rows to return
            
        Returns:
            Sample data dictionary
        """
        connection = self.get_connection(session_id)
        if not connection:
            return {"error": "No database connection found for session"}
        
        try:
            # Validate table name (basic security check)
            if not table_name.replace('_', '').replace('-', '').isalnum():
                return {"error": "Invalid table name"}
            
            sql_query = f"SELECT * FROM {table_name} LIMIT {limit}"
            
            result = self.execute_query(session_id, sql_query, limit)
            
            if "error" in result:
                return result
            
            return {
                "table_name": table_name,
                "sample_data": result["data"],
                "row_count": result["row_count"],
                "columns": result["columns"]
            }
            
        except Exception as e:
            log_error(e, "Failed to get sample data",
                     session_id=session_id, table_name=table_name)
            return {"error": f"Failed to get sample data: {str(e)}"}
    
    def test_connection(self, session_id: str) -> bool:
        """
        Test database connection.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if connection is active, False otherwise
        """
        connection = self.get_connection(session_id)
        if not connection:
            return False
        
        try:
            with connection.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def close_connection(self, session_id: str) -> bool:
        """
        Close database connection.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if closed successfully, False otherwise
        """
        if session_id in self.connections:
            try:
                connection = self.connections[session_id]
                connection.engine.dispose()
                del self.connections[session_id]
                
                logger.info(f"Closed database connection", extra={
                    'session_id': session_id
                })
                
                return True
            except Exception as e:
                log_error(e, "Failed to close connection",
                         session_id=session_id)
                return False
        return True
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all active connections."""
        return [conn.to_dict() for conn in self.connections.values()]
    
    def cleanup_stale_connections(self) -> int:
        """Clean up stale connections."""
        current_time = datetime.utcnow()
        stale_connections = []
        
        for session_id, connection in self.connections.items():
            time_since_last_use = (current_time - connection.last_used).total_seconds()
            if time_since_last_use > self.connection_timeout:
                stale_connections.append(session_id)
        
        for session_id in stale_connections:
            self.close_connection(session_id)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale connections")
        
        return len(stale_connections)


# Global database manager instance
database_manager: Optional[DatabaseManager] = None


def initialize_database_manager() -> DatabaseManager:
    """Initialize the global database manager."""
    global database_manager
    database_manager = DatabaseManager()
    return database_manager


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    if database_manager is None:
        raise RuntimeError("Database manager not initialized. Call initialize_database_manager() first.")
    return database_manager


# Example usage and testing
if __name__ == "__main__":
    # Test database manager
    manager = DatabaseManager()
    
    # Test SQLite connection (no external dependencies)
    test_db_path = "test.db"
    session_id = "test-session"
    
    success = manager.connect_sqlite(test_db_path, session_id)
    print(f"SQLite connection successful: {success}")
    
    if success:
        # Test schema info
        schema = manager.get_schema_info(session_id)
        print(f"Schema info: {schema}")
        
        # Test connection
        is_connected = manager.test_connection(session_id)
        print(f"Connection active: {is_connected}")
        
        # Close connection
        manager.close_connection(session_id)
        print("Connection closed")
    
    # Cleanup
    import os
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
