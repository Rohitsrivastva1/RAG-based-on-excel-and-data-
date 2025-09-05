#!/usr/bin/env python3
"""
Test script for the new RAG Analytics architecture.
Tests all components and the main orchestration flow.
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime

def test_new_architecture():
    """Test the new architecture implementation."""
    print("🧪 Testing New RAG Analytics Architecture")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health['status']}")
            print(f"   Features: {health['features']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test 2: Create Test Data
    print("\n2️⃣ Creating Test Data")
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'] * 4,
        'Revenue': [1000, 1500, 1200, 800, 900] * 4,
        'Users': [100, 150, 120, 80, 90] * 4,
        'Growth_%': [12.5, 8.3, 15.2, 6.7, 9.1] * 4,
        'Region': ['North', 'South', 'East', 'West'] * 5
    }
    
    df = pd.DataFrame(data)
    df.to_excel('test_architecture.xlsx', index=False)
    print(f"✅ Created test data: {len(df)} rows, {len(df.columns)} columns")
    
    # Test 3: Upload File
    print("\n3️⃣ Testing File Upload")
    try:
        with open('test_architecture.xlsx', 'rb') as f:
            files = {'file': ('test_architecture.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/upload_excel", files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            session_id = upload_result['session_id']
            print(f"✅ File uploaded successfully")
            print(f"   Session ID: {session_id}")
            print(f"   File info: {upload_result['file_info']}")
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
        "Show me the first 5 rows",
        "What is the total revenue by category?",
        "Create a bar chart showing revenue by category",
        "What is the average growth percentage?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   📝 Question {i}: {question}")
        
        try:
            form_data = {
                'question': question,
                'session_id': session_id
            }
            
            response = requests.post(f"{base_url}/ask_question", data=form_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Answer: {result['answer'][:100]}...")
                print(f"   📊 Query type: {result['query_type']}")
                
                if result.get('visualization'):
                    viz = result['visualization']
                    print(f"   📈 Visualization: {viz.get('type', 'unknown')} chart")
                
                if result.get('duration_ms'):
                    print(f"   ⏱️  Duration: {result['duration_ms']:.1f}ms")
                    
            else:
                print(f"   ❌ Question failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Question error: {e}")
    
    # Test 5: Session Management
    print("\n5️⃣ Testing Session Management")
    try:
        # Get session info
        response = requests.get(f"{base_url}/session/{session_id}/info")
        if response.status_code == 200:
            session_info = response.json()
            print(f"✅ Session info retrieved")
            print(f"   Data source: {session_info.get('data_source')}")
            print(f"   Created: {session_info.get('created_at')}")
        else:
            print(f"❌ Session info failed: {response.status_code}")
        
        # List all sessions
        response = requests.get(f"{base_url}/sessions")
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Sessions listed: {sessions['count']} active")
        else:
            print(f"❌ List sessions failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Session management error: {e}")
    
    # Test 6: Cleanup
    print("\n6️⃣ Testing Cleanup")
    try:
        # Delete session
        response = requests.delete(f"{base_url}/session/{session_id}")
        if response.status_code == 200:
            print(f"✅ Session deleted successfully")
        else:
            print(f"❌ Session deletion failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # Cleanup test file
    import os
    if os.path.exists('test_architecture.xlsx'):
        os.remove('test_architecture.xlsx')
        print(f"✅ Test file cleaned up")
    
    print("\n🎉 Architecture Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_new_architecture()
