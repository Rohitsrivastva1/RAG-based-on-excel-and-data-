# Visualization System Guide

## 📊 Understanding Chart Generation and Display

This guide explains how the RAG Analytics system automatically generates and displays interactive visualizations from your data queries.

## 🎯 Overview

The visualization system automatically:
- **Detects** when a user wants a chart
- **Analyzes** the data to determine the best chart type
- **Generates** interactive Plotly charts
- **Displays** them in the dark-themed interface
- **Provides** export options (CSV, PNG, PDF)

## 🔄 Visualization Flow

### 1. Query Analysis
The system analyzes user queries to detect visualization requests.

**Detection Logic:**
```python
def analyze_query_intent(self, query: str):
    intent = {
        "type": "general",
        "visualization": None,
        "aggregation": None
    }
    
    query_lower = query.lower()
    
    # Detect visualization requests
    if ("chart" in query_lower or "graph" in query_lower or 
        "plot" in query_lower or "visualize" in query_lower or
        "show" in query_lower or "display" in query_lower):
        intent["type"] = "visualization"
        
        # Determine specific chart type
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
            # Default to bar chart for general requests
            intent["visualization"] = "bar"
    
    return intent
```

### 2. Chart Type Selection
The system intelligently selects the most appropriate chart type.

**Selection Criteria:**
- **Bar Charts**: Categorical vs numerical data
- **Line Charts**: Time series or trend data
- **Pie Charts**: Part-to-whole relationships
- **Scatter Plots**: Correlation between two numerical variables
- **Histograms**: Distribution of single numerical variable

**Auto-Selection Logic:**
```python
def suggest_visualization(self, df: pd.DataFrame, query: str, result_data: Any = None):
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
```

### 3. Smart Column Selection
The system intelligently selects the right columns based on the user's query.

**Column Selection Logic:**
```python
def get_smart_columns(self, df: pd.DataFrame, query: str):
    """Select appropriate columns based on query context"""
    query_lower = query.lower()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=['object']).columns
    
    x_col = text_cols[0] if len(text_cols) > 0 else None
    
    # Smart y-column selection based on query
    if "revenue" in query_lower:
        y_col = "Revenue" if "Revenue" in numeric_cols else numeric_cols[0]
    elif "users" in query_lower:
        y_col = "Users" if "Users" in numeric_cols else numeric_cols[0]
    elif "growth" in query_lower:
        y_col = "Growth_%" if "Growth_%" in numeric_cols else numeric_cols[0]
    else:
        y_col = numeric_cols[0] if len(numeric_cols) > 0 else None
    
    return x_col, y_col
```

## 🎨 Chart Generation

### 1. Bar Chart Creation
Bar charts are the most common visualization type.

**Implementation:**
```python
def create_bar_chart(self, df: pd.DataFrame, query: str):
    """Create a bar chart from DataFrame"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=['object']).columns
    
    if len(text_cols) > 0 and len(numeric_cols) > 0:
        x_col = text_cols[0]
        
        # Smart column selection based on query
        query_lower = query.lower()
        if "revenue" in query_lower:
            y_col = "Revenue" if "Revenue" in numeric_cols else numeric_cols[0]
        elif "users" in query_lower:
            y_col = "Users" if "Users" in numeric_cols else numeric_cols[0]
        else:
            y_col = numeric_cols[0]
        
        # Group by categorical column
        grouped = df.groupby(x_col)[y_col].sum().reset_index()
        
        # Create Plotly figure
        fig = px.bar(
            grouped, 
            x=x_col, 
            y=y_col,
            title=f"{y_col} by {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
        
        return fig
```

### 2. Pie Chart Creation
Pie charts show part-to-whole relationships.

