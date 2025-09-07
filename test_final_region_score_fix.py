#!/usr/bin/env python3
"""
Final test to verify the region score pie chart fix works with the API
"""

import requests
import json
import time

def test_final_region_score_fix():
    """Test the complete region score pie chart fix with the API"""
    
    print("🧪 TESTING FINAL REGION SCORE PIE CHART FIX")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test the exact question that was failing
    test_question = "create pie chart for Region on basis of score"
    
    print(f"📝 Testing question: '{test_question}'")
    print(f"🎯 Expected: Clean real scores [1.79, 0.44, 0.36]")
    print(f"❌ Previous: Garbage values [statistics, to, columns, range, rows, nWest, nEast, nNorth]")
    
    try:
        # Make API request
        response = requests.post(
            f"{base_url}/ask_question",
            json={
                "question": test_question,
                "session_id": "test_final_region_score_fix"
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
            if "Region" in answer and "East" in answer and "0.44" in answer:
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
                        
                        # Check if we got clean real scores
                        expected_values = [1.79, 0.44, 0.36]  # Sorted descending
                        expected_labels = ['West', 'East', 'North']
                        
                        if values == expected_values and labels == expected_labels:
                            print(f"🎉 SUCCESS! Got clean real scores!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        elif any(isinstance(v, str) and len(v) > 10 for v in labels):  # Check for garbage labels
                            print(f"❌ FAILED! Still contains garbage labels!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        elif any(v < 0.1 for v in values if isinstance(v, (int, float))):  # Check for garbage values
                            print(f"❌ FAILED! Still contains garbage values!")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                        else:
                            print(f"⚠️ Got different values:")
                            print(f"   Labels: {labels}")
                            print(f"   Values: {values}")
                            
                        # Check total
                        total = sum(v for v in values if isinstance(v, (int, float)))
                        print(f"📊 Total score: {total:.2f}")
                        
                        # Check for garbage values
                        garbage_indicators = ['statistics', 'to', 'columns', 'range', 'rows', 'nWest', 'nEast', 'nNorth']
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
            with open('final_region_score_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to final_region_score_test_response.json")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {base_url}?")
        print(f"   Start the server with: python backend/app.py")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_multiple_region_questions():
    """Test with different region-based questions"""
    
    print(f"\n🧪 TESTING MULTIPLE REGION QUESTIONS")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    test_questions = [
        "create pie chart for Region on basis of score",
        "show me a pie chart for region and score",
        "generate pie chart for region vs score",
        "create a pie chart showing region distribution by score"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: '{question}'")
        
        try:
            response = requests.post(
                f"{base_url}/ask_question",
                json={
                    "question": question,
                    "session_id": f"test_region_questions_{i}"
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
                    
                    # Check if values look like real scores (not garbage)
                    if all(isinstance(v, (int, float)) and v > 0.1 for v in values):
                        print(f"   🎉 SUCCESS! Real scores detected")
                    else:
                        print(f"   ⚠️ Values may be incorrect or contain garbage")
                        
                    # Check for garbage labels
                    garbage_indicators = ['statistics', 'to', 'columns', 'range', 'rows', 'nWest', 'nEast', 'nNorth']
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
    print("🚀 Starting Final Region Score Pie Chart Fix Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_final_region_score_fix()
    test_multiple_region_questions()
    
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract float values from pandas Series")
    print("2. ✅ Trigger post-processing for 'pie chart' questions")
    print("3. ✅ Show [1.79, 0.44, 0.36] instead of garbage values")
    print("4. ✅ Handle any pandas Series format (Category, Region, etc.)")
    print("\nIf you still see garbage values like [statistics, to, columns, range, rows],")
    print("the post-processor may not be triggering properly.")
    print("Check the logs for: '🔍 Post-processing answer for pie chart data...'")
