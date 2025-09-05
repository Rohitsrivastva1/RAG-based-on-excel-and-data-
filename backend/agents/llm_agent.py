"""
LLM agent wrapper for LangChain pandas agent integration.
Provides safe execution environment and intelligent query processing.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import pandas as pd
import numpy as np

try:
    from ..settings import settings
    from ..utils.types import QueryType, ChartType
    from ..utils.security import safe_exec_pandas
    from ..logging_config import get_logger, log_performance, log_error
except ImportError:
    from settings import settings
    from utils.types import QueryType, ChartType
    from utils.security import safe_exec_pandas
    from logging_config import get_logger, log_performance, log_error

logger = get_logger(__name__)

# Optional LangChain imports
try:
    from langchain_experimental.agents import create_pandas_dataframe_agent
    from langchain.agents import AgentType
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import AgentAction, AgentFinish
    from langchain_core.callbacks import BaseCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not available ({e}). LLM agent features will be disabled.")


class SafeCallbackHandler:
    """Callback handler for safe agent execution."""
    
    def __init__(self):
        self.generated_code = []
        self.actions = []
    
    def on_agent_action(self, action, **kwargs) -> None:
        """Log agent actions."""
        self.actions.append(action)
        logger.info(f"Agent action: {getattr(action, 'tool', 'unknown')} - {getattr(action, 'tool_input', 'unknown')}")
    
    def on_agent_finish(self, finish, **kwargs) -> None:
        """Log agent finish."""
        logger.info(f"Agent finished: {getattr(finish, 'return_values', 'unknown')}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Log tool start."""
        logger.info(f"Tool started: {serialized.get('name', 'unknown')}")
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Log tool end."""
        logger.info(f"Tool output: {output[:200]}...")  # Truncate long outputs


class LLMAgent:
    """LLM-powered agent for data analysis."""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent = None
        self.callback_handler = SafeCallbackHandler()
        
        if self.llm:
            self._create_agent()
    
    def _initialize_llm(self):
        """Initialize LLM based on available API keys - MANDATORY."""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain not available. LangChain is required for this system.")

        logger.info(f"Initializing LLM: google_key={'***' if settings.google_api_key else None}")
        
        if not settings.google_api_key:
            raise RuntimeError("No Google API key available. Google API key is required for this system.")

        try:
            logger.info("Initializing Google Gemini LLM")
            print("Google API key")
            print(settings.google_api_key)
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.google_api_key,
                temperature=0.1,
                max_output_tokens=2000
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Gemini LLM: {e}")
    
    def _create_agent(self):
        """Create pandas agent with safe configuration - FIXED (removed deprecated kwargs)."""
        if not self.llm:
            raise RuntimeError("LLM not available. Cannot create agent.")
        
        try:
            # Create a dummy DataFrame for agent initialization
            dummy_df = pd.DataFrame({'dummy': [1, 2, 3]})
            
            self.agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=dummy_df,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=5,
                early_stopping_method="generate",
                allow_dangerous_code=True  # Required for pandas agent execution
            )
            
            logger.info("Created LLM agent successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {e}")
    
    def process_with_agent(
        self,
        df: pd.DataFrame,
        question: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Process query with LLM agent.
        
        Args:
            df: DataFrame to analyze
            question: User question
            context: Additional context
            
        Returns:
            Agent result dictionary
        """
        if not self.agent:
            raise RuntimeError("LLM agent not available. Agent creation failed.")
        
        try:
            start_time = datetime.utcnow()
            
            # Create new agent with the actual DataFrame
            agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=df,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                max_iterations=3,
                early_stopping_method="generate",
                allow_dangerous_code=True  # Required for pandas agent execution
            )
            
            # Prepare enhanced question with context
            enhanced_question = self._enhance_question(question, context, df)
            
            # FIX: attach callback handler at runtime
            result = agent.run(enhanced_question, callbacks=[self.callback_handler])
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("llm_agent_process", duration * 1000,
                          question_length=len(question),
                          df_shape=df.shape)
            
            # Determine if visualization is needed
            visualization = self._determine_visualization(question, result, df)
            
            return {
                'answer': str(result),
                'query_type': QueryType.LLM_AGENT.value,
                'generated_code': self._extract_generated_code(),
                'visualization': visualization,
                'confidence': 0.8,
                'processing_time_ms': duration * 1000,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                log_error(e, "Google Gemini API quota exceeded",
                         question=question, df_shape=df.shape)
                raise RuntimeError("Google Gemini API quota exceeded. Please try again later or check your billing.")
            elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                log_error(e, "Invalid Google API key",
                         question=question, df_shape=df.shape)
                raise RuntimeError("Invalid Google API key. Please check your GOOGLE_API_KEY.")
            else:
                log_error(e, "LLM agent processing failed",
                         question=question, df_shape=df.shape)
                raise RuntimeError(f"LLM agent processing failed: {e}")
    
    def _enhance_question(self, question: str, context: str, df: pd.DataFrame) -> str:
        """Enhance question with context and data information."""
        enhanced = question
        
        if context:
            enhanced = f"Context: {context}\n\nQuestion: {question}"
        
        # Add detailed data information
        data_info = f"\n\nData info: {len(df)} rows, {len(df.columns)} columns. "
        data_info += f"Columns: {', '.join(df.columns.tolist())}\n"
        
        # Add sample data for better context
        if len(df) > 0:
            data_info += f"Sample data (first 3 rows):\n{df.head(3).to_string()}\n"
            
            # Add unique values for categorical columns
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].nunique() < 10:
                    unique_vals = df[col].unique()[:10]  # Limit to first 10 unique values
                    data_info += f"Unique values in {col}: {list(unique_vals)}\n"
            
            # Add aggregation examples for better understanding
            if 'Category' in df.columns:
                category_counts = df['Category'].value_counts()
                data_info += f"\nCategory frequency: {category_counts.to_dict()}\n"
                
                # Show example aggregation
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    example_col = numeric_cols[0]
                    category_sum = df.groupby('Category')[example_col].sum()
                    data_info += f"Example aggregation ({example_col} by Category): {category_sum.to_dict()}\n"
        
        enhanced += data_info
        
        # Add strict instructions
        instructions = "\n\nIMPORTANT INSTRUCTIONS:\n"
        instructions += "1. Use only the data provided above - do not make up or hallucinate data\n"
        instructions += "2. Use only safe pandas operations\n"
        instructions += "3. Be precise and accurate in your analysis\n"
        instructions += "4. If asked about categories, use only the categories that exist in the data\n"
        instructions += "5. When aggregating data (sum, count, average), make sure to include ALL rows\n"
        instructions += "6. For category-based queries, group by category and aggregate properly\n"
        instructions += "7. Return data in a clear, structured format\n"
        instructions += "8. Do not use plotting libraries - return data suitable for visualization\n"
        instructions += "9. Always verify your calculations against the provided data"
        
        enhanced += instructions
        
        return enhanced
    
    def _determine_visualization(
        self,
        question: str,
        result: str,
        df: pd.DataFrame
    ) -> Optional[Dict[str, Any]]:
        """Improved visualization logic with priority system."""
        q = question.lower()
        
        # Check for visualization keywords
        viz_keywords = ['chart', 'graph', 'plot', 'visualize', 'bar', 'line', 'pie']
        if not any(keyword in q for keyword in viz_keywords):
            return None
        
        try:
            # 🔹 Force explicit visualization request (HIGHEST PRIORITY)
            if "bar" in q or "bar chart" in q or "bar graph" in q:
                return self._create_category_visualization(df, question)
            
            if "line" in q or "trend" in q or "over time" in q:
                return {"type": "line", "data": {}}  # you can extend
            
            if "pie" in q or "pie chart" in q:
                return {"type": "pie", "data": {}}  # you can extend
            
            if "heatmap" in q or "correlation" in q:
                return self._create_correlation_visualization(df)
            
            # Fallbacks (LOWER PRIORITY)
            if "groupby" in str(result).lower() or "sum()" in str(result).lower():
                return self._create_aggregation_visualization(df, question)
            
            if "corr" in str(result).lower():
                return self._create_correlation_visualization(df)
            
            # Default fallback
            return self._create_table_visualization(df)
                
        except Exception as e:
            logger.warning(f"Failed to create visualization: {e}")
            return None
    
    def _create_aggregation_visualization(
        self,
        df: pd.DataFrame,
        question: str
    ) -> Dict[str, Any]:
        """Create bar chart data for aggregation results."""
        try:
            # Find categorical and numeric columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                return None
            
            # Use first categorical and numeric columns
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Group and aggregate
            grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
            
            return {
                'type': 'bar',
                'data': {
                    'x': grouped.index.tolist(),
                    'y': grouped.values.tolist(),
                    'title': f'{num_col} by {cat_col}'
                },
                'title': f'{num_col} by {cat_col}'
            }
            
        except Exception as e:
            logger.warning(f"Failed to create aggregation visualization: {e}")
            return None
    
    def _create_correlation_visualization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create heatmap data for correlation results."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) < 2:
                return None
            
            corr_matrix = df[numeric_cols].corr()
            
            return {
                'type': 'heatmap',
                'data': {
                    'matrix': corr_matrix.values.tolist(),
                    'labels': corr_matrix.columns.tolist(),
                    'title': 'Correlation Matrix'
                },
                'title': 'Correlation Matrix'
            }
            
        except Exception as e:
            logger.warning(f"Failed to create correlation visualization: {e}")
            return None
    
    def _create_table_visualization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create table data for general results."""
        try:
            return {
                'type': 'table',
                'data': {
                    'columns': df.columns.tolist(),
                    'rows': df.head(20).to_dict('records'),
                    'title': 'Data Table'
                },
                'title': 'Data Table'
            }
            
        except Exception as e:
            logger.warning(f"Failed to create table visualization: {e}")
            return None
    
    def _create_category_visualization(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Safe category aggregation fallback with deterministic results."""
        try:
            # Extract the metric from the question
            q = question.lower()
            metric = None
            
            if "users" in q and "Users" in df.columns:
                metric = "Users"
            elif "revenue" in q and "Revenue" in df.columns:
                metric = "Revenue"
            elif "growth" in q and "Growth_%" in df.columns:
                metric = "Growth_%"
            
            if metric and "Category" in df.columns:
                # Safe category aggregation - ensures ALL categories are included
                grouped = df.groupby("Category")[metric].sum().sort_values(ascending=False)
                
                return {
                    "type": "bar",
                    "data": {
                        "x": grouped.index.tolist(),
                        "y": grouped.values.tolist(),
                        "x_label": "Category",
                        "y_label": f"Total {metric}",
                        "title": f"{metric} by Category"
                    },
                    "title": f"{metric} by Category"
                }
            else:
                # Fallback to table if no valid metric found
                return self._create_table_visualization(df)
                
        except Exception as e:
            logger.warning(f"Failed to create category visualization: {e}")
            return self._create_table_visualization(df)
    
    def _extract_generated_code(self) -> Optional[str]:
        """Extract generated code from callback handler."""
        if hasattr(self.callback_handler, 'actions'):
            code_parts = []
            for action in self.callback_handler.actions:
                if hasattr(action, 'tool_input') and isinstance(action.tool_input, str):
                    code_parts.append(action.tool_input)
            return '\n'.join(code_parts) if code_parts else None
        return None
    
