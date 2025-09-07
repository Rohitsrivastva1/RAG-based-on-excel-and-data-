#!/usr/bin/env python3
"""
Final test to verify the complete pie chart fix works with the API
"""

import requests
import json
import time

def test_final_pie_fix():
    """Test the complete pie chart fix with the API"""
    
    print("🧪 TESTING FINAL PIE CHART FIX")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test the exact question that was failing
    test_question = "create pie chart for category vs no of user in each category"
    
    print(f"📝 Testing question: '{test_question}'")
    print(f"🎯 Expected: Clean real counts [3964, 3055, 2968, 2500, 2144]")
    print(f"❌ Previous: Mixed with garbage [nFinance, nHealth, ..., range, statistics, 22, 23, 24, ...]")
    
    try:
        # Make API request
        response = requests.post(
            f"{base_url}/ask_question",
            json={
                "question": test_question,
                "session_id": "test_final_pie_fix"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check answer
            answer = data.get('answer', '')
            print(f"\n✅ Status: {response.status_code}")
            print(f"💬 Answer preview: {answer[:200]}...")
            
            # Check if answer contains pandas series format
            if "Category" in answer and "Education" in answer and "2500" in answer:
                print(f"✅ Answer contains pandas series format!")
            else:
                print(f"⚠️ Answer may not contain expected format")
            
            # Check visualization
            viz = data.get('visualization')
            if viz:
                viz_type = viz.get('type', 'unknown')
                viz_data = viz.get('data', {})
                
                print(f"\n📊 Visualization Type: {viz_type}")
                print(f"📊 Title: {viz.get('title', 'No title')}")
                
                if viz_type == 'pie':
                    # Check pie chart data structure
                    if 'labels' in viz_data and 'values' in viz_data:
                        labels = viz_data['labels']
                        values = viz_data['values']
                        
                        print(f"📊 Pie Labels: {labels}")
                        print(f"📊 Pie Values: {values}")
                        
                        # Check if we got clean real counts
                        expected_values = [3964, 3055, 2968, 2500, 2144]  # Sorted descending
                        expected_labels = ['Finance', 'Health', 'Entertainment', 'Education', 'Tech']
                        
                        if values == expected_values and labels == expected_labels:
                            print(f"🎉 SUCCESS! Got clean real counts!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        elif any(isinstance(v, str) and len(v) > 10 for v in labels):  # Check for garbage labels
                            print(f"❌ FAILED! Still contains garbage labels!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        elif any(v < 100 for v in values if isinstance(v, (int, float))):  # Check for garbage values
                            print(f"❌ FAILED! Still contains garbage values!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        else:
                            print(f"⚠️ Got different values:")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                            
                        # Check total
                        total = sum(v for v in values if isinstance(v, (int, float)))
                        print(f"📊 Total users: {total:,}")
                        
                        # Check for garbage values
                        garbage_indicators = ['range', 'statistics', '22', '23', '24', 'to', '19', 'columns', 'rows', 'nFinance', 'nHealth']
                        has_garbage = any(indicator in str(labels) for indicator in garbage_indicators)
                        if has_garbage:
                            print(f"❌ WARNING: Still contains garbage indicators!")
                        else:
                            print(f"✅ Clean data - no garbage indicators found!")
                        
                    else:
                        print(f"❌ Unexpected pie chart data structure")
                        print(f"   Data keys: {list(viz_data.keys())}")
                else:
                    print(f"⚠️ Expected pie chart, got {viz_type}")
            else:
                print(f"❌ No visualization generated")
                
            # Save the full response for inspection
            with open('final_pie_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to final_pie_test_response.json")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {base_url}?")
        print(f"   Start the server with: python backend/app.py")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_multiple_formats():
    """Test with different question formats"""
    
    print(f"\n🧪 TESTING MULTIPLE QUESTION FORMATS")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    test_questions = [
        "create pie chart for category vs no of user in each category",
        "show me a pie chart showing the distribution of users by category",
        "generate a pie chart for category and users",
        "create a pie chart for users by category"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: '{question}'")
        
        try:
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": question,
                    "session_id": f"test_multiple_formats_{i}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                viz = data.get('visualization')
                
                if viz and viz.get('type') == 'pie':
                    values = viz.get('data', {}).get('values', [])
                    labels = viz.get('data', {}).get('labels', [])
                    
                    print(f"   ✅ Pie chart generated")
                    print(f"   📊 Labels: {labels}")
                    print(f"   📊 Values: {values}")
                    
                    # Check if values look like real counts (not garbage)
                    if all(isinstance(v, (int, float)) and v > 100 for v in values):
                        print(f"   🎉 SUCCESS! Real counts detected")
                    else:
                        print(f"   ⚠️ Values may be incorrect or contain garbage")
                        
                    # Check for garbage labels
                    garbage_indicators = ['range', 'statistics', '22', '23', '24', 'to', '19', 'columns', 'rows', 'nFinance', 'nHealth']
                    has_garbage = any(indicator in str(labels) for indicator in garbage_indicators)
                    if has_garbage:
                        print(f"   ❌ WARNING: Contains garbage labels!")
                    else:
                        print(f"   ✅ Clean labels!")
                else:
                    print(f"   ❌ No pie chart generated")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Final Pie Chart Fix Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_final_pie_fix()
    test_multiple_formats()
    
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract pandas Series format from LLM answers")
    print("2. ✅ Build clean pie charts with only real data")
    print("3. ✅ Show [3964, 3055, 2968, 2500, 2144] without garbage values")
    print("4. ✅ Replace regular visualization to avoid junk tokens")
    print("\nIf you still see garbage values like [range, statistics, 22, 23, 24],")
    print("the post-processor may not be triggering properly.")
    print("Check the logs for: '🔍 Post-processing answer for pie chart data...'")
