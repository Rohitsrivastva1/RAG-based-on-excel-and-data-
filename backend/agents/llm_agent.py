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
        # Add required attributes for LangChain compatibility
        self.ignore_chain = False
        self.raise_error = False
    
    def on_agent_action(self, action, **kwargs) -> None:
        """Log agent actions."""
        self.actions.append(action)
        print(f"🎯 AGENT ACTION: {getattr(action, 'tool', 'unknown')} - {getattr(action, 'tool_input', 'unknown')}")
        logger.info(f"Agent action: {getattr(action, 'tool', 'unknown')} - {getattr(action, 'tool_input', 'unknown')}")
    
    def on_agent_finish(self, finish, **kwargs) -> None:
        """Log agent finish."""
        print(f"🏁 AGENT FINISHED: {getattr(finish, 'return_values', 'unknown')}")
        logger.info(f"Agent finished: {getattr(finish, 'return_values', 'unknown')}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Log tool start."""
        print(f"🔧 TOOL STARTED: {serialized.get('name', 'unknown')} - Input: {input_str[:100]}...")
        logger.info(f"Tool started: {serialized.get('name', 'unknown')}")
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Log tool end."""
        print(f"✅ TOOL ENDED: Output: {output[:200]}...")
        logger.info(f"Tool output: {output[:200]}...")  # Truncate long outputs
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Log chain start."""
        print(f"⛓️ CHAIN STARTED: {serialized.get('name', 'unknown')} - Inputs: {list(inputs.keys())}")
        logger.info(f"Chain started: {serialized.get('name', 'unknown')}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Log chain end."""
        print(f"🔚 CHAIN ENDED: Outputs: {list(outputs.keys())}")
        logger.info(f"Chain ended with outputs: {list(outputs.keys())}")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Log LLM start."""
        print(f"🧠 LLM STARTED: {len(prompts)} prompts - Preview: {prompts[0][:100] if prompts else 'No prompts'}...")
        logger.info(f"LLM started with {len(prompts)} prompts")
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Log LLM end."""
        print(f"🧠 LLM COMPLETED: Response type: {type(response)}")
        logger.info(f"LLM completed")


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
                allow_dangerous_code=True  # Required for pandas agent execution
            )
            
            logger.info("Created LLM agent successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {e}")
    
    @staticmethod
    def extract_output(result: dict) -> str:
        """
        Extracts and returns only the 'output' value 
        from the given result dictionary.
        """
        return result.get("output", "")

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
        print(f"\n🤖 LLM AGENT PROCESSING START")
        print(f"📊 Input DataFrame shape: {df.shape}")
        print(f"❓ Original question: '{question}'")
        print(f"📝 Context: '{context}'")
        
        if not self.agent:
            print("❌ ERROR: LLM agent not available")
            raise RuntimeError("LLM agent not available. Agent creation failed.")
        
        try:
            start_time = datetime.utcnow()
            print(f"⏰ Started processing at: {start_time}")
            
            # Create new agent with the actual DataFrame
            print(f"🔧 Creating pandas dataframe agent...")
            print(f"   - DataFrame shape: {df.shape}")
            print(f"   - Columns: {list(df.columns)}")
            print(f"   - Data types: {dict(df.dtypes)}")
            
            agent = create_pandas_dataframe_agent(
                llm=self.llm,
                df=df,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                max_iterations=3,
                early_stopping_method="generate",
                allow_dangerous_code=True  # Required for pandas agent execution
            )

            print(f"agent: {agent}")
            print(f"✅ Agent created successfully")
            
            # Prepare enhanced question with context
            print(f"📝 Enhancing question with data context...")
            enhanced_question = self._enhance_question(question, context, df)
            print(f"📝 Enhanced question length: {len(enhanced_question)} characters")
            print(f"📝 Enhanced question preview: {enhanced_question[:200]}...")
            print(f"enhanced question: {enhanced_question}")
            # Use invoke instead of deprecated run method
            print(f"🚀 Invoking agent with enhanced question...")
            result = agent.invoke({"input": enhanced_question}, callbacks=[self.callback_handler])
            print(f"✅ Agent completed processing")
            print(f"📤 Raw result type: {type(result)}")
            print(f"📤 Raw result: {result}")
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            print(f"⏱️ Processing duration: {duration:.2f} seconds")
            
            log_performance("llm_agent_process", duration * 1000,
                          question_length=len(question),
                          df_shape=df.shape)
            
            # Determine if visualization is needed
            print(f"🎨 Determining visualization needs...")
            visualization = self._determine_visualization(question, result, df)
            print(f"🎨 Visualization result: {visualization}")
            
            final_result = {
                'answer': str(LLMAgent.extract_output(result)),
                'query_type': QueryType.LLM_AGENT.value,
                'generated_code': self._extract_generated_code(),
                'visualization': visualization,
                'confidence': 0.8,
                'processing_time_ms': duration * 1000,
                'success': True
            }
            
            print(f"✅ LLM AGENT PROCESSING COMPLETE")
            print(f"📤 Final result keys: {list(final_result.keys())}")
            print(f"📤 Answer preview: {str(result)[:100]}...")
            
            # Post-process to extract visualization from answer if needed
            if 'pie' in question.lower() or 'pie chart' in question.lower():
                print(f"🔍 Post-processing answer for pie chart data...")
                viz_from_answer = self._build_visualization_from_answer(final_result['answer'], question)
                if viz_from_answer:
                    # Always replace visualization for pie charts to avoid garbage values
                    final_result['visualization'] = viz_from_answer
                    print(f"✅ Post-processed visualization (replaced): {viz_from_answer}")
                else:
                    print(f"⚠️ Could not extract pie chart data from answer")
            
            return final_result
            
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
        print(f"\n📝 ENHANCING QUESTION")
        print(f"   Original question: '{question}'")
        print(f"   Context: '{context}'")
        print(f"   DataFrame shape: {df.shape}")
        
        enhanced = question
        
        if context:
            enhanced = f"Context: {context}\n\nQuestion: {question}"
            print(f"   Added context to question")
        
        # Add basic dataset information (no sample data to avoid confusion)
        print(f"   Adding dataset information...")
        data_info = f"\n\nDATASET INFORMATION:\n"
        data_info += f"Total rows: {len(df)}\n"
        data_info += f"Total columns: {len(df.columns)}\n"
        data_info += f"Column names: {', '.join(df.columns.tolist())}\n"
        
        # Add data types
        print(f"   Adding data types...")
        data_info += f"Data types:\n"
        for col, dtype in df.dtypes.items():
            data_info += f"  {col}: {dtype}\n"
        
        # Add basic statistics for numeric columns (no sample data)
        print(f"   Adding numeric statistics...")
        numeric_cols = df.select_dtypes(include=['number']).columns
        print(f"   Found {len(numeric_cols)} numeric columns: {list(numeric_cols)}")
        
        if len(numeric_cols) > 0:
            data_info += f"\nNUMERIC STATISTICS:\n"
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                data_info += f"  {col}: min={min_val:.2f}, max={max_val:.2f}, mean={mean_val:.2f}\n"
                print(f"     {col}: min={min_val:.2f}, max={max_val:.2f}, mean={mean_val:.2f}")
        
        enhanced += data_info
        
        # Add strict instructions with conversational elements
        print(f"   Adding instructions...")
        instructions = "\n\nIMPORTANT INSTRUCTIONS:\n"
        instructions += "1. You have access to the FULL DataFrame - use df.column_name to access any column\n"
        instructions += "2. Use only safe pandas operations (df.column_name, df.groupby(), etc.)\n"
        instructions += "3. Be precise and accurate in your analysis\n"
        instructions += "4. If asked about specific values, check if they exist in the data first\n"
        instructions += "5. When aggregating data (sum, count, average), make sure to include ALL rows\n"
        instructions += "6. For category-based queries, group by the correct column and aggregate properly\n"
        instructions += "7. Return data in a clear, structured format\n"
        instructions += "8. Do not use plotting libraries - return data suitable for visualization\n"
        instructions += "9. Always verify your calculations against the provided data\n"
        instructions += "10. If asked about 'strongest' or 'highest', use max() function\n"
        instructions += "11. If asked about 'weakest' or 'lowest', use min() function\n"
        instructions += "12. If asked about counts, use len() or count() function\n"
        instructions += "13. The DataFrame is available as 'df' - you can use df.head(), df.tail(), df.describe(), etc.\n\n"
        
        instructions += "CONVERSATIONAL GUIDELINES:\n"
        instructions += "1. GREETINGS: If the question starts with 'hello', 'hi', 'hey', respond warmly like 'Hello! I'm here to help you analyze your data.'\n"
        instructions += "2. VALIDATION: Acknowledge the user's question positively, e.g., 'Great question!', 'I can help you with that!', 'Let me analyze that for you.'\n"
        instructions += "3. FRUSTRATION HANDLING: If the question seems frustrated or confused, be empathetic: 'I understand this might be confusing. Let me help clarify...'\n"
        instructions += "4. THANK YOU: If the question contains 'thank', 'thanks', 'appreciate', respond graciously: 'You're welcome!', 'Happy to help!', 'My pleasure!'\n"
        instructions += "5. CLARIFICATION: If the question is unclear, ask for clarification: 'Could you please clarify what specific information you're looking for?'\n"
        instructions += "6. ENCOURAGEMENT: When providing results, be encouraging: 'Here's what I found:', 'Great news!', 'Perfect! Here are the results:'\n"
        instructions += "7. ASKING NAME: If the question is asking for the name of you and want to know about yourself, respond with the name of the your name i.e Lunex and you are here to help them with their data analysis.'\n"
        instructions += "8. BE FRIENDLY and supportive throughout the conversation while maintaining professionalism.\n"
        instructions += "9. If you can't find the requested data, explain what you found instead and suggest alternatives.\n"
        instructions += "10. Use conversational language that makes the user feel supported and understood."
        
        enhanced += instructions
        
        print(f"   Enhanced question length: {len(enhanced)} characters")
        print(f"   Enhanced question preview: {enhanced[:300]}...")
        print(f"✅ QUESTION ENHANCEMENT COMPLETE")
        
        return enhanced
    
    def _determine_visualization(
        self,
        question: str,
        result: str,
        df: pd.DataFrame
    ) -> Optional[Dict[str, Any]]:
        """Improved visualization logic with priority system."""
        print(f"\n🎨 DETERMINING VISUALIZATION")
        print(f"   Question: '{question}'")
        print(f"   Result type: {type(result)}")
        print(f"   Result preview: {str(result)[:200]}...")
        print(f"   DataFrame columns: {list(df.columns)}")
        print(f"   DataFrame shape: {df.shape}")
        
        q = question.lower()
        
        # Enhanced visualization keywords
        viz_keywords = [
            'chart', 'graph', 'plot', 'visualize', 'show', 'display',
            'bar', 'line', 'pie', 'scatter', 'histogram', 'heatmap',
            'create', 'generate', 'make', 'draw'
        ]
        has_viz_keywords = any(keyword in q for keyword in viz_keywords)
        print(f"   Has visualization keywords: {has_viz_keywords}")
        print(f"   Keywords found: {[kw for kw in viz_keywords if kw in q]}")
        
        # Also check if the result suggests visualization
        result_lower = str(result).lower()
        has_aggregation = any(term in result_lower for term in ['groupby', 'sum()', 'mean()', 'count()', 'total', 'average'])
        print(f"   Result suggests aggregation: {has_aggregation}")
        
        if not has_viz_keywords and not has_aggregation:
            print(f"   ❌ No visualization keywords or aggregation found, returning None")
            return None
        
        try:
            print(f"   🔍 Checking for specific chart types...")
            
            # 🔹 Force explicit visualization request (HIGHEST PRIORITY)
            if "bar" in q or "bar chart" in q or "bar graph" in q:
                print(f"   📊 Bar chart requested")
                viz = self._create_category_visualization(df, question)
                print(f"   📊 Bar chart result: {viz}")
                return viz
            
            if "line" in q or "trend" in q or "over time" in q:
                print(f"   📈 Line chart requested")
                viz = self._create_line_chart_visualization(df, question)
                print(f"   📈 Line chart result: {viz}")
                return viz
            
            if "pie" in q or "pie chart" in q:
                print(f"   🥧 Pie chart requested")
                viz = self._create_pie_chart_visualization(df, question, str(result))
                print(f"   🥧 Pie chart result: {viz}")
                return viz
            
            if "heatmap" in q or "correlation" in q:
                print(f"   🔥 Heatmap requested")
                viz = self._create_correlation_visualization(df)
                print(f"   🔥 Heatmap result: {viz}")
                return viz
            
            # Fallbacks (LOWER PRIORITY)
            print(f"   🔍 Checking result for aggregation patterns...")
            if "groupby" in str(result).lower() or "sum()" in str(result).lower():
                print(f"   📊 Aggregation detected in result")
                viz = self._create_aggregation_visualization(df, question)
                print(f"   📊 Aggregation visualization: {viz}")
                return viz
            
            if "corr" in str(result).lower():
                print(f"   🔥 Correlation detected in result")
                viz = self._create_correlation_visualization(df)
                print(f"   🔥 Correlation visualization: {viz}")
                return viz
            
            # Default fallback
            print(f"   📋 Using default table visualization")
            viz = self._create_table_visualization(df)
            print(f"   📋 Table visualization: {viz}")
            return viz
                
        except Exception as e:
            print(f"   ❌ Failed to create visualization: {e}")
            logger.warning(f"Failed to create visualization: {e}")
            return None
    
    def _create_aggregation_visualization(
        self,
        df: pd.DataFrame,
        question: str
    ) -> Dict[str, Any]:
        """Create bar chart data for aggregation results with intelligent column detection."""
        try:
            print(f"   🔍 Creating aggregation visualization for question: '{question}'")
            
            # Find categorical and numeric columns
            categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            print(f"   📊 Categorical columns: {categorical_cols}")
            print(f"   📊 Numeric columns: {numeric_cols}")
            
            if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                print(f"   ❌ No categorical or numeric columns found")
                return None
            
            # Try to extract columns from question
            q = question.lower()
            cat_col = None
            num_col = None
            
            # Find category column from question
            for col in categorical_cols:
                if col.lower() in q:
                    cat_col = col
                    break
            
            # Find numeric column from question
            for col in numeric_cols:
                if col.lower() in q:
                    num_col = col
                    break
            
            # Fallback to first available columns
            if not cat_col:
                cat_col = categorical_cols[0]
            if not num_col:
                num_col = numeric_cols[0]
            
            print(f"   📊 Using category: '{cat_col}', numeric: '{num_col}'")
            
            # Group and aggregate
            grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
            print(f"   📊 Grouped data: {grouped.head()}")
            
            return {
                'type': 'bar',
                'data': {
                    'x': grouped.index.tolist(),
                    'y': grouped.values.tolist(),
                    'x_label': cat_col,
                    'y_label': f'Total {num_col}',
                    'title': f'{num_col} by {cat_col}'
                },
                'title': f'{num_col} by {cat_col}'
            }
            
        except Exception as e:
            print(f"   ❌ Failed to create aggregation visualization: {e}")
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
    
    def _create_line_chart_visualization(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Create line chart data for trends over time."""
        try:
            print(f"   🔍 Creating line chart visualization for question: '{question}'")
            print(f"   📊 Available columns: {list(df.columns)}")
            
            # Find date/time columns
            date_cols = df.select_dtypes(include=['datetime64', 'datetime']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            print(f"   📊 Date columns: {date_cols}")
            print(f"   📊 Numeric columns: {numeric_cols}")
            
            if len(date_cols) == 0 or len(numeric_cols) == 0:
                print(f"   ❌ No date or numeric columns found")
                return self._create_table_visualization(df)
            
            # Use first date and numeric columns
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            
            print(f"   📊 Using date: '{date_col}', numeric: '{numeric_col}'")
            
            # Sort by date and get data
            df_sorted = df.sort_values(date_col)
            dates = df_sorted[date_col].dt.strftime('%Y-%m-%d').tolist()
            values = df_sorted[numeric_col].tolist()
            
            return {
                "type": "line",
                "data": {
                    "x": dates,
                    "y": values,
                    "x_label": date_col,
                    "y_label": numeric_col,
                    "title": f"{numeric_col} over {date_col}"
                },
                "title": f"{numeric_col} over {date_col}"
            }
                
        except Exception as e:
            print(f"   ❌ Failed to create line chart visualization: {e}")
            logger.warning(f"Failed to create line chart visualization: {e}")
            return self._create_table_visualization(df)
    
    def _create_pie_chart_visualization(self, df: pd.DataFrame, question: str, llm_result: str = None) -> Dict[str, Any]:
        """Create pie chart data for category distribution using LLM calculated values."""
        try:
            print(f"   🔍 Creating pie chart visualization for question: '{question}'")
            print(f"   📊 Available columns: {list(df.columns)}")
            
            # Find categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            print(f"   📊 Categorical columns: {categorical_cols}")
            
            if len(categorical_cols) == 0:
                print(f"   ❌ No categorical columns found")
                return self._create_table_visualization(df)
            
            # Extract category column from question
            q = question.lower()
            category_col = None
            
            for col in categorical_cols:
                if col.lower() in q:
                    category_col = col
                    break
            
            # Fallback to first categorical column
            if not category_col:
                category_col = categorical_cols[0]
            
            print(f"   📊 Using category column: '{category_col}'")
            
            # Try to extract real counts from LLM result first
            labels = []
            values = []
            
            if llm_result:
                print(f"   🔍 Attempting to extract real counts from LLM result...")
                extracted_data = self._extract_counts_from_llm_result(llm_result, category_col)
                if extracted_data:
                    labels = extracted_data['labels']
                    values = extracted_data['values']
                    print(f"   ✅ Extracted real counts from LLM: {dict(zip(labels, values))}")
                else:
                    print(f"   ⚠️ Could not extract counts from LLM, falling back to DataFrame")
            
            # Fallback to DataFrame counting if LLM extraction failed
            if not labels or not values:
                print(f"   📊 Using DataFrame value counts as fallback...")
                value_counts = df[category_col].value_counts()
                labels = value_counts.index.tolist()
                values = value_counts.values.tolist()
                print(f"   📊 DataFrame value counts: {dict(zip(labels, values))}")
            
            return {
                "type": "pie",
                "data": {
                    "labels": labels,
                    "values": values,
                    "title": f"Distribution of {category_col}"
                },
                "title": f"Distribution of {category_col}"
            }
                
        except Exception as e:
            print(f"   ❌ Failed to create pie chart visualization: {e}")
            logger.warning(f"Failed to create pie chart visualization: {e}")
            return self._create_table_visualization(df)
    
    def _extract_counts_from_llm_result(self, llm_result: str, category_col: str) -> Optional[Dict[str, List]]:
        """Extract category counts from LLM result text."""
        try:
            import re
            import ast
            
            # First try to extract dictionary directly from the answer
            dict_data = self._extract_dict_from_answer(llm_result)
            if dict_data:
                print(f"   📊 Extracted dictionary from LLM: {dict_data}")
                # Sort by value descending
                sorted_items = sorted(dict_data.items(), key=lambda x: x[1], reverse=True)
                labels = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                return {"labels": labels, "values": values}
            
            # Fallback to pattern matching
            patterns = [
                rf'(\w+)\s*:\s*(\d+)',  # "Category: 1234"
                rf'(\w+)\s+(\d+)',      # "Category 1234"
                rf'(\w+)\s+(\d+\.?\d*)', # "Category 1234.5"
            ]
            
            extracted = {}
            
            for pattern in patterns:
                matches = re.findall(pattern, llm_result, re.IGNORECASE)
                for match in matches:
                    category = match[0].strip()
                    try:
                        value = int(float(match[1]))
                        extracted[category] = value
                    except ValueError:
                        continue
            
            if extracted:
                # Sort by value descending
                sorted_items = sorted(extracted.items(), key=lambda x: x[1], reverse=True)
                labels = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
                
                print(f"   📊 Extracted from LLM patterns: {extracted}")
                return {"labels": labels, "values": values}
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extracting counts from LLM result: {e}")
            return None
    
    def _extract_dict_from_answer(self, answer: str) -> Optional[Dict[str, int]]:
        """Extract dictionary from LLM answer text."""
        try:
            import re
            import ast
            
            # First try to extract pandas Series format (new format)
            pandas_data = self._extract_pandas_series_from_answer(answer)
            if pandas_data:
                print(f"   📊 Found pandas series in answer: {pandas_data}")
                return pandas_data
            
            # Then try dictionary patterns (old format)
            dict_patterns = [
                r"\{[^}]*'[^']*':\s*\d+[^}]*\}",  # {'key': value, 'key2': value2}
                r"\{[^}]*\"[^\"]*\":\s*\d+[^}]*\}",  # {"key": value, "key2": value2}
            ]
            
            for pattern in dict_patterns:
                matches = re.findall(pattern, answer)
                for match in matches:
                    try:
                        # Try to evaluate the dictionary
                        dict_data = ast.literal_eval(match)
                        if isinstance(dict_data, dict):
                            # Convert values to int if possible
                            result = {}
                            for k, v in dict_data.items():
                                try:
                                    result[str(k)] = int(float(v))
                                except (ValueError, TypeError):
                                    continue
                            if result:
                                print(f"   📊 Found dictionary in answer: {result}")
                                return result
                    except (ValueError, SyntaxError):
                        continue
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extracting dictionary from answer: {e}")
            return None
    
    def _extract_pandas_series_from_answer(self, answer: str) -> Optional[Dict[str, float]]:
        """Extract pandas Series format from LLM answer text."""
        try:
            import re
            
            # Look for pandas Series format like:
            # Category
            # Education        2500
            # Entertainment    2968
            # Finance          3964
            # Health           3055
            # Tech             2144
            # Name: Users, dtype: int64
            
            lines = answer.split('\n')
            result = {}
            in_series = False
            
            for line in lines:
                line = line.strip()
                
                # Check if we're starting a pandas series (look for header line followed by data)
                if line and not line.startswith('```') and not line.startswith('Name:') and not line.startswith('dtype:'):
                    # Check if this looks like a header (single word, no numbers)
                    if len(line.split()) == 1 and line.isalpha():
                        # Check if next lines contain data (word + number pattern)
                        next_lines = lines[lines.index(line) + 1:lines.index(line) + 4]  # Check next 3 lines
                        has_data = any(re.match(r'^[A-Za-z]+\s+[\d.]+$', l.strip()) for l in next_lines if l.strip())
                        if has_data:
                            in_series = True
                            continue
                
                # Skip empty lines and metadata
                if not line or 'Name:' in line or 'dtype:' in line:
                    continue
                
                # Extract category and value pairs
                if in_series:
                    # Pattern: "CategoryName    Value" or "CategoryName         Value" (supports floats)
                    match = re.match(r'^([A-Za-z]+)\s+([\d.]+)$', line)
                    if match:
                        category = match.group(1)
                        try:
                            value = float(match.group(2))
                            result[category] = value
                        except ValueError:
                            continue
                    else:
                        # Try more flexible pattern
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                category = parts[0]
                                value = float(parts[-1])  # Last part should be the number
                                result[category] = value
                            except (ValueError, IndexError):
                                continue
            
            # Only return if we found at least 2 categories (to avoid false positives)
            if len(result) >= 2:
                print(f"   📊 Extracted pandas series: {result}")
                return result
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extracting pandas series from answer: {e}")
            return None
    
    def _build_visualization_from_answer(self, answer: str, question: str) -> Optional[Dict[str, Any]]:
        """Build visualization from LLM answer when regular visualization fails."""
        try:
            print(f"   🔍 Building visualization from answer...")
            
            # Extract dictionary from answer
            dict_data = self._extract_dict_from_answer(answer)
            if not dict_data:
                print(f"   ❌ No dictionary found in answer")
                return None
            
            # Create pie chart visualization
            labels = list(dict_data.keys())
            values = list(dict_data.values())
            
            # Sort by values descending
            sorted_items = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
            labels = [item[0] for item in sorted_items]
            values = [item[1] for item in sorted_items]
            
            print(f"   📊 Created pie chart from answer: {dict(zip(labels, values))}")
            
            return {
                "type": "pie",
                "data": {
                    "labels": labels,
                    "values": values,
                    "title": "Distribution by Category"
                },
                "title": "Distribution by Category"
            }
            
        except Exception as e:
            print(f"   ❌ Error building visualization from answer: {e}")
            return None
    
    def _create_category_visualization(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Dynamic category aggregation with intelligent column detection."""
        try:
            print(f"   🔍 Creating category visualization for question: '{question}'")
            print(f"   📊 Available columns: {list(df.columns)}")
            
            # Find categorical columns (potential x-axis)
            categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
            print(f"   📊 Categorical columns: {categorical_cols}")
            
            # Find numeric columns (potential y-axis)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"   📊 Numeric columns: {numeric_cols}")
            
            if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                print(f"   ❌ No categorical or numeric columns found")
                return self._create_table_visualization(df)
            
            # Extract metric from question (more flexible)
            q = question.lower()
            metric = None
            category_col = None
            
            # Try to find metric column from question
            for col in numeric_cols:
                if col.lower() in q:
                    metric = col
                    break
            
            # Try to find category column from question
            for col in categorical_cols:
                if col.lower() in q:
                    category_col = col
                    break
            
            # Fallback to first available columns
            if not metric:
                metric = numeric_cols[0]
            if not category_col:
                category_col = categorical_cols[0]
            
            print(f"   📊 Using category: '{category_col}', metric: '{metric}'")
            
            # Create aggregation
            grouped = df.groupby(category_col)[metric].sum().sort_values(ascending=False)
            print(f"   📊 Grouped data: {grouped.head()}")
            
            return {
                "type": "bar",
                "data": {
                    "x": grouped.index.tolist(),
                    "y": grouped.values.tolist(),
                    "x_label": category_col,
                    "y_label": f"Total {metric}",
                    "title": f"{metric} by {category_col}"
                },
                "title": f"{metric} by {category_col}"
            }
                
        except Exception as e:
            print(f"   ❌ Failed to create category visualization: {e}")
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
