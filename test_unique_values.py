#!/usr/bin/env python3
"""Test script specifically for unique values queries."""

import requests
import json
import pandas as pd
import os

# Test data
test_data = {
    'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech', 'Education', 'Entertainment', 'Finance'],
    'Revenue': [1000, 1500, 1200, 800, 2000, 1100, 1600, 1300],
    'Users': [100, 150, 120, 80, 200, 110, 160, 130],
    'Growth_%': [5.2, 8.1, 3.4, 2.1, 12.5, 6.3, 9.2, 4.7]
}

def test_unique_values():
    """Test unique values queries."""
    print("🧪 Testing Unique Values Queries")
    print("=" * 50)
    
    # Create test file
    df = pd.DataFrame(test_data)
    test_file = 'test_unique_values.xlsx'
    df.to_excel(test_file, index=False)
    
    try:
        # Upload file
        print("1️⃣ Uploading test file...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post('http://localhost:8000/upload_excel', files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            session_id = upload_data['session_id']
            print(f"✅ File uploaded successfully. Session ID: {session_id}")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return
        
        # Test unique values queries
        test_questions = [
            "unique value in category columns",
            "unique values in Category column",
            "what are the unique values in Category?",
            "show me unique values in Category column",
            "list unique values in Category"
        ]
        
        print("\n2️⃣ Testing unique values queries...")
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Question {i}: {question}")
            
            data = {
                'question': question,
                'session_id': session_id
            }
            
            response = requests.post('http://localhost:8000/ask_question', data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer: {result['answer']}")
                print(f"📊 Query type: {result['query_type']}")
                print(f"⏱️  Duration: {result.get('duration_ms', 0):.1f}ms")
            else:
                print(f"❌ Question failed: {response.status_code} - {response.text}")
        
        # Test other column unique values
        print("\n3️⃣ Testing unique values in other columns...")
        other_questions = [
            "unique values in Revenue column",
            "unique values in Users column",
            "unique values in Growth_% column"
        ]
        
        for i, question in enumerate(other_questions, 1):
            print(f"\n📝 Question {i}: {question}")
            
            data = {
                'question': question,
                'session_id': session_id
            }
            
            response = requests.post('http://localhost:8000/ask_question', data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer: {result['answer']}")
                print(f"📊 Query type: {result['query_type']}")
            else:
                print(f"❌ Question failed: {response.status_code} - {response.text}")
        
        # Cleanup
        print("\n4️⃣ Cleaning up...")
        response = requests.delete(f'http://localhost:8000/session/{session_id}')
        if response.status_code == 200:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Session deletion failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ Test file cleaned up")
    
    print("\n🎉 Unique Values Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_unique_values()
