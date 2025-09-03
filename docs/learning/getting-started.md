# Getting Started with RAG Analytics

## 🚀 Quick Start Guide

This guide will walk you through setting up and using the RAG Analytics system from scratch.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.9 or higher
- **Node.js**: Version 16 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space

### Required Accounts
- **Google Gemini API**: For AI processing (free tier available)
- **Database Access**: Optional, for SQL connections

## 🛠️ Installation Steps

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd RAG_LLM
```

### Step 2: Backend Setup

#### Install Python Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Or if you have multiple Python versions
py -m pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Start Backend Server
```bash
# Start the FastAPI server
uvicorn enhanced_backend:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 3: Frontend Setup

#### Install Node.js Dependencies
```bash
# Navigate to src directory
cd src

# Install npm packages
npm install

# Start development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view rag-analytics in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000
```

### Step 4: Verify Installation

#### Check Backend Health
```bash
# Test backend endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "message": "Enhanced RAG Analytics API is running",
  "version": "2.0.0"
}
```

#### Check Frontend
- Open browser to `http://localhost:3000`
- You should see the dark-themed RAG Analytics interface

## 🎯 First Steps

### 1. Upload Your First Dataset

#### Using Excel/CSV Files
1. Click on the **"Upload Your Data"** tab
2. Drag and drop an Excel or CSV file
3. Wait for upload completion
4. You'll see a success message with session details

**Supported File Formats:**
- Excel files (.xlsx, .xls)
- CSV files (.csv)
- Maximum file size: 50MB

#### Sample Data Structure
Your file should have:
- **Headers**: Column names in the first row
- **Data Types**: Mix of text and numbers
- **Clean Data**: No empty rows at the top

**Example CSV:**
```csv
Date,Category,Users,Revenue,Growth_%
2025-01-01,Education,202,6557.33,10.11
2025-01-02,Entertainment,535,6504.88,3.50
2025-01-03,Games,960,1063.60,-0.84
```

### 2. Ask Your First Question

#### Navigate to Chat Interface
1. Click on the **"Chat"** tab
2. You'll see the AI Data Assistant interface
3. Type your question in the input box

#### Example Questions to Try
```
"How many rows are in the data?"
"What are the unique categories?"
"Show me a bar chart of revenue by category"
"What is the total revenue?"
"Which category has the highest growth?"
```

### 3. View Visualizations

#### Check Visualization Tab
1. After asking a question that generates a chart
2. Click on the **"Visualization"** tab
3. You'll see your interactive chart
4. Use export buttons to save as CSV, PNG, or PDF

## 🔧 Configuration

### API Key Setup

#### Get Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### Configure in Code (Temporary)
```python
# In backend/llm_agent.py
GEMINI_API_KEY = "your_actual_api_key_here"
```

### Database Connection (Optional)

#### Supported Databases
- **PostgreSQL**: `postgresql://user:pass@host:port/db`
- **MySQL**: `mysql://user:pass@host:port/db`
- **SQLite**: `sqlite:///path/to/database.db`

#### Connection Setup
1. Go to **"Database Connection"** tab
2. Fill in connection details
3. Test connection
4. Start querying your database

## 🎨 Customization

### Theme Customization

#### Modify Colors
```css
/* In src/App.css */
:root {
  --primary-color: #00d4aa;    /* Teal accent */
  --background-dark: #1a1a1a;  /* Dark background */
  --text-light: #ffffff;       /* White text */
}
```

#### Component Styling
```javascript
// In src/App.js
const darkTheme = {
  token: {
    colorPrimary: '#00d4aa',     // Change primary color
    colorBgBase: '#1a1a1a',      // Change background
    colorTextBase: '#ffffff',    // Change text color
  }
}
```

### Adding New Chart Types

#### Backend Extension
```python
# In backend/llm_agent.py
def create_visualization(self, df: pd.DataFrame, chart_type: str, query: str):
    if chart_type == "heatmap":
        # Add heatmap logic
        fig = px.density_heatmap(df, x=x_col, y=y_col)
    # ... existing chart types
```

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port availability
netstat -ano | findstr :8000
```

#### Frontend Won't Load
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules
npm install

# Check Node.js version
node --version
```

#### API Connection Issues
```bash
# Test backend connectivity
curl http://localhost:8000/health

# Check CORS settings in backend
# Verify proxy configuration in package.json
```

### Error Messages

#### "ModuleNotFoundError"
```bash
# Install missing package
pip install package_name

# Or reinstall all requirements
pip install -r requirements.txt
```

#### "ECONNREFUSED"
- Backend server not running
- Wrong port number
- Firewall blocking connection

#### "API Key Error"
- Invalid Gemini API key
- API key not set in environment
- Exceeded API quota

## 📚 Next Steps

### Learn More
- [Data Ingestion Guide](data-ingestion.md) - Detailed file upload and database setup
- [LLM Integration Guide](llm-integration.md) - Understanding AI processing
- [Visualization System](visualization-system.md) - Chart generation details
- [Frontend Components](frontend-components.md) - React component structure

### Advanced Usage
- [User Guide](../usage/user-guide.md) - Complete user manual
- [Admin Guide](../usage/admin-guide.md) - System administration
- [Examples](../usage/examples.md) - Real-world usage scenarios

### Development
- [Technical Architecture](../architecture/technical-architecture.md) - Implementation details
- [API Documentation](../architecture/api-documentation.md) - REST API reference
- [Deployment Guide](../architecture/deployment-guide.md) - Production deployment

## 🆘 Getting Help

### Support Resources
1. **Documentation**: Check relevant guides in this documentation
2. **Error Logs**: Check browser console and backend logs
3. **Community**: GitHub issues and discussions
4. **Troubleshooting**: [Troubleshooting Guide](troubleshooting.md)

### Reporting Issues
When reporting issues, include:
- Operating system and version
- Python and Node.js versions
- Error messages and logs
- Steps to reproduce the issue
- Expected vs actual behavior

---

*Congratulations! You've successfully set up the RAG Analytics system. Now explore the other guides to learn more about its capabilities.*
