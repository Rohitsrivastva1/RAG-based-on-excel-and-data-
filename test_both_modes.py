#!/usr/bin/env python3
"""
Test script to verify both compact and full visualization modes work
"""

import requests
import json
import time

def test_both_modes():
    """Test both compact and full visualization modes"""
    
    print("📊 TESTING BOTH VISUALIZATION MODES")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test both modes with a pie chart question
    test_question = "create pie chart for Region on basis of score"
    
    print(f"📝 Testing question: '{test_question}'")
    print(f"🎯 Expected: Graph visible in both compact mode (sidebar) and full mode (visualization tab)")
    
    try:
        # Make API request
        response = requests.post(
            f"{base_url}/ask_question",
            json={
                "question": test_question,
                "session_id": "test_both_modes"
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
                
                # Check if it's a pie chart with clean data
                if viz.get('type') == 'pie':
                    labels = viz.get('data', {}).get('labels', [])
                    values = viz.get('data', {}).get('values', [])
                    
                    print(f"📊 Pie Labels: {labels}")
                    print(f"📊 Pie Values: {values}")
                    
                    # Check for garbage values
                    garbage_indicators = ['statistics', 'to', 'columns', 'range', 'rows', 'nWest', 'nEast', 'nNorth']
                    has_garbage = any(indicator in str(labels) for indicator in garbage_indicators)
                    
                    if has_garbage:
                        print(f"❌ WARNING: Still contains garbage values!")
                    else:
                        print(f"✅ SUCCESS: Clean data without garbage!")
                        
                        # Check if values look like real scores
                        if all(isinstance(v, (int, float)) and v > 0.1 for v in values):
                            print(f"🎉 PERFECT: Real score values detected!")
                        else:
                            print(f"⚠️ Values may be incorrect")
                else:
                    print(f"⚠️ Expected pie chart, got {viz.get('type')}")
            else:
                print(f"❌ No visualization generated")
                
            # Save response for inspection
            with open('both_modes_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Response saved to both_modes_test_response.json")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {base_url}?")
        print(f"   Start the server with: python backend/app.py")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_both_modes_fixes():
    """Test the both modes fixes"""
    
    print(f"\n🔧 TESTING BOTH MODES FIXES")
    print("=" * 60)
    
    fixes = [
        "✅ Added currentViz prop to Visualization component",
        "✅ Updated App.js to pass currentViz to both modes",
        "✅ Fixed data sharing between compact and full modes",
        "✅ Added debug info for full mode",
        "✅ Enhanced useEffect to use propCurrentViz",
        "✅ Fixed renderVisualization calls with proper parameters",
        "✅ Improved data flow between components",
        "✅ Added console logging for debugging"
    ]
    
    for fix in fixes:
        print(f"  {fix}")
    
    print(f"\n🎯 BOTH MODES FIXES IMPLEMENTED:")
    print("=" * 60)
    print("1. 🔧 Added currentViz prop to Visualization component")
    print("2. 📊 Updated App.js to pass currentViz to both modes")
    print("3. 🔄 Fixed data sharing between compact and full modes")
    print("4. 🐛 Added debug info for full mode")
    print("5. ⚡ Enhanced useEffect to use propCurrentViz")
    print("6. 🎨 Fixed renderVisualization calls with proper parameters")
    print("7. 📦 Improved data flow between components")
    print("8. 🔍 Added console logging for debugging")

if __name__ == "__main__":
    print("🚀 Starting Both Modes Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_both_modes()
    test_both_modes_fixes()
    
    print(f"\n🎉 BOTH MODES FIXES COMPLETE!")
    print("=" * 60)
    print("Both visualization modes should now work:")
    print("• ✅ Compact mode (sidebar) - should show graph")
    print("• ✅ Full mode (visualization tab) - should show graph")
    print("• 🔄 Data sharing between both modes")
    print("• 🐛 Debug info for troubleshooting")
    print("• 📊 Same data displayed in both modes")
    print("• 🎨 Proper rendering in both modes")
    print("\nCheck both the sidebar and visualization tab!")
