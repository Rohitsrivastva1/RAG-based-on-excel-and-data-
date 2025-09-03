"""
AI processing module using LlamaIndex and LangChain for query generation
"""

import os
import json
from typing import Dict, List, Any, Optional
try:
    from llama_index import VectorStoreIndex, Document, ServiceContext
    from llama_index.llms import OpenAI, Anthropic
    from llama_index.embeddings import OpenAIEmbedding
except ImportError:
    # Fallback for different versions
    from llama_index.core import VectorStoreIndex, Document, ServiceContext
    from llama_index.llms import OpenAI, Anthropic
    from llama_index.embeddings import OpenAIEmbedding
try:
    from langchain.agents import create_sql_agent, AgentExecutor
    from langchain.agents.agent_toolkits import SQLDatabaseToolkit
    from langchain.sql_database import SQLDatabase
    from langchain.llms import OpenAI as LangChainOpenAI
    from langchain.chat_models import ChatOpenAI, ChatAnthropic
except ImportError:
    # Fallback for newer versions
    from langchain.agents import create_sql_agent, AgentExecutor
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain_community.sql_database import SQLDatabase
    from langchain.llms import OpenAI as LangChainOpenAI
    from langchain.chat_models import ChatOpenAI, ChatAnthropic
from dotenv import load_dotenv

from .database import DatabaseManager

load_dotenv()

class AIProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        # Initialize LLM
        if "gpt" in self.llm_model.lower():
            self.llm = OpenAI(model=self.llm_model, temperature=0.1)
            self.langchain_llm = ChatOpenAI(model_name=self.llm_model, temperature=0.1)
        elif "claude" in self.llm_model.lower():
            self.llm = Anthropic(model=self.llm_model, temperature=0.1)
            self.langchain_llm = ChatAnthropic(model=self.llm_model, temperature=0.1)
        else:
            # Default to OpenAI
            self.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
            self.langchain_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbedding()
        
        # Service context for LlamaIndex
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embeddings
        )
    
    async def process_question(self, question: str, session_id: str) -> Dict:
        """Process natural language question and generate appropriate query"""
        try:
            # Get session information
            session = await self.db_manager.get_session(session_id)
            if not session:
                raise ValueError("Session not found")
            
            data_source_type = session["data_source_type"]
            schema_info = session["schema_info"]
            
            if data_source_type == "database":
                return await self._process_database_question(question, session, schema_info)
            elif data_source_type == "excel":
                return await self._process_excel_question(question, session, schema_info)
            else:
                raise ValueError(f"Unsupported data source type: {data_source_type}")
        
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}")
    
    async def _process_database_question(self, question: str, session: Dict, schema_info: Dict) -> Dict:
        """Process question for database data source"""
        try:
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
            
            # Create SQL database object
            db = SQLDatabase.from_uri(connection_string)
            
            # Create SQL agent
            toolkit = SQLDatabaseToolkit(db=db, llm=self.langchain_llm)
            agent = create_sql_agent(
                llm=self.langchain_llm,
                toolkit=toolkit,
                verbose=True,
                handle_parsing_errors=True
            )
            
            # Generate SQL query
            response = agent.run(question)
            
            # Extract SQL query from response (this is a simplified approach)
            # In practice, you might need more sophisticated parsing
            sql_query = self._extract_sql_from_response(response)
            
            # Determine suggested chart type
            suggested_chart_type = self._suggest_chart_type(question, sql_query)
            
            return {
                "query": sql_query,
                "query_type": "sql",
                "suggested_chart_type": suggested_chart_type,
                "raw_response": response
            }
        
        except Exception as e:
            # Fallback to simple prompt-based approach
            return await self._fallback_sql_generation(question, schema_info)
    
    async def _process_excel_question(self, question: str, session: Dict, schema_info: Dict) -> Dict:
        """Process question for Excel data source"""
        try:
            # Create context from schema
            schema_context = self._create_schema_context(schema_info)
            
            # Generate pandas code
            prompt = f"""
            You are a data analyst. Given the following data schema and user question, generate pandas code to answer the question.
            
            Data Schema:
            {schema_context}
            
            User Question: {question}
            
            Generate pandas code that:
            1. Loads the data (assume it's in a variable called 'df')
            2. Performs the necessary operations to answer the question
            3. Returns the result in a clear format
            
            Only return the pandas code, no explanations.
            """
            
            response = self.llm.complete(prompt)
            pandas_code = response.text.strip()
            
            # Clean up the code
            pandas_code = self._clean_pandas_code(pandas_code)
            
            # Determine suggested chart type
            suggested_chart_type = self._suggest_chart_type(question, pandas_code)
            
            return {
                "query": pandas_code,
                "query_type": "pandas",
                "suggested_chart_type": suggested_chart_type,
                "raw_response": response.text
            }
        
        except Exception as e:
            raise Exception(f"Error generating pandas code: {str(e)}")
    
    async def _fallback_sql_generation(self, question: str, schema_info: Dict) -> Dict:
        """Fallback SQL generation using simple prompt"""
        try:
            schema_context = self._create_schema_context(schema_info)
            
            prompt = f"""
            You are a SQL expert. Given the following database schema and user question, generate a SQL query.
            
            Database Schema:
            {schema_context}
            
            User Question: {question}
            
            Generate a SQL query that answers the question. Only return the SQL query, no explanations.
            """
            
            response = self.llm.complete(prompt)
            sql_query = response.text.strip()
            
            # Clean up the query
            sql_query = self._clean_sql_query(sql_query)
            
            suggested_chart_type = self._suggest_chart_type(question, sql_query)
            
            return {
                "query": sql_query,
                "query_type": "sql",
                "suggested_chart_type": suggested_chart_type,
                "raw_response": response.text
            }
        
        except Exception as e:
            raise Exception(f"Error in fallback SQL generation: {str(e)}")
    
    def _create_schema_context(self, schema_info: Dict) -> str:
        """Create a readable schema context for the LLM"""
        if "tables" in schema_info:
            # Database schema
            context = "Tables:\n"
            for table_name, table_info in schema_info["tables"].items():
                context += f"\n{table_name}:\n"
                for column in table_info["columns"]:
                    context += f"  - {column['name']} ({column['type']})"
                    if column.get('primary_key'):
                        context += " [PRIMARY KEY]"
                    if not column.get('nullable'):
                        context += " [NOT NULL]"
                    context += "\n"
        else:
            # Excel schema
            context = "Columns:\n"
            for column in schema_info["columns"]:
                context += f"  - {column['name']} ({column['type']})"
                if column.get('sample_values'):
                    context += f" - Sample values: {column['sample_values']}"
                context += "\n"
        
        return context
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from agent response"""
        # This is a simplified approach - in practice, you might need more sophisticated parsing
        lines = response.split('\n')
        sql_query = ""
        in_sql = False
        
        for line in lines:
            if 'SELECT' in line.upper() or 'WITH' in line.upper():
                in_sql = True
            if in_sql:
                sql_query += line + '\n'
                if line.strip().endswith(';'):
                    break
        
        return sql_query.strip()
    
    def _clean_sql_query(self, query: str) -> str:
        """Clean and validate SQL query"""
        # Remove markdown formatting
        query = query.replace('```sql', '').replace('```', '')
        query = query.strip()
        
        # Basic validation
        if not any(keyword in query.upper() for keyword in ['SELECT', 'WITH']):
            raise ValueError("Generated query is not a valid SELECT statement")
        
        return query
    
    def _clean_pandas_code(self, code: str) -> str:
        """Clean and validate pandas code"""
        # Remove markdown formatting
        code = code.replace('```python', '').replace('```', '')
        code = code.strip()
        
        # Basic validation
        if 'df' not in code:
            raise ValueError("Generated code doesn't reference the dataframe")
        
        return code
    
    def _suggest_chart_type(self, question: str, query: str) -> str:
        """Suggest appropriate chart type based on question and query"""
        question_lower = question.lower()
        query_lower = query.lower()
        
        # Time series indicators
        if any(word in question_lower for word in ['trend', 'over time', 'time series', 'monthly', 'yearly', 'daily']):
            return 'line'
        
        # Comparison indicators
        if any(word in question_lower for word in ['compare', 'vs', 'versus', 'difference', 'ranking']):
            return 'bar'
        
        # Distribution indicators
        if any(word in question_lower for word in ['distribution', 'breakdown', 'percentage', 'share', 'proportion']):
            return 'pie'
        
        # Correlation indicators
        if any(word in question_lower for word in ['correlation', 'relationship', 'scatter', 'plot']):
            return 'scatter'
        
        # Count/aggregation indicators
        if any(word in query_lower for word in ['count', 'sum', 'avg', 'mean', 'total']):
            return 'bar'
        
        # Default to bar chart
        return 'bar'
