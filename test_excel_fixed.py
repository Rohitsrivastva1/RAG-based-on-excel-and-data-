#!/usr/bin/env python3
"""
Test Excel functionality with fixed enhanced_backend.py
"""

import requests
import pandas as pd
import os

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_EXCEL_FILE = "test_data.xlsx"

def create_test_excel():
    """Create a test Excel file with sample data"""
    print("📊 Creating test Excel file...")
    
    # Sample data for testing
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech', 'Education', 'Entertainment', 'Finance'],
        'Revenue': [63853.87, 37001.99, 44569.89, 52341.12, 38976.45, 71234.56, 45678.90, 67890.12],
        'Users': [1200, 890, 1100, 950, 800, 1350, 920, 1250],
        'Growth_%': [12.5, 8.3, 15.2, 9.7, 11.8, 14.6, 7.9, 13.4],
        'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
        'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2']
    }
    
    df = pd.DataFrame(data)
    df.to_excel(TEST_EXCEL_FILE, index=False)
    print(f"✅ Created {TEST_EXCEL_FILE} with {len(df)} rows")
    return df

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def upload_excel_file():
    """Upload Excel file to the system"""
    print("📤 Uploading Excel file...")
    
    try:
        with open(TEST_EXCEL_FILE, 'rb') as f:
            files = {'file': (TEST_EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{BACKEND_URL}/upload_excel", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File uploaded successfully")
            print(f"   Session ID: {result.get('session_id', 'N/A')}")
            print(f"   Rows: {result.get('rows', 'N/A')}")
            print(f"   Columns: {result.get('columns', 'N/A')}")
            return result.get('session_id')
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_excel_queries(session_id):
    """Test various Excel-based queries"""
    print("\n🧪 Testing Excel Queries...")
    
    test_queries = [
        "What columns are in this dataset?",
        "Show me the first 5 rows of data",
        "What is the total revenue by category?",
        "Create a bar chart showing revenue by category",
        "What is the average growth percentage?",
        "How many users are in each region?",
        "Show me the top 3 categories by revenue"
    ]
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        
        try:
            data = {
                "question": query,
                "session_id": session_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ask_question",
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query processed successfully")
                
                # Show answer preview
                answer = result.get('answer', 'No answer')
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                print(f"   Answer: {answer}")
                
                # Check for visualization
                if 'visualization' in result and result['visualization']:
                    viz = result['visualization']
                    print(f"   📊 Visualization: {viz.get('type', 'unknown')} chart")
                
                successful_queries += 1
                
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Query error: {e}")
    
    return successful_queries, len(test_queries)

def main():
    """Main test function"""
    print("🚀 Excel Data Processing Test (Fixed Backend)")
    print("=" * 60)
    
    # Create test data
    df = create_test_excel()
    
    # Test backend health
    if not test_backend_health():
        print("❌ Backend is not running. Please start it first.")
        return
    
    # Upload Excel file
    session_id = upload_excel_file()
    if not session_id:
        print("❌ Failed to upload Excel file")
        return
    
    # Test Excel queries
    successful_queries, total_queries = test_excel_queries(session_id)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Excel Queries: {successful_queries}/{total_queries} successful")
    print(f"📈 Success Rate: {(successful_queries / total_queries) * 100:.1f}%")
    
    if successful_queries == total_queries:
        print("🎉 All Excel queries processed successfully!")
    else:
        print("⚠️ Some Excel queries failed. Check the logs above.")
    
    # Cleanup
    if os.path.exists(TEST_EXCEL_FILE):
        os.remove(TEST_EXCEL_FILE)
        print(f"\n🧹 Cleaned up {TEST_EXCEL_FILE}")

if __name__ == "__main__":
    main()
