#!/usr/bin/env python3
"""
Test script to debug visualization issues
"""

import requests
import json

def test_visualization():
    """Test different visualization requests"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Bar chart request",
            "question": "generate a bar graph for category and revenue"
        },
        {
            "name": "Line chart request", 
            "question": "create a line chart showing revenue over time"
        },
        {
            "name": "Pie chart request",
            "question": "make a pie chart for category distribution"
        },
        {
            "name": "General chart request",
            "question": "show me a chart of the data"
        }
    ]
    
    print("🧪 TESTING VISUALIZATION DETECTION")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Question: '{test_case['question']}'")
        
        try:
            # Make request
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": test_case['question'],
                    "session_id": f"test_viz_{i}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Visualization: {data.get('visualization', 'None')}")
                print(f"   💬 Answer: {data.get('answer', 'No answer')[:100]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_visualization()
