#!/usr/bin/env python3
"""
Simple test script for the new RAG Analytics architecture.
Tests basic functionality without complex dependencies.
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime

def test_simple_backend():
    """Test the new architecture with a simple approach."""
    print("🧪 Testing New RAG Analytics Architecture (Simple)")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   Message: {health.get('message', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        print("   Make sure the backend server is running on port 8000")
        return
    
    # Test 2: Create Test Data
    print("\n2️⃣ Creating Test Data")
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'] * 4,
        'Revenue': [1000, 1500, 1200, 800, 900] * 4,
        'Users': [100, 150, 120, 80, 90] * 4,
        'Growth_%': [12.5, 8.3, 15.2, 6.7, 9.1] * 4
    }
    
    df = pd.DataFrame(data)
    df.to_excel('test_simple.xlsx', index=False)
    print(f"✅ Created test data: {len(df)} rows, {len(df.columns)} columns")
    
    # Test 3: Upload File
    print("\n3️⃣ Testing File Upload")
    try:
        with open('test_simple.xlsx', 'rb') as f:
            files = {'file': ('test_simple.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/upload_excel", files=files, timeout=10)
        
        if response.status_code == 200:
            upload_result = response.json()
            session_id = upload_result['session_id']
            print(f"✅ File uploaded successfully")
            print(f"   Session ID: {session_id}")
            print(f"   File info: {upload_result.get('file_info', {}).get('name', 'unknown')}")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Test 4: Ask Questions
    print("\n4️⃣ Testing Question Processing")
    questions = [
        "What columns are in this dataset?",
        "Show me the first 3 rows",
        "What is the total revenue by category?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   📝 Question {i}: {question}")
        
        try:
            form_data = {
                'question': question,
                'session_id': session_id
            }
            
            response = requests.post(f"{base_url}/ask_question", data=form_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer: {result.get('answer', 'No answer')[:100]}...")
                print(f"   📊 Query type: {result.get('query_type', 'unknown')}")
                
                if result.get('visualization'):
                    viz = result['visualization']
                    print(f"   📈 Visualization: {viz.get('type', 'unknown')} chart")
                    
            else:
                print(f"   ❌ Question failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Question error: {e}")
    
    # Test 5: Cleanup
    print("\n5️⃣ Testing Cleanup")
    try:
        # Delete session
        response = requests.delete(f"{base_url}/session/{session_id}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Session deleted successfully")
        else:
            print(f"❌ Session deletion failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # Cleanup test file
    import os
    if os.path.exists('test_simple.xlsx'):
        os.remove('test_simple.xlsx')
        print(f"✅ Test file cleaned up")
    
    print("\n🎉 Simple Architecture Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_simple_backend()