# REMOVED: Fallback processing function - LLM agent is now mandatory
    
    def is_available(self) -> bool:
        """Check if LLM agent is available."""
        available = self.agent is not None and self.llm is not None
        logger.info(f"LLM agent availability check: agent={self.agent is not None}, llm={self.llm is not None}, available={available}")
        return available
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            'available': self.is_available(),
            'llm_provider': settings.get_llm_provider(),
            'max_tokens': settings.max_tokens_llm,
            'agent_type': 'pandas_dataframe_agent'
        }


# Global LLM agent instance
llm_agent: Optional[LLMAgent] = None


def initialize_llm_agent() -> LLMAgent:
    """Initialize the global LLM agent."""
    global llm_agent
    llm_agent = LLMAgent()
    return llm_agent


def get_llm_agent() -> LLMAgent:
    """Get the global LLM agent instance."""
    if llm_agent is None:
        raise RuntimeError("LLM agent not initialized. Call initialize_llm_agent() first.")
    return llm_agent


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    
    # Test LLM agent
    agent = LLMAgent()
    
    # Create test data
    df = pd.DataFrame({
        'Category': ['Education', 'Entertainment', 'Finance'],
        'Revenue': [1000, 1500, 1200],
        'Users': [100, 150, 120]
    })
    
    # Test agent processing
    result = agent.process_with_agent(
        df=df,
        question="What is the total revenue by category?",
        context="This is sales data"
    )
    
    print(f"Agent available: {agent.is_available()}")
    print(f"Result: {result['answer']}")
    print(f"Success: {result['success']}")
    print(f"Agent info: {agent.get_agent_info()}")
