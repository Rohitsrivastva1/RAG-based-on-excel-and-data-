#!/usr/bin/env python3
"""
Test script to verify visualization fixes
"""

import requests
import json
import time

def test_visualization_fixes():
    """Test the improved visualization detection"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 TESTING IMPROVED VISUALIZATION DETECTION")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    test_cases = [
        {
            "name": "Bar chart with specific columns",
            "question": "generate a bar graph for category and revenue",
            "expected_type": "bar"
        },
        {
            "name": "General chart request",
            "question": "show me a chart of the data",
            "expected_type": "bar"
        },
        {
            "name": "Line chart request",
            "question": "create a line chart showing trends",
            "expected_type": "line"
        },
        {
            "name": "Pie chart request",
            "question": "make a pie chart for distribution",
            "expected_type": "pie"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Question: '{test_case['question']}'")
        print(f"   Expected: {test_case['expected_type']}")
        
        try:
            # Make request
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": test_case['question'],
                    "session_id": f"test_viz_fix_{i}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                viz = data.get('visualization')
                
                if viz:
                    viz_type = viz.get('type', 'unknown')
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   📊 Visualization Type: {viz_type}")
                    print(f"   📊 Title: {viz.get('title', 'No title')}")
                    
                    if viz_type == test_case['expected_type']:
                        print(f"   ✅ CORRECT: Got expected {viz_type} chart")
                    else:
                        print(f"   ⚠️  MISMATCH: Expected {test_case['expected_type']}, got {viz_type}")
                else:
                    print(f"   ❌ No visualization generated")
                
                print(f"   💬 Answer: {data.get('answer', 'No answer')[:100]}...")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_visualization_fixes()
