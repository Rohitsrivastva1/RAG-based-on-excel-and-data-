"""
Visualization engine for generating Plotly JSON charts.
Converts DataFrame results into interactive visualizations.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import re

try:
    from ..utils.types import ChartType
    from ..utils.serializer import clean_for_json
    from ..logging_config import get_logger, log_performance
except ImportError:
    from utils.types import ChartType
    from utils.serializer import clean_for_json
    from logging_config import get_logger, log_performance

logger = get_logger(__name__)

# Optional Plotly import
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.utils import PlotlyJSONEncoder
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly not available. Visualization features will be limited.")


class VisualizationEngine:
    """Engine for creating interactive visualizations from data."""
    
    def __init__(self):
        self.chart_templates = {
            'dark': {
                'layout': {
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': '#ffffff'},
                    'xaxis': {'color': '#ffffff', 'gridcolor': '#404040'},
                    'yaxis': {'color': '#ffffff', 'gridcolor': '#404040'}
                }
            },
            'light': {
                'layout': {
                    'paper_bgcolor': 'white',
                    'plot_bgcolor': '#f8f9fa',
                    'font': {'color': '#333333'},
                    'xaxis': {'color': '#333333', 'gridcolor': '#e0e0e0'},
                    'yaxis': {'color': '#333333', 'gridcolor': '#e0e0e0'}
                }
            }
        }
    
    def create_visualization(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        suggested_chart_type: Optional[str] = None,
        theme: str = 'dark'
    ) -> Optional[Dict[str, Any]]:
        """
        Create visualization from data based on question and suggested type.
        
        Args:
            data: DataFrame or data dictionary
            question: Original question that generated the data
            suggested_chart_type: Suggested chart type from LLM
            theme: Chart theme ('dark' or 'light')
            
        Returns:
            Visualization data dictionary or None
        """
        try:
            start_time = datetime.utcnow()
            
            # Determine chart type
            chart_type = self._determine_chart_type(data, question, suggested_chart_type)
            
            if chart_type is None:
                logger.warning("Could not determine appropriate chart type")
                return None
            
            # Create visualization based on type
            if chart_type == ChartType.BAR:
                viz_data = self._create_bar_chart(data, question, theme)
            elif chart_type == ChartType.LINE:
                viz_data = self._create_line_chart(data, question, theme)
            elif chart_type == ChartType.PIE:
                viz_data = self._create_pie_chart(data, question, theme)
            elif chart_type == ChartType.SCATTER:
                viz_data = self._create_scatter_chart(data, question, theme)
            elif chart_type == ChartType.HISTOGRAM:
                viz_data = self._create_histogram(data, question, theme)
            elif chart_type == ChartType.HEATMAP:
                viz_data = self._create_heatmap(data, question, theme)
            elif chart_type == ChartType.TABLE:
                viz_data = self._create_table(data, question, theme)
            else:
                logger.warning(f"Unsupported chart type: {chart_type}")
                return None
            
            if viz_data is None:
                return None
            
            # Add metadata
            viz_data['metadata'] = {
                'chart_type': chart_type.value,
                'question': question,
                'created_at': datetime.utcnow().isoformat(),
                'theme': theme
            }
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_performance("create_visualization", duration * 1000,
                          chart_type=chart_type.value,
                          theme=theme)
            
            logger.info(f"Created {chart_type.value} visualization", extra={
                'chart_type': chart_type.value,
                'theme': theme,
                'duration_ms': duration * 1000
            })
            
            return clean_for_json(viz_data)
            
        except Exception as e:
            logger.error(f"Failed to create visualization: {e}", exc_info=True)
            return None
    
    def _determine_chart_type(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        suggested_type: Optional[str]
    ) -> Optional[ChartType]:
        """Determine the best chart type based on data and question."""
        
        # Use suggested type if available and valid
        if suggested_type:
            try:
                return ChartType(suggested_type.lower())
            except ValueError:
                logger.warning(f"Invalid suggested chart type: {suggested_type}")
        
        # Analyze question for chart type hints
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['bar', 'column', 'compare', 'category']):
            return ChartType.BAR
        elif any(word in question_lower for word in ['line', 'trend', 'time', 'over time']):
            return ChartType.LINE
        elif any(word in question_lower for word in ['pie', 'proportion', 'percentage', 'share']):
            return ChartType.PIE
        elif any(word in question_lower for word in ['scatter', 'correlation', 'relationship']):
            return ChartType.SCATTER
        elif any(word in question_lower for word in ['histogram', 'distribution', 'frequency']):
            return ChartType.HISTOGRAM
        elif any(word in question_lower for word in ['heatmap', 'matrix', 'correlation matrix']):
            return ChartType.HEATMAP
        elif any(word in question_lower for word in ['table', 'list', 'show', 'display']):
            return ChartType.TABLE
        
        # Analyze data structure
        if isinstance(data, dict):
            # Check if it's already in chart format
            if 'x' in data and 'y' in data:
                return ChartType.BAR
            elif 'type' in data:
                try:
                    return ChartType(data['type'].lower())
                except ValueError:
                    pass
        
        elif isinstance(data, pd.DataFrame):
            # Analyze DataFrame structure
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                if len(categorical_cols) == 1 and len(numeric_cols) == 1:
                    return ChartType.BAR
                elif len(numeric_cols) >= 2:
                    return ChartType.SCATTER
            elif len(numeric_cols) >= 1:
                return ChartType.HISTOGRAM
            else:
                return ChartType.TABLE
        
        # Default to bar chart
        return ChartType.BAR
    
    def _create_bar_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a bar chart visualization."""
        try:
            if isinstance(data, dict):
                # Data is already in chart format
                x_data = data.get('x', [])
                y_data = data.get('y', [])
                title = data.get('title', 'Bar Chart')
            else:
                # Convert DataFrame to chart format
                df = data
                if df.empty:
                    return None
                
                # Find categorical and numeric columns
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                    return None
                
                # Use first categorical column for x-axis
                x_col = categorical_cols[0]
                # Use first numeric column for y-axis
                y_col = numeric_cols[0]
                
                # Group by categorical column and sum numeric column
                grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
                
                x_data = grouped.index.tolist()
                y_data = grouped.values.tolist()
                title = f"{y_col} by {x_col}"
            
            # Create Plotly figure if available
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Bar(
                        x=x_data,
                        y=y_data,
                        marker_color='#00d4aa',
                        marker_line_color='#00a8ff',
                        marker_line_width=1
                    )
                ])
                
                # Apply theme
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_data[0] if x_data else 'Category',
                    yaxis_title='Value',
                    **template['layout']
                )
                
                return {
                    'type': 'bar',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                # Fallback to simple format
                return {
                    'type': 'bar',
                    'data': {
                        'x': x_data,
                        'y': y_data,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create bar chart: {e}")
            return None
    
    def _create_line_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a line chart visualization."""
        try:
            if isinstance(data, dict):
                x_data = data.get('x', [])
                y_data = data.get('y', [])
                title = data.get('title', 'Line Chart')
            else:
                df = data
                if df.empty:
                    return None
                
                # Find numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    return None
                
                # Use index as x-axis if it's datetime-like
                if isinstance(df.index, pd.DatetimeIndex):
                    x_data = df.index.tolist()
                else:
                    x_data = list(range(len(df)))
                
                # Use first numeric column for y-axis
                y_col = numeric_cols[0]
                y_data = df[y_col].tolist()
                title = f"{y_col} over time"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='lines+markers',
                        line=dict(color='#00d4aa', width=2),
                        marker=dict(color='#00a8ff', size=6)
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    xaxis_title='Time',
                    yaxis_title='Value',
                    **template['layout']
                )
                
                return {
                    'type': 'line',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'line',
                    'data': {
                        'x': x_data,
                        'y': y_data,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create line chart: {e}")
            return None
    
    def _create_pie_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a pie chart visualization."""
        try:
            if isinstance(data, dict):
                labels = data.get('x', [])
                values = data.get('y', [])
                title = data.get('title', 'Pie Chart')
            else:
                df = data
                if df.empty:
                    return None
                
                # Find categorical and numeric columns
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                if len(categorical_cols) == 0 or len(numeric_cols) == 0:
                    return None
                
                # Group by categorical column and sum numeric column
                grouped = df.groupby(categorical_cols[0])[numeric_cols[0]].sum()
                
                labels = grouped.index.tolist()
                values = grouped.values.tolist()
                title = f"Distribution of {numeric_cols[0]}"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        marker_colors=['#00d4aa', '#00a8ff', '#ff6b6b', '#4ecdc4', '#45b7d1']
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    **template['layout']
                )
                
                return {
                    'type': 'pie',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'pie',
                    'data': {
                        'labels': labels,
                        'values': values,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create pie chart: {e}")
            return None
    
    def _create_scatter_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a scatter chart visualization."""
        try:
            if isinstance(data, dict):
                x_data = data.get('x', [])
                y_data = data.get('y', [])
                title = data.get('title', 'Scatter Chart')
            else:
                df = data
                if df.empty:
                    return None
                
                # Find numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) < 2:
                    return None
                
                x_data = df[numeric_cols[0]].tolist()
                y_data = df[numeric_cols[1]].tolist()
                title = f"{numeric_cols[1]} vs {numeric_cols[0]}"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='markers',
                        marker=dict(
                            color='#00d4aa',
                            size=8,
                            line=dict(color='#00a8ff', width=1)
                        )
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    xaxis_title=x_data[0] if x_data else 'X',
                    yaxis_title=y_data[0] if y_data else 'Y',
                    **template['layout']
                )
                
                return {
                    'type': 'scatter',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'scatter',
                    'data': {
                        'x': x_data,
                        'y': y_data,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create scatter chart: {e}")
            return None
    
    def _create_histogram(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a histogram visualization."""
        try:
            if isinstance(data, dict):
                values = data.get('y', [])
                title = data.get('title', 'Histogram')
            else:
                df = data
                if df.empty:
                    return None
                
                # Find numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    return None
                
                values = df[numeric_cols[0]].tolist()
                title = f"Distribution of {numeric_cols[0]}"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Histogram(
                        x=values,
                        marker_color='#00d4aa',
                        marker_line_color='#00a8ff',
                        marker_line_width=1
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    xaxis_title='Value',
                    yaxis_title='Frequency',
                    **template['layout']
                )
                
                return {
                    'type': 'histogram',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'histogram',
                    'data': {
                        'values': values,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create histogram: {e}")
            return None
    
    def _create_heatmap(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a heatmap visualization."""
        try:
            if isinstance(data, dict):
                # Assume data is in matrix format
                matrix = data.get('matrix', [])
                title = data.get('title', 'Heatmap')
            else:
                df = data
                if df.empty:
                    return None
                
                # Create correlation matrix for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) < 2:
                    return None
                
                matrix = df[numeric_cols].corr().values.tolist()
                title = "Correlation Matrix"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Heatmap(
                        z=matrix,
                        colorscale='Viridis'
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    **template['layout']
                )
                
                return {
                    'type': 'heatmap',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'heatmap',
                    'data': {
                        'matrix': matrix,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create heatmap: {e}")
            return None
    
    def _create_table(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        question: str,
        theme: str
    ) -> Optional[Dict[str, Any]]:
        """Create a table visualization."""
        try:
            if isinstance(data, dict):
                # Assume data is already in table format
                table_data = data.get('data', [])
                columns = data.get('columns', [])
                title = data.get('title', 'Table')
            else:
                df = data
                if df.empty:
                    return None
                
                # Convert DataFrame to table format
                table_data = df.head(100).to_dict('records')  # Limit to 100 rows
                columns = df.columns.tolist()
                title = f"Data Table ({len(df)} rows)"
            
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[
                    go.Table(
                        header=dict(
                            values=columns,
                            fill_color='#00d4aa',
                            font=dict(color='white', size=12),
                            align='left'
                        ),
                        cells=dict(
                            values=[[row.get(col, '') for col in columns] for row in table_data],
                            fill_color='#f8f9fa',
                            font=dict(color='#333333', size=11),
                            align='left'
                        )
                    )
                ])
                
                template = self.chart_templates.get(theme, self.chart_templates['dark'])
                fig.update_layout(
                    title=title,
                    **template['layout']
                )
                
                return {
                    'type': 'table',
                    'data': fig.to_dict(),
                    'title': title
                }
            else:
                return {
                    'type': 'table',
                    'data': {
                        'columns': columns,
                        'rows': table_data,
                        'title': title
                    },
                    'title': title
                }
                
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return None


# Global visualization engine instance
visualization_engine: Optional[VisualizationEngine] = None


def initialize_visualization_engine() -> VisualizationEngine:
    """Initialize the global visualization engine."""
    global visualization_engine
    visualization_engine = VisualizationEngine()
    return visualization_engine


def get_visualization_engine() -> VisualizationEngine:
    """Get the global visualization engine instance."""
    if visualization_engine is None:
        raise RuntimeError("Visualization engine not initialized. Call initialize_visualization_engine() first.")
    return visualization_engine


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd
    
    # Test visualization engine
    engine = VisualizationEngine()
    
    # Create test data
    df = pd.DataFrame({
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'Revenue': [1000, 1500, 1200, 800, 900],
        'Users': [100, 150, 120, 80, 90]
    })
    
    # Test bar chart
    viz = engine.create_visualization(df, "Show revenue by category", "bar")
    print(f"Bar chart created: {viz is not None}")
    
    # Test pie chart
    viz = engine.create_visualization(df, "Show distribution of revenue", "pie")
    print(f"Pie chart created: {viz is not None}")
    
    # Test with dict data
    dict_data = {
        'x': ['A', 'B', 'C'],
        'y': [10, 20, 15],
        'title': 'Test Chart'
    }
    viz = engine.create_visualization(dict_data, "Test chart", "bar")
    print(f"Dict chart created: {viz is not None}")
