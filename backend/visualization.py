"""
Visualization engine for creating charts and dashboards
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

class VisualizationEngine:
    def __init__(self):
        self.supported_chart_types = ['bar', 'line', 'pie', 'scatter', 'kpi']
    
    async def create_visualization(self, data: List[Dict], question: str, suggested_chart_type: str) -> Dict:
        """Create visualization based on data and question"""
        try:
            if not data:
                return {"error": "No data available for visualization"}
            
            df = pd.DataFrame(data)
            
            # Determine the best chart type
            chart_type = self._determine_chart_type(df, question, suggested_chart_type)
            
            # Generate the chart
            chart_config = await self._generate_chart(df, chart_type, question)
            
            return {
                "chart_type": chart_type,
                "config": chart_config,
                "data_points": len(df)
            }
        
        except Exception as e:
            return {"error": f"Visualization creation failed: {str(e)}"}
    
    def _determine_chart_type(self, df: pd.DataFrame, question: str, suggested_type: str) -> str:
        """Determine the best chart type based on data and question"""
        if suggested_type in self.supported_chart_types:
            return suggested_type
        
        # Analyze data to determine chart type
        numeric_columns = df.select_dtypes(include=['number']).columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        # If we have 2 numeric columns, scatter plot might be good
        if len(numeric_columns) >= 2:
            return 'scatter'
        
        # If we have 1 numeric and 1 categorical, bar chart
        if len(numeric_columns) >= 1 and len(categorical_columns) >= 1:
            return 'bar'
        
        # If we have only categorical data, pie chart
        if len(numeric_columns) == 0 and len(categorical_columns) >= 1:
            return 'pie'
        
        # Default to bar chart
        return 'bar'
    
    async def _generate_chart(self, df: pd.DataFrame, chart_type: str, question: str) -> Dict:
        """Generate chart configuration"""
        try:
            if chart_type == 'bar':
                return self._create_bar_chart(df, question)
            elif chart_type == 'line':
                return self._create_line_chart(df, question)
            elif chart_type == 'pie':
                return self._create_pie_chart(df, question)
            elif chart_type == 'scatter':
                return self._create_scatter_chart(df, question)
            elif chart_type == 'kpi':
                return self._create_kpi_chart(df, question)
            else:
                return self._create_bar_chart(df, question)  # Default
        
        except Exception as e:
            raise Exception(f"Chart generation failed: {str(e)}")
    
    def _create_bar_chart(self, df: pd.DataFrame, question: str) -> Dict:
        """Create bar chart"""
        numeric_columns = df.select_dtypes(include=['number']).columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_columns) == 0 or len(categorical_columns) == 0:
            # Fallback: use first two columns
            if len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
            else:
                # Single column - create count chart
                x_col = df.columns[0]
                y_col = 'count'
                df = df[x_col].value_counts().reset_index()
                df.columns = [x_col, y_col]
        else:
            x_col = categorical_columns[0]
            y_col = numeric_columns[0]
        
        # Aggregate data if needed
        if len(df) > 20:  # Too many bars
            df = df.groupby(x_col)[y_col].sum().reset_index()
        
        fig = go.Figure(data=[
            go.Bar(
                x=df[x_col],
                y=df[y_col],
                name=y_col
            )
        ])
        
        fig.update_layout(
            title=question[:50] + "..." if len(question) > 50 else question,
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=False
        )
        
        return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
    
    def _create_line_chart(self, df: pd.DataFrame, question: str) -> Dict:
        """Create line chart"""
        numeric_columns = df.select_dtypes(include=['number']).columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        # Look for date/time columns
        date_columns = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower() or 'time' in col.lower():
                date_columns.append(col)
        
        if date_columns and numeric_columns:
            x_col = date_columns[0]
            y_col = numeric_columns[0]
        elif len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
        else:
            # Fallback to bar chart
            return self._create_bar_chart(df, question)
        
        fig = go.Figure(data=[
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col
            )
        ])
        
        fig.update_layout(
            title=question[:50] + "..." if len(question) > 50 else question,
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=False
        )
        
        return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
    
    def _create_pie_chart(self, df: pd.DataFrame, question: str) -> Dict:
        """Create pie chart"""
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_columns) == 0:
            # Use first column
            col = df.columns[0]
        else:
            col = categorical_columns[0]
        
        # Count values
        value_counts = df[col].value_counts().head(10)  # Limit to top 10
        
        fig = go.Figure(data=[
            go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                name=col
            )
        ])
        
        fig.update_layout(
            title=question[:50] + "..." if len(question) > 50 else question,
            showlegend=True
        )
        
        return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
    
    def _create_scatter_chart(self, df: pd.DataFrame, question: str) -> Dict:
        """Create scatter chart"""
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) < 2:
            # Fallback to bar chart
            return self._create_bar_chart(df, question)
        
        x_col = numeric_columns[0]
        y_col = numeric_columns[1]
        
        # Add color column if available
        color_col = None
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        if categorical_columns:
            color_col = categorical_columns[0]
        
        if color_col:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col)
        else:
            fig = px.scatter(df, x=x_col, y=y_col)
        
        fig.update_layout(
            title=question[:50] + "..." if len(question) > 50 else question,
            xaxis_title=x_col,
            yaxis_title=y_col
        )
        
        return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
    
    def _create_kpi_chart(self, df: pd.DataFrame, question: str) -> Dict:
        """Create KPI dashboard"""
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        if len(numeric_columns) == 0:
            # Fallback to bar chart
            return self._create_bar_chart(df, question)
        
        # Calculate KPIs
        kpis = []
        for col in numeric_columns:
            kpis.append({
                "name": col,
                "value": float(df[col].sum()),
                "type": "sum"
            })
            kpis.append({
                "name": f"{col} (Avg)",
                "value": float(df[col].mean()),
                "type": "average"
            })
        
        # Create a simple bar chart showing KPIs
        fig = go.Figure(data=[
            go.Bar(
                x=[kpi["name"] for kpi in kpis],
                y=[kpi["value"] for kpi in kpis],
                name="KPI Values"
            )
        ])
        
        fig.update_layout(
            title=question[:50] + "..." if len(question) > 50 else question,
            xaxis_title="Metrics",
            yaxis_title="Values",
            showlegend=False
        )
        
        return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
    
    def get_chart_suggestions(self, df: pd.DataFrame, question: str) -> List[str]:
        """Get suggested chart types based on data and question"""
        suggestions = []
        
        numeric_columns = df.select_dtypes(include=['number']).columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        
        # Time series suggestions
        if any(word in question.lower() for word in ['trend', 'over time', 'time series']):
            suggestions.append('line')
        
        # Comparison suggestions
        if any(word in question.lower() for word in ['compare', 'vs', 'versus']):
            suggestions.append('bar')
        
        # Distribution suggestions
        if any(word in question.lower() for word in ['distribution', 'breakdown', 'percentage']):
            suggestions.append('pie')
        
        # Correlation suggestions
        if any(word in question.lower() for word in ['correlation', 'relationship']):
            suggestions.append('scatter')
        
        # Data-based suggestions
        if len(numeric_columns) >= 2:
            suggestions.append('scatter')
        
        if len(numeric_columns) >= 1 and len(categorical_columns) >= 1:
            suggestions.append('bar')
        
        if len(categorical_columns) >= 1:
            suggestions.append('pie')
        
        # Remove duplicates and return
        return list(dict.fromkeys(suggestions))