**Implementation:**
```python
def create_pie_chart(self, df: pd.DataFrame, query: str):
    """Create a pie chart from DataFrame"""
    text_cols = df.select_dtypes(include=['object']).columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(text_cols) > 0:
        cat_col = text_cols[0]
        
        if len(numeric_cols) > 0:
            # Use numerical column for values
            val_col = numeric_cols[0]
            grouped = df.groupby(cat_col)[val_col].sum()
            
            fig = px.pie(
                values=grouped.values,
                names=grouped.index,
                title=f"Distribution of {val_col} by {cat_col}"
            )
        else:
            # Use counts for categorical data
            counts = df[cat_col].value_counts()
            
            fig = px.pie(
                values=counts.values,
                names=counts.index,
                title=f"Distribution of {cat_col}"
            )
        
        return fig
```

### 3. Line Chart Creation
Line charts show trends over time or continuous data.

**Implementation:**
```python
def create_line_chart(self, df: pd.DataFrame, query: str):
    """Create a line chart from DataFrame"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col,
            title=f"{y_col} vs {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
    elif len(text_cols) > 0 and len(numeric_cols) > 0:
        # Group by categorical column
        x_col = text_cols[0]
        y_col = numeric_cols[0]
        grouped = df.groupby(x_col)[y_col].sum().reset_index()
        
        fig = px.line(
            grouped, 
            x=x_col, 
            y=y_col,
            title=f"{y_col} by {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
    
    return fig
```

### 4. Scatter Plot Creation
Scatter plots show relationships between two numerical variables.

**Implementation:**
```python
def create_scatter_plot(self, df: pd.DataFrame, query: str):
    """Create a scatter plot from DataFrame"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col,
            title=f"{y_col} vs {x_col}",
            labels={x_col: x_col, y_col: y_col}
        )
        
        return fig
```

## 🎨 Dark Theme Integration

### 1. Chart Styling
All charts are automatically styled with the dark theme.

**Dark Theme Configuration:**
```python
def apply_dark_theme(self, fig):
    """Apply dark theme to Plotly figure"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',      # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',       # Transparent plot area
        font={'color': '#ffffff'},           # White text
        xaxis={
            'color': '#ffffff',              # White axis text
            'gridcolor': '#404040',          # Dark grid lines
            'linecolor': '#404040',          # Dark axis lines
            'tickcolor': '#ffffff'           # White tick marks
        },
        yaxis={
            'color': '#ffffff',              # White axis text
            'gridcolor': '#404040',          # Dark grid lines
            'linecolor': '#404040',          # Dark axis lines
            'tickcolor': '#ffffff'           # White tick marks
        },
        legend={
            'bgcolor': 'rgba(0,0,0,0)',     # Transparent legend background
            'bordercolor': '#404040',        # Dark legend border
            'font': {'color': '#ffffff'}     # White legend text
        }
    )
    
    return fig
```

### 2. Color Schemes
Charts use colors that work well with the dark theme.

**Color Configuration:**
```python
# Default Plotly colors that work with dark theme
colorway = [
    "#636efa",  # Blue
    "#EF553B",  # Red
    "#00cc96",  # Green
    "#ab63fa",  # Purple
    "#FFA15A",  # Orange
    "#19d3f3",  # Cyan
    "#FF6692",  # Pink
    "#B6E880",  # Light Green
    "#FF97FF",  # Magenta
    "#FECB52"   # Yellow
]

# Apply to figure
fig.update_layout(colorway=colorway)
```

## 📤 Data Export and JSON Generation

### 1. Clean JSON Generation
The system generates clean JSON without binary encoding issues.

**JSON Generation:**
```python
def create_clean_chart_data(self, fig):
    """Create clean chart data without binary encoding"""
    chart_data = {
        "data": [],
        "layout": {
            "title": fig.layout.title.text if fig.layout.title else "Chart",
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
    
    # Extract data from the figure manually
    for trace in fig.data:
        clean_trace = {
            "type": trace.type,
            "x": trace.x.tolist() if hasattr(trace.x, 'tolist') else list(trace.x),
            "y": trace.y.tolist() if hasattr(trace.y, 'tolist') else list(trace.y),
            "name": trace.name if hasattr(trace, 'name') else "",
            "hovertemplate": trace.hovertemplate if hasattr(trace, 'hovertemplate') else "",
            "marker": {
                "color": trace.marker.color if hasattr(trace.marker, 'color') else "#636efa"
            }
        }
        chart_data["data"].append(clean_trace)
    
    return chart_data
```

