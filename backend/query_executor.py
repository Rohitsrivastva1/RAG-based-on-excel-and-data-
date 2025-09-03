"""
Query execution module for safely executing SQL and Pandas queries
"""

import os
import time
import json
import pandas as pd
import io
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import subprocess
import tempfile
from datetime import datetime

from .database import DatabaseManager

class QueryExecutor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.max_execution_time = 30  # seconds
        self.max_rows = 10000  # Maximum rows to return
    
    async def execute_query(self, query: str, query_type: str, session_id: str) -> Dict:
        """Execute a query and return results"""
        start_time = time.time()
        
        try:
            if query_type == "sql":
                result = await self._execute_sql_query(query, session_id)
            elif query_type == "pandas":
                result = await self._execute_pandas_query(query, session_id)
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
            
            execution_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            # Save query result to database
            query_id = await self.db_manager.save_query(
                session_id=session_id,
                question="",  # Will be filled by caller
                generated_query=query,
                query_type=query_type,
                execution_time=execution_time,
                row_count=len(result["data"]),
                result_data=result["data"]
            )
            
            result["query_id"] = query_id
            result["execution_time"] = execution_time
            result["row_count"] = len(result["data"])
            
            return result
        
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            raise Exception(f"Query execution failed: {str(e)}")
    
    async def _execute_sql_query(self, query: str, session_id: str) -> Dict:
        """Execute SQL query against database"""
        try:
            # Get session information
            session = await self.db_manager.get_session(session_id)
            if not session:
                raise ValueError("Session not found")
            
            if session["data_source_type"] != "database":
                raise ValueError("SQL queries can only be executed on database sessions")
            
            # Create database connection
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
            
            # Validate and sanitize query
            sanitized_query = self._sanitize_sql_query(query)
            
            # Execute query
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                # Add LIMIT if not present and query is a SELECT
                if sanitized_query.upper().strip().startswith('SELECT') and 'LIMIT' not in sanitized_query.upper():
                    sanitized_query += f" LIMIT {self.max_rows}"
                
                result = conn.execute(text(sanitized_query))
                
                # Convert to list of dictionaries
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "data": data,
                    "columns": list(columns),
                    "query_type": "sql"
                }
        
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")
    
    async def _execute_pandas_query(self, query: str, session_id: str) -> Dict:
        """Execute pandas query on Excel data"""
        try:
            # Get session information
            session = await self.db_manager.get_session(session_id)
            if not session:
                raise ValueError("Session not found")
            
            if session["data_source_type"] != "excel":
                raise ValueError("Pandas queries can only be executed on Excel sessions")
            
            # For this implementation, we'll simulate pandas execution
            # In a real implementation, you would:
            # 1. Load the Excel file data
            # 2. Execute the pandas code in a sandboxed environment
            # 3. Return the results
            
            # This is a simplified version - in production, you'd need proper sandboxing
            sanitized_code = self._sanitize_pandas_code(query)
            
            # Create a mock DataFrame for demonstration
            # In real implementation, load actual data
            df = pd.DataFrame({
                'id': [1, 2, 3, 4, 5],
                'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                'age': [25, 30, 35, 28, 32],
                'salary': [50000, 60000, 70000, 55000, 65000]
            })
            
            # Execute pandas code in a controlled environment
            local_vars = {'df': df}
            exec(sanitized_code, {"pd": pd, "np": __import__('numpy')}, local_vars)
            
            # Get the result (assuming it's stored in 'result' variable)
            if 'result' in local_vars:
                result_data = local_vars['result']
            else:
                # If no 'result' variable, assume the last expression is the result
                result_data = df  # Fallback
            
            # Convert to list of dictionaries
            if isinstance(result_data, pd.DataFrame):
                data = result_data.head(self.max_rows).to_dict('records')
                columns = list(result_data.columns)
            else:
                data = [{"result": str(result_data)}]
                columns = ["result"]
            
            return {
                "data": data,
                "columns": columns,
                "query_type": "pandas"
            }
        
        except Exception as e:
            raise Exception(f"Pandas execution error: {str(e)}")
    
    def _sanitize_sql_query(self, query: str) -> str:
        """Sanitize SQL query to prevent malicious operations"""
        query_upper = query.upper().strip()
        
        # Only allow SELECT statements
        if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
            raise ValueError("Only SELECT and WITH statements are allowed")
        
        # Block dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE',
            'EXEC', 'EXECUTE', 'SP_', 'XP_', '--', '/*', '*/', 'UNION'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Dangerous keyword '{keyword}' not allowed")
        
        return query.strip()
    
    def _sanitize_pandas_code(self, code: str) -> str:
        """Sanitize pandas code to prevent malicious operations"""
        # Block dangerous operations
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys', '__import__',
            'exec(', 'eval(', 'open(', 'file(', 'input(', 'raw_input(',
            'exit(', 'quit(', 'del ', 'globals(', 'locals('
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                raise ValueError(f"Dangerous pattern '{pattern}' not allowed")
        
        return code
    
    async def export_data(self, format: str, session_id: str, query_id: Optional[str] = None) -> Dict:
        """Export data in various formats"""
        try:
            if query_id:
                # Export specific query result
                query_result = await self.db_manager.get_query_result(query_id)
                if not query_result:
                    raise ValueError("Query result not found")
                
                data = query_result["result_data"]
                filename = f"query_{query_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                # Export session data (simplified)
                raise ValueError("Session export not implemented")
            
            if format == "csv":
                return await self._export_csv(data, filename)
            elif format == "png":
                return await self._export_png(data, filename)
            elif format == "pdf":
                return await self._export_pdf(data, filename)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    async def _export_csv(self, data: List[Dict], filename: str) -> Dict:
        """Export data as CSV"""
        try:
            df = pd.DataFrame(data)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            df.to_csv(temp_file.name, index=False)
            temp_file.close()
            
            return {
                "file_path": temp_file.name,
                "media_type": "text/csv",
                "filename": f"{filename}.csv"
            }
        
        except Exception as e:
            raise Exception(f"CSV export failed: {str(e)}")
    
    async def _export_png(self, data: List[Dict], filename: str) -> Dict:
        """Export data as PNG image"""
        try:
            # This would require visualization data
            # For now, return a placeholder
            raise NotImplementedError("PNG export requires visualization data")
        
        except Exception as e:
            raise Exception(f"PNG export failed: {str(e)}")
    
    async def _export_pdf(self, data: List[Dict], filename: str) -> Dict:
        """Export data as PDF"""
        try:
            # This would require visualization data
            # For now, return a placeholder
            raise NotImplementedError("PDF export requires visualization data")
        
        except Exception as e:
            raise Exception(f"PDF export failed: {str(e)}")
