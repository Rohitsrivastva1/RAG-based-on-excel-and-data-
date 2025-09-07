#!/usr/bin/env python3
"""
Test script to verify pie chart visualization fix
"""

import requests
import json
import time

def test_pie_chart_fix():
    """Test the pie chart visualization fix"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 TESTING PIE CHART VISUALIZATION FIX")
    print("=" * 50)
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    test_cases = [
        {
            "name": "Pie chart for category distribution",
            "question": "show me pie chart for distribution of category",
            "expected_type": "pie"
        },
        {
            "name": "Bar chart for category and revenue",
            "question": "generate a bar graph for category and revenue",
            "expected_type": "bar"
        },
        {
            "name": "Line chart for trends",
            "question": "create a line chart showing revenue over time",
            "expected_type": "line"
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
                    viz_data = viz.get('data', {})
                    
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   📊 Visualization Type: {viz_type}")
                    print(f"   📊 Title: {viz.get('title', 'No title')}")
                    
                    # Check if data is populated
                    if viz_data:
                        print(f"   ✅ Data populated: {len(viz_data)} fields")
                        if viz_type == "pie":
                            labels = viz_data.get('labels', [])
                            values = viz_data.get('values', [])
                            print(f"   📊 Pie chart - Labels: {len(labels)}, Values: {len(values)}")
                        elif viz_type == "bar":
                            x_data = viz_data.get('x', [])
                            y_data = viz_data.get('y', [])
                            print(f"   📊 Bar chart - X: {len(x_data)}, Y: {len(y_data)}")
                        elif viz_type == "line":
                            x_data = viz_data.get('x', [])
                            y_data = viz_data.get('y', [])
                            print(f"   📊 Line chart - X: {len(x_data)}, Y: {len(y_data)}")
                    else:
                        print(f"   ❌ Data is empty!")
                    
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
    test_pie_chart_fix()