### 2. Export Functionality
The system provides multiple export options.

**Export Options:**
```python
def export_chart(self, chart_data: dict, format: str):
    """Export chart in various formats"""
    if format == "csv":
        return self.export_to_csv(chart_data)
    elif format == "png":
        return self.export_to_png(chart_data)
    elif format == "pdf":
        return self.export_to_pdf(chart_data)
    else:
        raise ValueError(f"Unsupported export format: {format}")

def export_to_csv(self, chart_data: dict):
    """Export chart data as CSV"""
    data = chart_data["data"][0]  # Get first trace
    df = pd.DataFrame({
        data["x"][0]: data["x"],  # X-axis data
        data["y"][0]: data["y"]   # Y-axis data
    })
    return df.to_csv(index=False)

def export_to_png(self, chart_data: dict):
    """Export chart as PNG image"""
    fig = go.Figure(chart_data)
    return fig.to_image(format="png", width=800, height=600)

def export_to_pdf(self, chart_data: dict):
    """Export chart as PDF"""
    fig = go.Figure(chart_data)
    return fig.to_image(format="pdf", width=800, height=600)
```

## 🖥️ Frontend Integration

### 1. Visualization Component
The React component displays the charts.

**Component Structure:**
```javascript
const Visualization = ({ sessionId }) => {
  const [visualizations, setVisualizations] = useState([]);
  const [currentViz, setCurrentViz] = useState(null);

  // Listen for new visualizations from chat interface
  useEffect(() => {
    const handleStorageChange = () => {
      const latestViz = localStorage.getItem(`viz_${sessionId}`);
      if (latestViz) {
        const vizData = JSON.parse(latestViz);
        setVisualizations(prev => [vizData, ...prev]);
        setCurrentViz(vizData);
        localStorage.removeItem(`viz_${sessionId}`);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [sessionId]);
```

### 2. Chart Rendering
Charts are rendered using Plotly.js with dark theme.

**Chart Rendering:**
```javascript
const renderVisualization = (vizData) => {
  if (!vizData || !vizData.config) {
    return <Empty description="No visualization data available" />;
  }

  const config = typeof vizData.config === 'string' 
    ? JSON.parse(vizData.config) 
    : vizData.config;

  return (
    <Plot
      data={config.data || []}
      layout={{
        ...config.layout,
        autosize: true,
        margin: { l: 50, r: 50, t: 50, b: 50 },
        showlegend: true,
        // Dark theme for Plotly
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
          color: '#ffffff',
          family: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
        },
        xaxis: {
          color: '#ffffff',
          gridcolor: '#404040',
          linecolor: '#404040',
          tickcolor: '#ffffff'
        },
        yaxis: {
          color: '#ffffff',
          gridcolor: '#404040',
          linecolor: '#404040',
          tickcolor: '#ffffff'
        },
        legend: {
          bgcolor: 'rgba(0,0,0,0)',
          bordercolor: '#404040',
          font: { color: '#ffffff' }
        }
      }}
      config={{
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
          format: 'png',
          filename: 'visualization',
          height: 500,
          width: 700,
          scale: 1
        }
      }}
      style={{ width: '100%', height: '400px' }}
      useResizeHandler={true}
    />
  );
};
```

### 3. Data Storage
Visualization data is stored in localStorage for persistence.

**Data Storage:**
```javascript
// Store visualization data for Visualization component
if (result.visualization && result.visualization.data) {
  const vizData = {
    config: result.visualization,
    chart_type: result.visualization.type || 'bar',
    query_id: Date.now(),
    timestamp: new Date().toISOString()
  };
  localStorage.setItem(`viz_${sessionId}`, JSON.stringify(vizData));
  // Trigger storage event for Visualization component
  window.dispatchEvent(new Event('storage'));
}
```

