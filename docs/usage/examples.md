# Usage Examples

## 📚 Real-World Scenarios and Use Cases

This guide provides practical examples of how to use RAG Analytics for various data analysis scenarios.

## 🏢 Business Analytics Examples

### Example 1: Sales Performance Analysis

#### Scenario
You have a sales dataset and want to analyze performance across different regions and products.

#### Data Structure
```csv
Date,Region,Product,Units_Sold,Revenue,Profit_Margin
2025-01-01,North,Product_A,150,7500,0.25
2025-01-01,South,Product_B,200,12000,0.30
2025-01-01,East,Product_A,100,5000,0.25
2025-01-02,North,Product_C,75,4500,0.20
2025-01-02,West,Product_B,300,18000,0.30
```

#### Questions to Ask
```
"Show me total revenue by region"
"Which product has the highest profit margin?"
"Create a bar chart of units sold by product"
"What's the average revenue per region?"
"Show me a pie chart of revenue distribution by region"
"Which region has the best performance?"
```

#### Expected Results
- **Text Answers**: "North region has the highest total revenue of $12,000"
- **Charts**: Bar charts showing revenue by region, pie charts showing product distribution
- **Insights**: Performance comparisons, trend analysis, recommendations

### Example 2: Customer Analytics

#### Scenario
Analyze customer behavior and demographics from your customer database.

#### Data Structure
```csv
Customer_ID,Age,Gender,City,Total_Purchases,Last_Purchase_Date,Customer_Type
C001,25,Female,New York,5,2025-01-15,Premium
C002,35,Male,Los Angeles,12,2025-01-14,Regular
C003,28,Female,Chicago,8,2025-01-13,Premium
C004,45,Male,Houston,3,2025-01-12,Basic
C005,32,Female,Phoenix,15,2025-01-11,Premium
```

#### Questions to Ask
```
"How many customers do we have by type?"
"Show me the age distribution of our customers"
"Which city has the most premium customers?"
"Create a bar chart of average purchases by customer type"
"What's the gender distribution of our customer base?"
"Show me a scatter plot of age vs total purchases"
```

#### Expected Results
- **Demographics**: Age, gender, and location analysis
- **Behavior Patterns**: Purchase frequency and customer type correlations
- **Segmentation**: Customer type performance and characteristics

### Example 3: Financial Analysis

#### Scenario
Analyze quarterly financial performance across different business units.

#### Data Structure
```csv
Quarter,Business_Unit,Revenue,Expenses,Profit,Employee_Count
Q1_2024,Technology,500000,350000,150000,25
Q1_2024,Marketing,200000,180000,20000,15
Q1_2024,Sales,800000,400000,400000,30
Q2_2024,Technology,550000,380000,170000,28
Q2_2024,Marketing,220000,190000,30000,16
```

#### Questions to Ask
```
"Show me quarterly revenue trends"
"Which business unit is most profitable?"
"Create a line chart of profit over time by business unit"
"What's the revenue per employee for each unit?"
"Show me a bar chart comparing Q1 vs Q2 performance"
"Which unit has the best profit margin?"
```

#### Expected Results
- **Performance Metrics**: Revenue, profit, and efficiency analysis
- **Trend Analysis**: Quarterly performance comparisons
- **Unit Comparison**: Business unit performance rankings

## 📊 Marketing Analytics Examples

### Example 4: Campaign Performance

#### Scenario
Analyze the effectiveness of different marketing campaigns across various channels.

#### Data Structure
```csv
Campaign_ID,Channel,Start_Date,End_Date,Budget,Impressions,Clicks,Conversions,Revenue
CAMP001,Google Ads,2025-01-01,2025-01-31,5000,100000,5000,250,12500
CAMP002,Facebook,2025-01-01,2025-01-31,3000,80000,4000,200,10000
CAMP003,Email,2025-01-01,2025-01-31,1000,50000,2500,150,7500
CAMP004,LinkedIn,2025-01-01,2025-01-31,2000,30000,1500,100,5000
```

#### Questions to Ask
```
"Which channel has the best ROI?"
"Show me conversion rates by campaign"
"Create a bar chart of revenue by channel"
"What's the cost per conversion for each campaign?"
"Which campaign has the highest click-through rate?"
"Show me a scatter plot of budget vs revenue"
```

#### Expected Results
- **Channel Performance**: ROI, conversion rates, and efficiency metrics
- **Campaign Analysis**: Budget effectiveness and performance rankings
- **Optimization Insights**: Recommendations for budget allocation

