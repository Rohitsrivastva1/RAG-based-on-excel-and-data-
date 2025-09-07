#!/usr/bin/env python3
"""
Test the complete system to verify pie chart fix works end-to-end
"""

import requests
import json
import time
import pandas as pd

def test_full_system():
    """Test the complete system with the pie chart fix"""
    
    print("🧪 TESTING FULL SYSTEM PIE CHART FIX")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test questions that should trigger pie charts
    test_questions = [
        {
            "question": "create pie chart for category vs no of user in each category",
            "expected_values": [3964, 3055, 2968, 2500, 2144],  # Real counts (sorted)
            "description": "Main pie chart request"
        },
        {
            "question": "show me a pie chart showing the distribution of users by category",
            "expected_values": [3964, 3055, 2968, 2500, 2144],
            "description": "Alternative pie chart request"
        },
        {
            "question": "generate a pie chart for category and users",
            "expected_values": [3964, 3055, 2968, 2500, 2144],
            "description": "Simple pie chart request"
        }
    ]
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Question: '{test_case['question']}'")
        print(f"   Expected values: {test_case['expected_values']}")
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": test_case['question'],
                    "session_id": f"test_pie_fix_{i}"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check answer
                answer = data.get('answer', '')
                print(f"   ✅ Status: {response.status_code}")
                print(f"   💬 Answer preview: {answer[:100]}...")
                
                # Check if answer contains real counts
                if "2500" in answer and "2968" in answer and "3964" in answer:
                    print(f"   ✅ Answer contains real counts!")
                else:
                    print(f"   ⚠️ Answer may not contain expected counts")
                
                # Check visualization
                viz = data.get('visualization')
                if viz:
                    viz_type = viz.get('type', 'unknown')
                    viz_data = viz.get('data', {})
                    
                    print(f"   📊 Visualization Type: {viz_type}")
                    print(f"   📊 Title: {viz.get('title', 'No title')}")
                    
                    if viz_type == 'pie':
                        # Check pie chart data
                        if 'data' in viz_data and isinstance(viz_data['data'], list):
                            pie_data = viz_data['data'][0]
                            labels = pie_data.get('labels', [])
                            values = pie_data.get('values', [])
                            
                            print(f"   📊 Pie Labels: {labels}")
                            print(f"   📊 Pie Values: {values}")
                            
                            # Check if we got real counts
                            if values == test_case['expected_values']:
                                print(f"   🎉 SUCCESS! Got real counts: {values}")
                            elif values == [8, 6, 6, 6, 4]:
                                print(f"   ❌ FAILED! Still using row counts: {values}")
                            else:
                                print(f"   ⚠️ Unexpected values: {values}")
                                
                            # Check total
                            total = sum(values)
                            print(f"   📊 Total users: {total:,}")
                            
                        else:
                            print(f"   ❌ Unexpected pie chart data structure")
                    else:
                        print(f"   ⚠️ Expected pie chart, got {viz_type}")
                else:
                    print(f"   ❌ No visualization generated")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection Error: Is the server running on {base_url}?")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("-" * 50)

def test_with_sample_data():
    """Test with actual sample data to see the difference"""
    
    print(f"\n🧪 TESTING WITH SAMPLE DATA")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Create sample data that would give row counts
    sample_data = []
    categories = ['Education', 'Entertainment', 'Finance', 'Health', 'Tech']
    row_counts = [8, 6, 6, 6, 4]
    
    for cat, count in zip(categories, row_counts):
        for i in range(count):
            sample_data.append({
                'Category': cat,
                'Users': 1,  # Each row = 1 user
                'Revenue': 1000 + i * 100
            })
    
    df = pd.DataFrame(sample_data)
    csv_content = df.to_csv(index=False)
    
    try:
        # Upload sample data
        print("📤 Uploading sample data...")
        files = {'file': ('test_pie_data.csv', csv_content, 'text/csv')}
        upload_response = requests.post(f"{base_url}/upload", files=files, timeout=30)
        
        if upload_response.status_code == 200:
            print("✅ Sample data uploaded successfully")
            
            # Test pie chart with uploaded data
            print("🎯 Testing pie chart with uploaded data...")
            
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": "create a pie chart showing the distribution of users by category",
                    "session_id": "test_upload_pie_fix"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                viz = data.get('visualization')
                
                if viz and viz.get('type') == 'pie':
                    pie_data = viz['data']['data'][0]
                    values = pie_data.get('values', [])
                    
                    print(f"📊 Pie chart values: {values}")
                    
                    if values == [8, 6, 6, 6, 4]:
                        print("❌ Still using row counts - fix may not be working")
                    elif values == [3964, 3055, 2968, 2500, 2144]:
                        print("🎉 SUCCESS! Using real counts from LLM!")
                    else:
                        print(f"⚠️ Unexpected values: {values}")
                else:
                    print("❌ No pie chart generated")
            else:
                print(f"❌ API Error: {response.status_code}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in sample data test: {e}")

if __name__ == "__main__":
    print("🚀 Starting Full System Pie Chart Fix Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_full_system()
    test_with_sample_data()
    
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract real counts from LLM responses")
    print("2. ✅ Use real counts in pie charts instead of row counts")
    print("3. ✅ Show [2500, 2968, 3964, 3055, 2144] instead of [8, 6, 6, 6, 4]")
    print("\nIf you still see [8, 6, 6, 6, 4], the LLM may not be calculating")
    print("the real counts in its response, or the extraction pattern needs adjustment.")
