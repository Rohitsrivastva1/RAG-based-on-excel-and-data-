#!/usr/bin/env python3
"""
Demo script for RAG Analytics System
Shows example usage of the system components
"""

import pandas as pd
import json
from backend.data_ingestion import DataIngestionManager
from backend.ai_processor import AIProcessor
from backend.visualization import VisualizationEngine
from backend.query_executor import QueryExecutor
from backend.database import DatabaseManager

def demo_excel_processing():
    """Demo Excel/CSV processing"""
    print("📊 Demo: Excel/CSV Processing")
    print("-" * 40)
    
    # Create sample data
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'HR']
    }
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('demo_data.csv', index=False)
    print("✓ Created demo_data.csv")
    
    # Process the file
    ingestion_manager = DataIngestionManager()
    
    # Read the file
    with open('demo_data.csv', 'rb') as f:
        file_content = f.read()
    
    # Process it (this would normally be async)
    print("✓ Processing file...")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Rows: {len(df)}")
    print(f"  Data types: {df.dtypes.to_dict()}")
    
    return df

def demo_ai_processing():
    """Demo AI query generation"""
    print("\n🤖 Demo: AI Query Generation")
    print("-" * 40)
    
    # Sample schema
    schema_info = {
        "data_type": "excel",
        "columns": [
            {"name": "name", "type": "object", "nullable": False},
            {"name": "age", "type": "int64", "nullable": False},
            {"name": "salary", "type": "int64", "nullable": False},
            {"name": "department", "type": "object", "nullable": False}
        ]
    }
    
    # Sample questions
    questions = [
        "What is the average salary?",
        "Show me employees by department",
        "Who are the top 3 highest paid employees?"
    ]
    
    ai_processor = AIProcessor()
    
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            # This would normally be async and use a real session
            print("  → Would generate appropriate query")
            print("  → Would suggest visualization type")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def demo_visualization():
    """Demo visualization generation"""
    print("\n📈 Demo: Visualization Generation")
    print("-" * 40)
    
    # Sample data
    data = [
        {"department": "Engineering", "count": 2, "avg_salary": 60000},
        {"department": "Marketing", "count": 1, "avg_salary": 60000},
        {"department": "Sales", "count": 1, "avg_salary": 55000},
        {"department": "HR", "count": 1, "avg_salary": 65000}
    ]
    
    viz_engine = VisualizationEngine()
    
    try:
        # This would normally be async
        print("✓ Would generate bar chart for department data")
        print("✓ Would create interactive Plotly visualization")
        print("✓ Would suggest appropriate chart type")
    except Exception as e:
        print(f"✗ Error: {e}")

def demo_query_execution():
    """Demo query execution"""
    print("\n⚡ Demo: Query Execution")
    print("-" * 40)
    
    # Sample pandas code
    pandas_code = """
# Calculate average salary by department
result = df.groupby('department')['salary'].mean().reset_index()
result = result.sort_values('salary', ascending=False)
"""
    
    print("Sample Pandas Query:")
    print(pandas_code)
    
    # Sample SQL query
    sql_query = """
SELECT department, AVG(salary) as avg_salary, COUNT(*) as count
FROM employees 
GROUP BY department 
ORDER BY avg_salary DESC
"""
    
    print("\nSample SQL Query:")
    print(sql_query)
    
    print("\n✓ Would execute queries safely")
    print("✓ Would return structured results")
    print("✓ Would handle errors gracefully")

def main():
    """Main demo function"""
    print("🚀 RAG Analytics System Demo")
    print("=" * 50)
    
    try:
        # Demo 1: Excel processing
        df = demo_excel_processing()
        
        # Demo 2: AI processing
        demo_ai_processing()
        
        # Demo 3: Visualization
        demo_visualization()
        
        # Demo 4: Query execution
        demo_query_execution()
        
        print("\n✅ Demo completed successfully!")
        print("\nTo run the full system:")
        print("1. Start backend: python start_backend.py")
        print("2. Start frontend: npm start")
        print("3. Open http://localhost:3000")
        print("4. Upload demo_data.csv and ask questions!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