### Example 5: Website Analytics

#### Scenario
Analyze website traffic and user behavior from your analytics data.

#### Data Structure
```csv
Date,Page,Visitors,Bounce_Rate,Avg_Session_Duration,Page_Views,Conversions
2025-01-01,Homepage,1000,0.45,120,1500,50
2025-01-01,Products,800,0.35,180,1200,40
2025-01-01,About,600,0.60,90,800,20
2025-01-01,Contact,400,0.25,240,500,30
2025-01-02,Homepage,1200,0.42,125,1800,60
```

#### Questions to Ask
```
"Which page has the lowest bounce rate?"
"Show me daily visitor trends"
"Create a bar chart of conversions by page"
"What's the average session duration by page?"
"Which page generates the most conversions?"
"Show me a line chart of page views over time"
```

#### Expected Results
- **Page Performance**: Bounce rates, session duration, and conversion metrics
- **Traffic Analysis**: Visitor trends and page popularity
- **Optimization Opportunities**: Pages that need improvement

## 🏥 Healthcare Analytics Examples

### Example 6: Patient Data Analysis

#### Scenario
Analyze patient demographics and treatment outcomes.

#### Data Structure
```csv
Patient_ID,Age,Gender,Diagnosis,Treatment,Length_of_Stay,Outcome,Cost
P001,45,Male,Diabetes,Medication,3,Improved,2500
P002,62,Female,Hypertension,Surgery,7,Recovered,15000
P003,38,Male,Injury,Physical Therapy,14,Improved,5000
P004,55,Female,Diabetes,Medication,2,Stable,2000
P005,29,Male,Injury,Surgery,5,Recovered,12000
```

#### Questions to Ask
```
"What's the average length of stay by diagnosis?"
"Show me treatment outcomes by age group"
"Create a bar chart of costs by treatment type"
"Which diagnosis is most common?"
"Show me a pie chart of outcomes distribution"
"What's the correlation between age and treatment cost?"
```

#### Expected Results
- **Clinical Insights**: Treatment effectiveness and patient outcomes
- **Resource Planning**: Cost analysis and resource allocation
- **Demographic Analysis**: Age and gender-based treatment patterns

## 🎓 Educational Analytics Examples

### Example 7: Student Performance Analysis

#### Scenario
Analyze student performance across different subjects and demographics.

#### Data Structure
```csv
Student_ID,Grade,Subject,Score,Attendance,Study_Hours,Parent_Education
S001,10,Math,85,95,15,College
S002,10,Science,92,98,20,High School
S003,11,English,78,88,12,College
S004,11,Math,90,92,18,Graduate
S005,10,Science,88,90,16,High School
```

#### Questions to Ask
```
"Which subject has the highest average score?"
"Show me performance by grade level"
"Create a bar chart of scores by subject"
"What's the correlation between study hours and scores?"
"Which grade has the best attendance?"
"Show me a scatter plot of attendance vs performance"
```

#### Expected Results
- **Academic Performance**: Subject-wise and grade-wise analysis
- **Behavioral Patterns**: Study habits and attendance impact
- **Demographic Insights**: Parent education and student performance correlation

## 🏭 Manufacturing Analytics Examples

### Example 8: Production Quality Analysis

#### Scenario
Analyze production quality metrics across different production lines and shifts.

#### Data Structure
```csv
Date,Production_Line,Shift,Units_Produced,Defects,Quality_Score,Downtime_Hours
2025-01-01,Line_A,Day,1000,25,0.975,2
2025-01-01,Line_B,Night,800,30,0.9625,3
2025-01-01,Line_C,Day,1200,20,0.983,1
2025-01-02,Line_A,Night,900,35,0.961,4
2025-01-02,Line_B,Day,1100,15,0.986,1
```

#### Questions to Ask
```
"Which production line has the best quality score?"
"Show me defect rates by shift"
"Create a bar chart of units produced by line"
"What's the correlation between downtime and quality?"
"Which shift is most productive?"
"Show me a line chart of quality scores over time"
```

#### Expected Results
- **Quality Metrics**: Defect rates, quality scores, and production efficiency
- **Shift Analysis**: Performance differences between day and night shifts
- **Line Comparison**: Production line performance and optimization opportunities

## 🛒 E-commerce Analytics Examples

### Example 9: Product Sales Analysis

#### Scenario
Analyze product sales performance across different categories and time periods.

