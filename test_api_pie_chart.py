#!/usr/bin/env python3
"""
Test script to verify the API can generate pie charts correctly
"""

import requests
import json
import time
import pandas as pd

def test_api_pie_chart():
    """Test the API endpoint for pie chart generation"""
    
    print("🧪 TESTING API PIE CHART GENERATION")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test data
    test_questions = [
        {
            "question": "create pie chart for category vs no of user in each category",
            "expected_type": "pie",
            "description": "Pie chart for user distribution by category"
        },
        {
            "question": "show me a pie chart showing the distribution of users across different categories",
            "expected_type": "pie", 
            "description": "Alternative pie chart request"
        },
        {
            "question": "generate a pie chart for category and users",
            "expected_type": "pie",
            "description": "Simple pie chart request"
        }
    ]
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Question: '{test_case['question']}'")
        print(f"   Expected: {test_case['expected_type']}")
        
        try:
            # Make request to the API
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": test_case['question'],
                    "session_id": f"test_pie_api_{i}"
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
                    
                    # Check if it's a pie chart
                    if viz_type == 'pie':
                        print(f"   ✅ CORRECT: Got expected pie chart")
                        
                        # Check pie chart data structure
                        if 'data' in viz_data and isinstance(viz_data['data'], list):
                            pie_data = viz_data['data'][0]
                            labels = pie_data.get('labels', [])
                            values = pie_data.get('values', [])
                            
                            print(f"   📊 Pie Labels: {labels}")
                            print(f"   📊 Pie Values: {values}")
                            print(f"   📊 Total Values: {sum(values) if values else 0}")
                            
                            if labels and values and len(labels) == len(values):
                                print(f"   ✅ Data structure is valid")
                            else:
                                print(f"   ⚠️  Data structure issue: {len(labels)} labels, {len(values)} values")
                        else:
                            print(f"   ⚠️  Unexpected data structure")
                    else:
                        print(f"   ⚠️  MISMATCH: Expected pie, got {viz_type}")
                else:
                    print(f"   ❌ No visualization generated")
                
                # Show answer snippet
                answer = data.get('answer', 'No answer')
                print(f"   💬 Answer: {answer[:100]}...")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Is the server running on {base_url}?")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 40)

def test_with_sample_data():
    """Test with actual sample data upload"""
    
    print("\n🧪 TESTING WITH SAMPLE DATA UPLOAD")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Create sample data
    sample_data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'Users': [2500, 2968, 3964, 3055, 2144],
        'Revenue': [100000, 120000, 150000, 110000, 90000]
    }
    
    df = pd.DataFrame(sample_data)
    csv_content = df.to_csv(index=False)
    
    try:
        # Upload sample data
        print("📤 Uploading sample data...")
        files = {'file': ('test_data.csv', csv_content, 'text/csv')}
        upload_response = requests.post(f"{base_url}/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            print("✅ Sample data uploaded successfully")
            
            # Now test pie chart generation
            print("🎯 Testing pie chart generation with uploaded data...")
            
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": "create a pie chart showing the distribution of users by category",
                    "session_id": "test_upload_pie"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                viz = data.get('visualization')
                
                if viz and viz.get('type') == 'pie':
                    print("✅ Pie chart generated successfully from uploaded data!")
                    
                    # Save the result for inspection
                    with open('api_pie_chart_result.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print("💾 Result saved to api_pie_chart_result.json")
                else:
                    print("❌ Failed to generate pie chart from uploaded data")
            else:
                print(f"❌ API Error: {response.status_code}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in sample data test: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Pie Chart Tests")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_api_pie_chart()
    test_with_sample_data()
    
    print("\n🎉 API tests completed!")
    print("📝 To test the frontend:")
    print("   1. Open test_pie_chart_frontend.html in a browser")
    print("   2. Or start the React frontend and ask for a pie chart")
