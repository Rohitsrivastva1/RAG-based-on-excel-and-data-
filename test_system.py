#!/usr/bin/env python3
"""
Test script for RAG Analytics System
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
SAMPLE_FILE = "sample_data.csv"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✓ Backend is running")
            return True
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend is not running. Please start it first.")
        return False

def test_file_upload():
    """Test file upload functionality"""
    if not os.path.exists(SAMPLE_FILE):
        print(f"✗ Sample file {SAMPLE_FILE} not found")
        return None
    
    try:
        with open(SAMPLE_FILE, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BACKEND_URL}/upload_excel", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ File upload successful")
            print(f"  Session ID: {result['session_id']}")
            print(f"  Schema: {len(result['schema']['columns'])} columns")
            return result['session_id']
        else:
            print(f"✗ File upload failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
    except Exception as e:
        print(f"✗ File upload error: {e}")
        return None

def test_question_asking(session_id):
    """Test asking questions"""
    questions = [
        "What is the average salary?",
        "Show me the top 5 highest paid employees",
        "How many employees are in each department?"
    ]
    
    for question in questions:
        try:
            print(f"\nAsking: {question}")
            response = requests.post(f"{BACKEND_URL}/ask_question", json={
                "question": question,
                "session_id": session_id
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Question answered successfully")
                print(f"  Query type: {result['query_type']}")
                print(f"  Execution time: {result['execution_time']}ms")
                print(f"  Rows returned: {result['row_count']}")
                if result.get('visualization'):
                    print(f"  Visualization: {result['visualization']['chart_type']}")
            else:
                print(f"✗ Question failed: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Question error: {e}")

def test_sessions_list():
    """Test sessions listing"""
    try:
        response = requests.get(f"{BACKEND_URL}/sessions")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Sessions list retrieved: {len(result['sessions'])} sessions")
            return True
        else:
            print(f"✗ Sessions list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Sessions list error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing RAG Analytics System")
    print("=" * 50)
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   python start_backend.py")
        return
    
    # Test 2: File upload
    print("\n📁 Testing file upload...")
    session_id = test_file_upload()
    if not session_id:
        print("\n❌ File upload failed. Cannot continue with tests.")
        return
    
    # Test 3: Ask questions
    print("\n❓ Testing question asking...")
    test_question_asking(session_id)
    
    # Test 4: Sessions list
    print("\n📋 Testing sessions list...")
    test_sessions_list()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Start the frontend: npm start")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Upload the sample_data.csv file")
    print("4. Ask questions about the data")

if __name__ == "__main__":
    main()
