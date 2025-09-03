# User Guide

## 👤 Complete User Manual for RAG Analytics

This guide provides comprehensive instructions for using the RAG Analytics system as an end user.

## 🎯 What is RAG Analytics?

RAG Analytics is an AI-powered data analytics platform that allows you to:
- **Upload** your data files (Excel, CSV) or connect to databases
- **Ask questions** in natural language about your data
- **Get instant answers** with AI-powered analysis
- **View interactive charts** automatically generated from your queries
- **Export results** in multiple formats (CSV, PNG, PDF)

## 🚀 Getting Started

### 1. Access the System
- Open your web browser
- Navigate to the RAG Analytics URL
- You'll see the dark-themed interface with a modern design

### 2. First Time Setup
- No account creation required
- No login needed
- Start immediately with data upload

## 📊 Data Upload

### Method 1: File Upload

#### Supported File Types
- **Excel Files**: .xlsx, .xls
- **CSV Files**: .csv
- **Maximum Size**: 50MB

#### Upload Process
1. Click on the **"Upload Your Data"** tab
2. Drag and drop your file into the upload area, or click "Choose File"
3. Wait for the upload to complete
4. You'll see a success message with your session details

#### File Requirements
Your data file should have:
- **Headers**: Column names in the first row
- **Clean Data**: No empty rows at the top
- **Consistent Format**: Same data types in each column

**Example CSV Structure:**
```csv
Date,Category,Users,Revenue,Growth_%
2025-01-01,Education,202,6557.33,10.11
2025-01-02,Entertainment,535,6504.88,3.50
2025-01-03,Games,960,1063.60,-0.84
```

### Method 2: Database Connection

#### Supported Databases
- **PostgreSQL**
- **MySQL**
- **SQLite**

#### Connection Setup
1. Click on the **"Database Connection"** tab
2. Fill in the connection details:
   - **Database Type**: Select from dropdown
   - **Host**: Database server address
   - **Port**: Database port (default provided)
   - **Database Name**: Name of your database
   - **Username**: Your database username
   - **Password**: Your database password
3. Click **"Connect to Database"**
4. Wait for connection confirmation

#### Connection Examples
**PostgreSQL:**
```
Host: localhost
Port: 5432
Database: my_database
Username: my_user
Password: my_password
```

**MySQL:**
```
Host: localhost
Port: 3306
Database: my_database
Username: my_user
Password: my_password
```

## 💬 Asking Questions

### Natural Language Interface

The system understands questions in plain English. You can ask:

#### Data Overview Questions
```
"How many rows are in the data?"
"What columns do we have?"
"Show me the first 10 rows"
"What's the data structure?"
```

#### Analysis Questions
```
"What is the total revenue?"
"What's the average growth rate?"
"Which category has the highest revenue?"
"What are the unique categories?"
```

#### Comparison Questions
```
"Compare revenue by category"
"Show me the top 5 categories by users"
"Which category has the best growth rate?"
```

#### Visualization Requests
```
"Show me a bar chart of revenue by category"
"Create a pie chart of users by category"
"Display a line chart of growth over time"
"Make a scatter plot of revenue vs users"
```

### Chat Interface Features

#### Typing Animation
- Responses appear with a ChatGPT-like typing animation
- Creates a natural conversation feel
- Shows the AI is "thinking"

#### Message History
- All your questions and answers are saved
- Scroll through previous conversations
- Copy answers to clipboard

#### Query Types
The system automatically detects and labels different types of queries:
- **Data Analysis**: General data questions
- **Visualization**: Chart requests
- **Aggregation**: Sum, average, count operations
- **Filtering**: Specific data subsets

## 📈 Viewing Visualizations

### Automatic Chart Generation
When you ask for charts, the system automatically:
1. **Detects** the chart type you want
2. **Analyzes** your data structure
3. **Selects** the appropriate columns
4. **Generates** an interactive chart
5. **Displays** it in the Visualization tab

### Chart Types

#### Bar Charts
- **Best for**: Comparing categories
- **Example**: "Show me revenue by category"
- **Features**: Hover for exact values, zoom, pan

#### Pie Charts
- **Best for**: Showing proportions
- **Example**: "Create a pie chart of users by category"
- **Features**: Interactive segments, percentage labels

#### Line Charts
- **Best for**: Trends over time
- **Example**: "Display growth over time"
- **Features**: Multiple lines, time-based navigation

#### Scatter Plots
- **Best for**: Correlations
- **Example**: "Show revenue vs users"
- **Features**: Point selection, trend lines

### Interactive Features
- **Hover**: See exact values
- **Zoom**: Click and drag to zoom in
- **Pan**: Move around the chart
- **Reset**: Return to original view
- **Fullscreen**: View in full screen mode

