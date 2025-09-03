"""
LLM Agent with LangChain for intelligent query processing
Handles SQL generation, Pandas code execution, and visualization decisions
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

try:
    from langchain.agents import AgentType
    from langchain_community.llms import OpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.tools import Tool
    from langchain.agents import initialize_agent
    
    # Try different import paths for ChatOpenAI
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            from langchain.chat_models import ChatOpenAI
    
    # Try to import Gemini
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        GEMINI_AVAILABLE = True
    except ImportError:
        try:
            from langchain_community.llms import GooglePalm
            GEMINI_AVAILABLE = True
        except ImportError:
            GEMINI_AVAILABLE = False
    
    # Try different import paths for create_pandas_dataframe_agent
    try:
        from langchain_experimental.agents import create_pandas_dataframe_agent
    except ImportError:
        try:
            from langchain.agents import create_pandas_dataframe_agent
        except ImportError:
            create_pandas_dataframe_agent = None
    
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"Warning: LangChain not available. Using fallback. Error: {e}")
    # Create dummy classes for fallback
    class ChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass
    
    def create_pandas_dataframe_agent(*args, **kwargs):
        return None
    
    class AgentType:
        OPENAI_FUNCTIONS = "openai_functions"

from dotenv import load_dotenv
load_dotenv()

class LLMAgent:
    """LangChain agent for intelligent data analysis"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.initialize_llm()
    
    def initialize_llm(self):
        """Initialize the LLM - require either Gemini or OpenAI API key"""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain is not available. Please install required packages.")
        
        try:
            # Try Gemini first (often more accessible)
            gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "AIzaSyCJgEIxXGLiM7_m3TL0TMM81sd4tsNZTlU"
            if gemini_key and GEMINI_AVAILABLE:
                try:
                    # Use Gemini 1.5 Flash model
                    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                    self.llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=gemini_key,
                        temperature=0.1
                    )
                    print(f"✅ Initialized Gemini LLM with model: {model_name}")
                    return
                except Exception as e:
                    print(f"❌ Failed to initialize Gemini: {e}")
            
            # Try OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.llm = ChatOpenAI(
                    openai_api_key=openai_key,
                    model_name="gpt-3.5-turbo",
                    temperature=0.1
                )
                print("✅ Initialized OpenAI LLM")
            else:
                raise RuntimeError(
                    "❌ No valid API key found!\n"
                    "Please set one of these environment variables:\n"
                    "  - GOOGLE_API_KEY (for Gemini)\n"
                    "  - GEMINI_API_KEY (alternative for Gemini)\n"
                    "  - OPENAI_API_KEY (for OpenAI)\n\n"
                    "Get your API key from:\n"
                    "  - Gemini: https://makersuite.google.com/app/apikey\n"
                    "  - OpenAI: https://platform.openai.com/account/api-keys"
                )
        except Exception as e:
            print(f"❌ Error initializing LLM: {e}")
            raise
    
    def create_pandas_agent(self, df: pd.DataFrame) -> Any:
        """Create a pandas dataframe agent"""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain is not available. Please install required packages.")
        
        if not self.llm:
            raise RuntimeError("LLM is not initialized. Please configure API key.")
        
        try:
            # Create a custom agent that uses the existing DataFrame
            from langchain.agents import create_react_agent, AgentExecutor
            from langchain.tools import Tool
            from langchain.prompts import PromptTemplate
            
            # Create a custom tool that works with the existing DataFrame
            def pandas_tool(query: str) -> str:
                """Execute pandas operations on the existing DataFrame"""
                try:
                    # Prevent plotting operations
                    if any(plot_lib in query.lower() for plot_lib in ['matplotlib', 'plt.', 'seaborn', 'sns.', 'plotly', 'fig.', 'chart', 'graph']):
                        return "Error: Chart creation is not allowed. Please use pandas operations only for data analysis."
                    
                    # Execute the query in the context where df is available
                    # Make sure df is in the local scope
                    local_vars = {'df': df}
                    result = eval(query, {"__builtins__": {}}, local_vars)
                    return str(result)
                except Exception as e:
                    return f"Error: {str(e)}"
            
            # Create the tool
            pandas_tool_obj = Tool(
                name="pandas_analysis",
                description="Execute pandas operations on the DataFrame. Use 'df' to refer to the DataFrame. DO NOT create charts or visualizations - only data analysis operations.",
                func=pandas_tool
            )
            
            # Create a custom prompt that emphasizes using the existing DataFrame
            prompt = PromptTemplate.from_template(f"""
You are working with a pandas DataFrame called 'df' that is already loaded in memory.

The DataFrame has the following structure:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Sample data: {df.head().to_string()}

IMPORTANT: The DataFrame 'df' is already available. Do NOT create a new DataFrame.
Use the existing 'df' variable directly for all operations.

CRITICAL: DO NOT create charts, graphs, or visualizations. Only perform data analysis operations.

Question: {{input}}

Use the pandas_analysis tool to execute your operations on the existing DataFrame.
Always use 'df' to refer to the DataFrame.
Only perform data analysis - no plotting or visualization.

{{agent_scratchpad}}
""")
            
            # Create the agent
            agent = create_react_agent(
                llm=self.llm,
                tools=[pandas_tool_obj],
                prompt=prompt
            )
            
            # Create agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=[pandas_tool_obj],
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
            
            print("✅ Created custom pandas agent with existing DataFrame")
            return agent_executor
            
        except Exception as e:
            print(f"❌ Error creating custom agent: {e}")
            # Fallback to original method
            try:
                agent = create_pandas_dataframe_agent(
                    llm=self.llm,
                    df=df,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True,
                    handle_parsing_errors=True,
                    allow_dangerous_code=True,
                    max_iterations=3
                )
                print("✅ Created pandas dataframe agent (ZERO_SHOT_REACT_DESCRIPTION)")
                return agent
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                raise
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze query intent to determine processing approach"""
        query_lower = query.lower()
        
        intent = {
            "type": "unknown",
            "visualization": None,
            "aggregation": None,
            "filtering": None,
            "columns": []
        }
        
        # Determine query type
        if any(word in query_lower for word in ["show", "display", "plot", "chart", "graph", "visualize"]):
            intent["type"] = "visualization"
        elif any(word in query_lower for word in ["sum", "total", "average", "mean", "count", "max", "min"]):
            intent["type"] = "aggregation"
        elif any(word in query_lower for word in ["filter", "where", "find", "search"]):
            intent["type"] = "filtering"
        elif any(word in query_lower for word in ["types", "categories", "unique", "distinct"]):
            intent["type"] = "categorization"
        else:
            intent["type"] = "general"
        
        # Determine visualization type
        if ("chart" in query_lower or "graph" in query_lower or "plot" in query_lower or 
            "visualize" in query_lower or "show" in query_lower or "display" in query_lower):
            # Set visualization type based on context
            if "bar" in query_lower or "column" in query_lower:
                intent["visualization"] = "bar"
            elif "line" in query_lower or "trend" in query_lower:
                intent["visualization"] = "line"
            elif "pie" in query_lower or "donut" in query_lower:
                intent["visualization"] = "pie"
            elif "scatter" in query_lower:
                intent["visualization"] = "scatter"
            elif "histogram" in query_lower:
                intent["visualization"] = "histogram"
            else:
                # Default to bar chart for general chart requests
                intent["visualization"] = "bar"
        elif "bar" in query_lower or "column" in query_lower:
            intent["visualization"] = "bar"
        elif "line" in query_lower or "trend" in query_lower:
            intent["visualization"] = "line"
        elif "pie" in query_lower or "donut" in query_lower:
            intent["visualization"] = "pie"
        elif "scatter" in query_lower:
            intent["visualization"] = "scatter"
        elif "histogram" in query_lower:
            intent["visualization"] = "histogram"
        
        # Determine aggregation type
        if "sum" in query_lower or "total" in query_lower:
            intent["aggregation"] = "sum"
        elif "average" in query_lower or "mean" in query_lower:
            intent["aggregation"] = "mean"
        elif "count" in query_lower:
            intent["aggregation"] = "count"
        elif "max" in query_lower or "maximum" in query_lower:
            intent["aggregation"] = "max"
        elif "min" in query_lower or "minimum" in query_lower:
            intent["aggregation"] = "min"
        
        return intent
    
    def suggest_visualization(self, df: pd.DataFrame, query: str, result_data: Any = None) -> Dict[str, Any]:
        """Suggest appropriate visualization based on query and data"""
        intent = self.analyze_query_intent(query)
        
        # If visualization type is already determined
        if intent["visualization"]:
            return self.create_visualization(df, intent["visualization"], query, result_data)
        
        # Auto-suggest based on data characteristics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        if len(numeric_cols) == 1 and len(text_cols) >= 1:
            return self.create_visualization(df, "bar", query, result_data)
        elif len(numeric_cols) >= 2:
            return self.create_visualization(df, "scatter", query, result_data)
        elif len(text_cols) >= 1:
            return self.create_visualization(df, "pie", query, result_data)
        else:
            return self.create_visualization(df, "bar", query, result_data)
    
    def create_visualization(self, df: pd.DataFrame, chart_type: str, query: str, result_data: Any = None) -> Dict[str, Any]:
        """Create Plotly visualization"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            text_cols = df.select_dtypes(include=['object']).columns
            
            if chart_type == "bar":
                if len(text_cols) > 0 and len(numeric_cols) > 0:
                    # Smart column selection based on query
                    query_lower = query.lower()
                    
                    # Select x-axis column (categorical)
                    x_col = text_cols[0]  # Default to first text column
                    if "category" in query_lower:
                        x_col = "Category" if "Category" in text_cols else text_cols[0]
                    elif "date" in query_lower:
                        x_col = "Date" if "Date" in text_cols else text_cols[0]
                    
                    # Select y-axis column (numeric)
                    if "revenue" in query_lower:
                        y_col = "Revenue" if "Revenue" in numeric_cols else numeric_cols[0]
                    elif "users" in query_lower:
                        y_col = "Users" if "Users" in numeric_cols else numeric_cols[0]
                    elif "growth" in query_lower:
                        y_col = "Growth_%" if "Growth_%" in numeric_cols else numeric_cols[0]
                    else:
                        y_col = numeric_cols[0]
                    
                    # Group by categorical column
                    grouped = df.groupby(x_col)[y_col].sum().reset_index()
                    
                    fig = px.bar(
                        grouped, 
                        x=x_col, 
                        y=y_col,
                        title=f"{y_col} by {x_col}",
                        labels={x_col: x_col, y_col: y_col}
                    )
                else:
                    # Simple bar chart of numeric values
                    if len(numeric_cols) > 0:
                        y_col = numeric_cols[0]
                        fig = px.bar(
                            x=df.index, 
                            y=df[y_col],
                            title=f"{y_col} Values",
                            labels={'x': 'Index', 'y': y_col}
                        )
                    else:
                        return {"error": "No suitable data for bar chart"}
            
            elif chart_type == "line":
                if len(numeric_cols) > 0:
                    y_col = numeric_cols[0]
                    x_col = df.index if len(text_cols) == 0 else text_cols[0]
                    
                    fig = px.line(
                        df, 
                        x=x_col, 
                        y=y_col,
                        title=f"{y_col} Trend",
                        labels={x_col: x_col, y_col: y_col}
                    )
                else:
                    return {"error": "No suitable data for line chart"}
            
            elif chart_type == "pie":
                if len(text_cols) > 0:
                    cat_col = text_cols[0]
                    counts = df[cat_col].value_counts()
                    
                    fig = px.pie(
                        values=counts.values,
                        names=counts.index,
                        title=f"Distribution of {cat_col}"
                    )
                else:
                    return {"error": "No suitable data for pie chart"}
            
            elif chart_type == "scatter":
                if len(numeric_cols) >= 2:
                    x_col, y_col = numeric_cols[0], numeric_cols[1]
                    fig = px.scatter(
                        df, 
                        x=x_col, 
                        y=y_col,
                        title=f"{y_col} vs {x_col}",
                        labels={x_col: x_col, y_col: y_col}
                    )
                else:
                    return {"error": "No suitable data for scatter plot"}
            
            elif chart_type == "histogram":
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    fig = px.histogram(
                        df, 
                        x=col,
                        title=f"Distribution of {col}",
                        labels={col: col}
                    )
                else:
                    return {"error": "No suitable data for histogram"}
            
            else:
                return {"error": f"Unknown chart type: {chart_type}"}
            
            # Create clean chart data without binary encoding
            chart_data = {
                "data": [],
                "layout": {
                    "title": fig.layout.title.text if fig.layout.title else f"Chart for: {query}",
                    "paper_bgcolor": 'rgba(0,0,0,0)',
                    "plot_bgcolor": 'rgba(0,0,0,0)',
                    "font": {"color": '#ffffff'},
                    "xaxis": {
                        "title": fig.layout.xaxis.title.text if fig.layout.xaxis.title else "",
                        "color": '#ffffff',
                        "gridcolor": '#404040',
                        "linecolor": '#404040',
                        "tickcolor": '#ffffff'
                    },
                    "yaxis": {
                        "title": fig.layout.yaxis.title.text if fig.layout.yaxis.title else "",
                        "color": '#ffffff',
                        "gridcolor": '#404040',
                        "linecolor": '#404040',
                        "tickcolor": '#ffffff'
                    },
                    "legend": {
                        "bgcolor": 'rgba(0,0,0,0)',
                        "bordercolor": '#404040',
                        "font": {"color": '#ffffff'}
                    }
                }
            }
            
            # Extract data from the figure manually and ensure plain arrays
            for trace in fig.data:
                # Convert x and y data to plain Python lists
                x_data = []
                y_data = []
                
                if hasattr(trace, 'x') and trace.x is not None:
                    if hasattr(trace.x, 'tolist'):
                        x_data = trace.x.tolist()
                    elif hasattr(trace.x, '__iter__'):
                        x_data = list(trace.x)
                    else:
                        x_data = [trace.x]
                
                if hasattr(trace, 'y') and trace.y is not None:
                    if hasattr(trace.y, 'tolist'):
                        y_data = trace.y.tolist()
                    elif hasattr(trace.y, '__iter__'):
                        y_data = list(trace.y)
                    else:
                        y_data = [trace.y]
                
                clean_trace = {
                    "type": trace.type,
                    "x": x_data,
                    "y": y_data,
                    "name": trace.name if hasattr(trace, 'name') else "",
                    "hovertemplate": trace.hovertemplate if hasattr(trace, 'hovertemplate') else "",
                    "marker": {
                        "color": trace.marker.color if hasattr(trace.marker, 'color') else "#636efa"
                    }
                }
                chart_data["data"].append(clean_trace)
            
            return {
                "type": chart_type,
                "data": chart_data,
                "title": fig.layout.title.text if fig.layout.title else f"Chart for: {query}"
            }
            
        except Exception as e:
            return {"error": f"Error creating visualization: {str(e)}"}
    
    def process_with_agent(self, df: pd.DataFrame, query: str, context: str = "") -> Dict[str, Any]:
        """Process query using LangChain agent"""
        try:
            if not LANGCHAIN_AVAILABLE:
                raise RuntimeError("LangChain is not available. Please install required packages.")
            
            if not self.llm:
                raise RuntimeError("LLM is not initialized. Please configure API key.")
            
            # Create agent
            agent = self.create_pandas_agent(df)
            print(f"🔧 Agent created: {type(agent)}")
            print(f"🔧 Agent tools: {[tool.name for tool in agent.tools] if hasattr(agent, 'tools') else 'No tools'}")
            
            # Execute query
            try:
                # Use invoke instead of run (newer method)
                print(f"🚀 Invoking agent with query: {query[:200]}...")
                
                # Add instructions to prevent chart creation
                enhanced_query = f"""
IMPORTANT: You are working with a DataFrame called 'df' that contains the following data:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Sample data: {df.head().to_string()}

The DataFrame 'df' is already loaded and available. Do NOT create a new DataFrame.
Use the existing 'df' variable directly.

Question: {query}

CRITICAL INSTRUCTIONS:
- DO NOT try to create charts, graphs, or visualizations
- DO NOT use matplotlib, seaborn, plotly, or any plotting libraries
- DO NOT use plt.show(), fig.show(), or any display functions
- Just analyze the data and return insights as text
- Use pandas operations only for data analysis
- Return clean, concise answers without any plotting code
"""
                
                response = agent.invoke({"input": enhanced_query})
                print(f"🔍 Agent response type: {type(response)}")
                print(f"🔍 Agent response: {response}")
                
                # Check if response is empty or None
                if not response:
                    print("❌ Agent returned empty response")
                    raise Exception("Agent returned empty response")
                
                # Only use direct pandas execution if agent completely fails
                if hasattr(response, 'output') and not response.output:
                    print("🧪 Agent returned empty output, using direct pandas fallback...")
                    try:
                        # Simple fallback for common queries
                        if "how many rows" in query.lower() and "data" in query.lower():
                            direct_result = len(df)
                            print(f"🧪 Direct pandas result: {direct_result}")
                            response.output = str(direct_result)
                        elif "unique values" in query.lower() and "category" in query.lower():
                            direct_result = df['Category'].unique().tolist()
                            print(f"🧪 Direct pandas result: {direct_result}")
                            response.output = str(direct_result)
                        else:
                            # Generic fallback - just show basic info
                            response.output = f"Dataset has {len(df)} rows and {len(df.columns)} columns. Columns: {list(df.columns)}"
                    except Exception as e:
                        print(f"🧪 Direct pandas execution failed: {e}")
                        response.output = f"Error processing query: {str(e)}"
                
                # Handle different response types and extract clean answer
                if hasattr(response, 'output'):
                    # Extract just the output text, not the full dictionary
                    output = response.output
                    if isinstance(output, str):
                        response_text = output
                    elif isinstance(output, dict) and 'output' in output:
                        response_text = str(output['output'])
                    else:
                        response_text = str(output)
                elif hasattr(response, 'content'):
                    response_text = str(response.content)
                elif hasattr(response, 'text'):
                    response_text = str(response.text)
                elif isinstance(response, str):
                    response_text = response
                else:
                    response_text = str(response) if response else "No response generated"
                
                # If we still have the full dictionary, extract just the output
                if isinstance(response_text, str) and "'output':" in response_text:
                    import re
                    output_match = re.search(r"'output':\s*'([^']*)'", response_text)
                    if output_match:
                        response_text = output_match.group(1)
                    else:
                        # Try with double quotes
                        output_match = re.search(r'"output":\s*"([^"]*)"', response_text)
                        if output_match:
                            response_text = output_match.group(1)
                
                # Clean up the response - remove any extra formatting
                if response_text.startswith("'") and response_text.endswith("'"):
                    response_text = response_text[1:-1]
                if response_text.startswith('"') and response_text.endswith('"'):
                    response_text = response_text[1:-1]
                
                print("Rohit",response_text)
                # Try to parse JSON response for structured output
                try:
                    import json
                    import re
                    
                    # Extract JSON from markdown code blocks if present
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(1)
                    elif response_text.strip().startswith('{') and response_text.strip().endswith('}'):
                        json_text = response_text.strip()
                    else:
                        json_text = None
                    
                    if json_text:
                        json_response = json.loads(json_text)
                        if 'count' in json_response and 'explanation' in json_response:
                            response_text = f"{json_response['explanation']} (Count: {json_response['count']})"
                        elif 'result' in json_response and 'explanation' in json_response:
                            result = json_response['result']
                            if isinstance(result, dict):
                                if 'rows' in result and 'columns' in result:
                                    response_text = f"The dataset has {result['rows']} rows and {result['columns']} columns."
                                else:
                                    response_text = f"{json_response['explanation']} (Result: {result})"
                            else:
                                response_text = f"{json_response['explanation']} (Result: {result})"
                        else:
                            response_text = f"JSON response: {json_response}"
                except Exception as e:
                    print(f"⚠️ JSON parsing failed: {e}")
                    pass  # Keep original response if JSON parsing fails
            except Exception as e:
                print(f"❌ Error in agent execution: {e}")
                # Simple fallback for agent failures
                try:
                    if "how many rows" in query.lower() and "data" in query.lower():
                        response_text = f"The dataset has {len(df)} rows and {len(df.columns)} columns."
                    elif "unique values" in query.lower() and "category" in query.lower():
                        unique_values = df['Category'].unique().tolist()
                        response_text = f"Unique values in Category: {unique_values}"
                    elif "unique" in query.lower():
                        # Try to find the column mentioned
                        for col in df.columns:
                            if col.lower() in query.lower():
                                unique_values = df[col].unique().tolist()
                                response_text = f"Unique values in {col}: {unique_values}"
                                break
                        else:
                            response_text = f"Available columns: {list(df.columns)}"
                    else:
                        response_text = f"Agent failed to process query. Dataset has {len(df)} rows and {len(df.columns)} columns."
                except Exception as fallback_error:
                    response_text = f"Error processing query: {str(e)}"
            
            # Analyze intent and create visualization
            intent = self.analyze_query_intent(query)
            visualization = None
            
            if intent["type"] in ["visualization", "aggregation", "categorization"]:
                try:
                    visualization = self.suggest_visualization(df, query, response_text)
                except Exception as e:
                    print(f"❌ Error creating visualization: {e}")
                    visualization = None
            
            return {
                "answer": response_text,
                "query_type": "llm_agent",
                "visualization": visualization,
                "intent": intent
            }
            
        except Exception as e:
            print(f"❌ Error in LLM agent processing: {e}")
            raise RuntimeError(f"Failed to process query with LLM agent: {str(e)}")

# Global instance
llm_agent = LLMAgent()