#### Data Structure
```csv
Product_ID,Category,Price,Units_Sold,Revenue,Profit_Margin,Customer_Rating
P001,Electronics,299.99,150,44998.50,0.30,4.5
P002,Clothing,49.99,300,14997.00,0.40,4.2
P003,Books,19.99,500,9995.00,0.25,4.8
P004,Electronics,599.99,75,44999.25,0.35,4.3
P005,Home,89.99,200,17998.00,0.45,4.6
```

#### Questions to Ask
```
"Which category has the highest revenue?"
"Show me profit margins by product category"
"Create a bar chart of units sold by category"
"What's the average customer rating by category?"
"Which product has the best profit margin?"
"Show me a scatter plot of price vs customer rating"
```

#### Expected Results
- **Category Performance**: Revenue, profit margins, and sales volume analysis
- **Product Insights**: Individual product performance and customer satisfaction
- **Pricing Analysis**: Price vs rating correlation and optimization opportunities

## 🚀 Advanced Analysis Examples

### Example 10: Multi-Dimensional Analysis

#### Scenario
Complex analysis combining multiple data dimensions for strategic insights.

#### Data Structure
```csv
Year,Quarter,Region,Product_Category,Channel,Revenue,Costs,Profit,Market_Share
2024,Q1,North,Electronics,Online,500000,350000,150000,0.25
2024,Q1,North,Electronics,Retail,300000,200000,100000,0.15
2024,Q1,South,Clothing,Online,200000,120000,80000,0.20
2024,Q2,North,Electronics,Online,550000,380000,170000,0.28
2024,Q2,South,Clothing,Retail,250000,150000,100000,0.22
```

#### Complex Questions to Ask
```
"Show me quarterly revenue trends by region and product category"
"Which combination of region, category, and channel is most profitable?"
"Create a bar chart of market share by region and quarter"
"What's the profit margin trend across all dimensions?"
"Show me the top 5 performing combinations of region, category, and channel"
"Which region has the highest growth rate in market share?"
```

#### Expected Results
- **Multi-Dimensional Insights**: Complex relationships between multiple variables
- **Strategic Recommendations**: Optimal combinations for maximum profitability
- **Trend Analysis**: Performance patterns across time and dimensions

## 💡 Tips for Effective Analysis

### 1. Start with Overview Questions
```
"How many rows are in the data?"
"What columns do we have?"
"Show me the first 10 rows"
```

### 2. Ask Specific Analysis Questions
```
"What is the total revenue?"
"What's the average growth rate?"
"Which category has the highest performance?"
```

### 3. Request Visualizations
```
"Show me a bar chart of revenue by category"
"Create a pie chart of market share"
"Display a line chart of trends over time"
```

### 4. Drill Down for Details
```
"Show me the top 5 categories by revenue"
"What are the bottom 3 performing regions?"
"Which products have profit margins above 30%?"
```

### 5. Compare and Contrast
```
"Compare Q1 vs Q2 performance"
"Show me the difference between online and retail channels"
"Which region performs better than the average?"
```

## 📈 Export and Reporting

### Export Strategies
1. **Export Charts**: Save visualizations as PNG or PDF for presentations
2. **Export Data**: Save analysis results as CSV for further processing
3. **Copy Answers**: Copy text answers for reports and documents

### Report Creation Workflow
1. **Upload Data**: Start with your dataset
2. **Initial Analysis**: Ask overview questions
3. **Generate Visualizations**: Create key charts
4. **Deep Dive**: Ask specific analysis questions
5. **Export Results**: Save charts and data
6. **Compile Report**: Combine exports into final report

## 🎯 Best Practices

### Question Formulation
- **Be Specific**: "Revenue by category" not "data"
- **Include Context**: "Q1 2024 revenue by category"
- **Use Clear Language**: "Show me" or "Create a chart"
- **Ask Follow-ups**: Build on previous answers

### Data Preparation
- **Clean Data**: Remove empty rows and inconsistent formats
- **Consistent Naming**: Use clear, consistent column names
- **Proper Types**: Ensure numbers are numeric, dates are dates
- **Complete Data**: Fill missing values appropriately

### Analysis Workflow
1. **Understand Data**: Start with overview questions
2. **Identify Patterns**: Look for trends and outliers
3. **Generate Insights**: Ask specific analysis questions
4. **Visualize Results**: Create charts for key findings
5. **Export and Share**: Save results for stakeholders

---

*These examples demonstrate the power and flexibility of RAG Analytics. Start with simple questions and gradually build up to more complex analyses as you become familiar with the system.*