## 🔧 Advanced Features

### 1. Interactive Features
Charts include interactive features for better user experience.

**Interactive Configuration:**
```python
def add_interactive_features(self, fig):
    """Add interactive features to the chart"""
    fig.update_layout(
        hovermode='closest',           # Show closest data point on hover
        hoverlabel={
            'align': 'left',           # Left-align hover labels
            'bgcolor': 'rgba(0,0,0,0.8)',  # Semi-transparent background
            'font': {'color': '#ffffff'}    # White text
        },
        dragmode='zoom',               # Enable zoom on drag
        selectdirection='diagonal'     # Diagonal selection
    )
    
    return fig
```

### 2. Custom Chart Types
Add support for new chart types.

**Adding New Chart Type:**
```python
def create_custom_chart(self, df: pd.DataFrame, chart_type: str, query: str):
    """Create custom chart types"""
    if chart_type == "heatmap":
        return self.create_heatmap(df, query)
    elif chart_type == "box":
        return self.create_box_plot(df, query)
    elif chart_type == "violin":
        return self.create_violin_plot(df, query)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

def create_heatmap(self, df: pd.DataFrame, query: str):
    """Create a heatmap visualization"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) >= 2:
        # Create correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Heatmap",
            color_continuous_scale='RdBu'
        )
        
        return fig
```

### 3. Performance Optimization
Optimize chart generation for large datasets.

**Performance Optimization:**
```python
def optimize_for_large_data(self, df: pd.DataFrame, max_rows: int = 1000):
    """Optimize chart generation for large datasets"""
    if len(df) > max_rows:
        # Sample data for visualization
        df_sample = df.sample(n=max_rows, random_state=42)
        return df_sample
    return df

def create_efficient_chart(self, df: pd.DataFrame, chart_type: str, query: str):
    """Create chart with performance optimizations"""
    # Optimize data size
    df_optimized = self.optimize_for_large_data(df)
    
    # Create chart
    fig = self.create_visualization(df_optimized, chart_type, query)
    
    # Add performance optimizations
    fig.update_layout(
        autosize=True,                 # Auto-resize
        responsive=True,               # Responsive design
        showlegend=False if len(df_optimized) > 500 else True  # Hide legend for large datasets
    )
    
    return fig
```

## 🐛 Troubleshooting

### Common Issues

#### Charts Not Displaying
```javascript
// Check if visualization data exists
console.log('Visualization data:', vizData);

// Verify Plotly configuration
console.log('Plotly config:', config);

// Check for errors in browser console
```

#### Binary Data Encoding Issues
```python
# Ensure clean data extraction
def fix_binary_encoding(self, chart_data):
    """Fix binary encoded data in chart"""
    for trace in chart_data['data']:
        if 'y' in trace and isinstance(trace['y'], dict) and 'bdata' in trace['y']:
            # Convert binary data to proper format
            trace['y'] = self.decode_binary_data(trace['y'])
    
    return chart_data
```

#### Performance Issues
```python
# Limit data size for visualization
def limit_data_size(self, df: pd.DataFrame, max_points: int = 1000):
    """Limit data points for better performance"""
    if len(df) > max_points:
        return df.sample(n=max_points, random_state=42)
    return df
```

## 📚 Best Practices

### 1. Chart Type Selection
- **Bar Charts**: For categorical comparisons
- **Line Charts**: For trends over time
- **Pie Charts**: For part-to-whole relationships
- **Scatter Plots**: For correlations
- **Histograms**: For distributions

### 2. Data Preparation
- Clean data before visualization
- Handle missing values appropriately
- Choose appropriate aggregation methods
- Consider data size limitations

### 3. User Experience
- Provide clear chart titles
- Use appropriate axis labels
- Include hover information
- Offer export options

---

*This guide covers the complete visualization system. For more details on specific components, see the other learning guides.*
