#!/usr/bin/env python3
"""
Test specific queries to verify the fixes
"""

import requests
import pandas as pd
import json

def test_specific_queries():
    print("🧪 Testing Specific Queries")
    print("=" * 50)
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding")
            return
    except:
        print("❌ Backend not running")
        return
    
    # Create test data
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'] * 6,
        'Revenue': [38607.09, 37571.27, 32455.20, 26593.53, 13883.04] * 6,
        'Users': [1200, 1100, 1000, 900, 800] * 6,
        'Growth_%': [12.5, 8.3, 15.2, 6.7, 9.1] * 6,
        'Region': ['North', 'South', 'East', 'West', 'Central'] * 6,
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'] * 7 + ['Q1', 'Q2']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('test_specific.xlsx', index=False)
    print("📊 Created test data with Users and Revenue columns")
    
    # Upload file
    with open('test_specific.xlsx', 'rb') as f:
        files = {'file': ('test_specific.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post("http://localhost:8000/upload_excel", files=files)
    
    if response.status_code == 200:
        result = response.json()
        session_id = result['session_id']
        print(f"✅ File uploaded, Session ID: {session_id}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        return
    
    # Test queries
    queries = [
        "generate a bar graph for category and revenue",
        "generate a bar graph for category and no of user",
        "create a bar chart showing users by category"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        
        form_data = {
            'question': query,
            'session_id': session_id
        }
        
        response = requests.post("http://localhost:8000/ask_question", data=form_data)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            print(f"✅ Answer: {answer[:100]}...")
            
            if 'visualization' in result and result['visualization']:
                viz = result['visualization']
                print(f"📊 Visualization: {viz.get('type', 'unknown')} - {viz.get('data', {}).get('title', 'No title')}")
            else:
                print("❌ No visualization generated")
        else:
            print(f"❌ Query failed: {response.status_code}")
    
    # Cleanup
    import os
    os.remove('test_specific.xlsx')
    print("\n🧹 Cleaned up test file")

if __name__ == "__main__":
    test_specific_queries()
