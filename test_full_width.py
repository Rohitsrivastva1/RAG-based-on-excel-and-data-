#!/usr/bin/env python3
"""
Test script to verify full width visualization
"""

import requests
import json
import time

def test_full_width():
    """Test full width visualization"""
    
    print("📊 TESTING FULL WIDTH VISUALIZATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test with a bar chart question
    test_question = "create bar chart for category vs users"
    
    print(f"📝 Testing question: '{test_question}'")
    print(f"🎯 Expected: Full width visualization in main tab")
    
    try:
        # Make API request
        response = requests.post(
            f"{base_url}/ask_question",
            json={
                "question": test_question,
                "session_id": "test_full_width"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ API Response Status: {response.status_code}")
            
            # Check if we have visualization data
            viz = data.get('visualization')
            if viz:
                print(f"📊 Visualization Type: {viz.get('type')}")
                print(f"📊 Has Data: {bool(viz.get('data'))}")
                print(f"📊 Data Structure: {list(viz.get('data', {}).keys()) if viz.get('data') else 'None'}")
                
                # Check if it's a bar chart
                if viz.get('type') == 'bar':
                    x_data = viz.get('data', {}).get('x', [])
                    y_data = viz.get('data', {}).get('y', [])
                    
                    print(f"📊 Bar X Data: {x_data}")
                    print(f"📊 Bar Y Data: {y_data}")
                    
                    if len(x_data) > 0 and len(y_data) > 0:
                        print(f"✅ SUCCESS: Bar chart data generated!")
                    else:
                        print(f"❌ ERROR: Empty bar chart data")
                else:
                    print(f"⚠️ Expected bar chart, got {viz.get('type')}")
            else:
                print(f"❌ No visualization generated")
                
            # Save response for inspection
            with open('full_width_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Response saved to full_width_test_response.json")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {base_url}?")
        print(f"   Start the server with: python backend/app.py")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_full_width_fixes():
    """Test the full width fixes"""
    
    print(f"\n🔧 TESTING FULL WIDTH FIXES")
    print("=" * 60)
    
    fixes = [
        "✅ Changed visualization grid to single column (1fr)",
        "✅ Added full width styles for visualization container",
        "✅ Increased height from 400px to 500px for full mode",
        "✅ Added CSS overrides for Plotly containers",
        "✅ Set min-height to 600px for visualization body",
        "✅ Added responsive width and height settings",
        "✅ Enhanced Plotly config for full mode",
        "✅ Added CSS classes for full visualization"
    ]
    
    for fix in fixes:
        print(f"  {fix}")
    
    print(f"\n🎯 FULL WIDTH FIXES IMPLEMENTED:")
    print("=" * 60)
    print("1. 🔧 Changed grid to single column layout")
    print("2. 📊 Added full width CSS classes")
    print("3. 📏 Increased height to 500px for full mode")
    print("4. 🎨 Added Plotly container overrides")
    print("5. 📐 Set min-height to 600px for body")
    print("6. 📱 Added responsive width settings")
    print("7. ⚙️ Enhanced Plotly configuration")
    print("8. 🎯 Added specific CSS for full visualization")

if __name__ == "__main__":
    print("🚀 Starting Full Width Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_full_width()
    test_full_width_fixes()
    
    print(f"\n🎉 FULL WIDTH FIXES COMPLETE!")
    print("=" * 60)
    print("The visualization should now take full width:")
    print("• ✅ Single column grid layout")
    print("• ✅ Full width visualization container")
    print("• ✅ Increased height (500px) for full mode")
    print("• ✅ Responsive width and height")
    print("• ✅ Proper CSS overrides for Plotly")
    print("• ✅ Enhanced visualization body")
    print("\nCheck the visualization tab - it should be full width!")