### Chart History
- View all your previous visualizations
- Switch between different charts
- Each chart is numbered (bar #1, pie #2, etc.)

## 📤 Exporting Results

### Export Options
The system provides three export formats:

#### CSV Export
- **Use for**: Data analysis in Excel or other tools
- **Contains**: Raw data from the chart
- **Format**: Comma-separated values

#### PNG Export
- **Use for**: Presentations, reports, documents
- **Contains**: High-quality image of the chart
- **Format**: Portable Network Graphics

#### PDF Export
- **Use for**: Professional reports, printing
- **Contains**: Vector-based chart image
- **Format**: Portable Document Format

### Export Process
1. Generate a chart by asking a visualization question
2. Go to the **Visualization** tab
3. Click on the export button you want (CSV, PNG, or PDF)
4. The file will download automatically
5. Save it to your desired location

## 🔄 Managing Sessions

### What are Sessions?
A session represents one data upload or database connection. Each session contains:
- Your uploaded data
- All your questions and answers
- Generated visualizations
- Export history

### Session Management
1. Click on the **"Sessions"** tab
2. View all your active and past sessions
3. See session details:
   - **Upload Date**: When you uploaded the data
   - **File Name**: Original file name
   - **Data Size**: Number of rows and columns
   - **Status**: Active or completed

### Session Features
- **Refresh**: Update session list
- **View Details**: See session information
- **Data Preview**: Quick look at your data
- **Session History**: Track your analysis progress

## 🎨 Interface Overview

### Dark Theme Design
The system uses a modern dark theme with:
- **Charcoal Background**: Easy on the eyes
- **Teal Accents**: Professional color scheme
- **White Text**: High contrast for readability
- **Glass Effects**: Modern, minimal design

### Navigation Tabs
- **Chat**: Ask questions and get answers
- **Visualization**: View and manage charts
- **Upload**: Upload new data files
- **Sessions**: Manage your data sessions

### Header Information
- **System Name**: RAG Analytics
- **Active Session**: Current data session info
- **Status Indicators**: System health and connection status

## 💡 Tips and Best Practices

### Writing Effective Questions

#### Be Specific
**Good**: "What is the total revenue for the Education category?"
**Poor**: "Tell me about education"

#### Use Clear Language
**Good**: "Show me a bar chart of revenue by category"
**Poor**: "Make a graph"

#### Include Context
**Good**: "Which category has the highest growth rate in the last quarter?"
**Poor**: "What's the highest?"

### Data Preparation Tips

#### Clean Your Data
- Remove empty rows at the top
- Ensure consistent column names
- Check for missing values
- Use consistent data formats

#### Column Naming
- Use descriptive names: "Revenue_2024" instead of "R24"
- Avoid special characters: Use underscores instead of spaces
- Be consistent: "User_Count" not "UserCount" and "user_count"

#### Data Types
- **Numbers**: Use actual numbers, not text
- **Dates**: Use proper date formats
- **Categories**: Use consistent spelling

### Visualization Best Practices

#### Choose the Right Chart Type
- **Bar Charts**: For comparing categories
- **Line Charts**: For trends over time
- **Pie Charts**: For showing proportions
- **Scatter Plots**: For correlations

#### Ask for Specific Visualizations
- "Show me a bar chart of revenue by category"
- "Create a pie chart showing the distribution of users"
- "Display a line chart of growth over time"

## 🐛 Troubleshooting

### Common Issues

#### Upload Problems
**Issue**: File won't upload
**Solutions**:
- Check file size (must be under 50MB)
- Verify file format (.xlsx, .xls, .csv)
- Ensure file isn't corrupted
- Try a different browser

#### Connection Issues
**Issue**: Can't connect to database
**Solutions**:
- Verify connection details
- Check if database server is running
- Ensure firewall allows connections
- Test with database client first

#### Chart Not Displaying
**Issue**: Visualization tab shows no chart
**Solutions**:
- Make sure you asked for a visualization
- Check if your data has the right columns
- Try asking a simpler question
- Refresh the page

#### Slow Performance
**Issue**: System is slow to respond
**Solutions**:
- Reduce data size (use fewer rows)
- Ask simpler questions
- Check your internet connection
- Close other browser tabs

### Error Messages

#### "No data found"
- Make sure you've uploaded data
- Check if your session is active
- Verify data has content

#### "Invalid file format"
- Use supported formats: .xlsx, .xls, .csv
- Check file isn't corrupted
- Try saving in a different format

#### "Connection failed"
- Verify database credentials
- Check network connectivity
- Ensure database server is running

## 📞 Getting Help

### Self-Service Resources
1. **This User Guide**: Comprehensive instructions
2. **Tooltips**: Hover over interface elements
3. **Error Messages**: Read error descriptions carefully
4. **Example Questions**: Try the suggested questions

### Support Channels
- **Documentation**: Check the learning guides
- **Community**: GitHub discussions
- **Issues**: Report bugs and request features

### Reporting Problems
When reporting issues, include:
- **What you were trying to do**
- **What happened instead**
- **Error messages you saw**
- **Your data file type and size**
- **Browser and operating system**

## 🎯 Advanced Usage

### Complex Queries
You can ask complex questions like:
```
"Show me the top 3 categories by revenue, but only include those with growth rate above 5%"
"What's the correlation between users and revenue for each category?"
"Create a bar chart showing average revenue by category, sorted from highest to lowest"
```

### Data Analysis Workflows
1. **Upload your data**
2. **Ask overview questions** to understand the data
3. **Generate visualizations** to see patterns
4. **Ask specific questions** for deeper insights
5. **Export results** for further analysis

### Integration with Other Tools
- **Export CSV**: Use in Excel, Google Sheets, or other tools
- **Export PNG/PDF**: Include in presentations or reports
- **Copy answers**: Paste into documents or emails

---

*This user guide covers all the essential features. For technical details and advanced configuration, see the learning and architecture documentation.*
