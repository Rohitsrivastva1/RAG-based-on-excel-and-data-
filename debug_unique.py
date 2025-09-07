#!/usr/bin/env python3
"""Debug script for unique values queries."""

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

def debug_unique_values():
    """Debug unique values queries."""
    print("🔍 Debugging Unique Values Queries")
    print("=" * 50)
    
    # Create test file
    df = pd.DataFrame(test_data)
    test_file = 'debug_unique.xlsx'
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
        
        # Test a simple question first
        print("\n2️⃣ Testing simple question...")
        data = {
            'question': 'What columns are in this dataset?',
            'session_id': session_id
        }
        
        response = requests.post('http://localhost:8000/ask_question', data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Simple question works: {result['answer']}")
        else:
            print(f"❌ Simple question failed: {response.status_code} - {response.text}")
        
        # Test unique values query
        print("\n3️⃣ Testing unique values query...")
        data = {
            'question': 'unique values in Category column',
            'session_id': session_id
        }
        
        response = requests.post('http://localhost:8000/ask_question', data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Unique values query: {result['answer']}")
            print(f"📊 Query type: {result['query_type']}")
        else:
            print(f"❌ Unique values query failed: {response.status_code} - {response.text}")
        
        # Test with different wording
        print("\n4️⃣ Testing different wording...")
        test_questions = [
    "unique value in category columns",
    "unique values in Category column",
    "what are the unique values in Category?",
    "show me unique values in Category column",
    "list unique values in Category",
    "how many unique categories are there?",
    "which category appears most frequently?",
    "show the count of records per category",
    "which categories have revenue greater than 1200?",
    "what is the average growth percentage for each category?",

    # Revenue related
    "what is the total revenue?",
    "which category has the highest revenue?",
    "show the top 3 categories by revenue",
    "what is the average revenue per category?",
    "find categories where revenue is above the overall average",

    # Users related
    "which category has the most users?",
    "show me the ratio of revenue to users per category",
    "find the average number of users per category",
    "which categories have fewer than 120 users?",
    "show categories sorted by user count in descending order",

    # Growth related
    "which category has the highest growth percentage?",
    "list categories where growth percentage is above 5",
    "what is the average growth percentage across all categories?",
    "compare revenue vs growth percentage per category",
    "find categories with revenue greater than 1000 and growth percentage above 5",

    # Advanced / Multi-column
    "show a summary table with category, average revenue, and average users",
    "find the correlation between users and revenue",
    "which category has the highest revenue per user?",
    "rank categories by revenue efficiency (revenue per user)",
    "group by category and show total revenue, total users, and average growth percentage"
]

        for question in test_questions:
            print(f"\n📝 Testing: {question}")
            data = {'question': question, 'session_id': session_id}
            response = requests.post('http://localhost:8000/ask_question', data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Answer: {result['answer']}")
                print(f"   Type: {result['query_type']}")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
        
        # Cleanup
        print("\n5️⃣ Cleaning up...")
        response = requests.delete(f'http://localhost:8000/session/{session_id}')
        if response.status_code == 200:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Session deletion failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print("✅ Test file cleaned up")
    
    print("\n🎉 Debug Complete!")
    print("=" * 50)

if __name__ == "__main__":
    debug_unique_values()
