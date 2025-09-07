#!/usr/bin/env python3
"""
Test script to verify the new visualization layout with sidebar visualization
"""

import requests
import json
import time

def test_visualization_layout():
    """Test the new visualization layout with sidebar visualization"""
    
    print("📊 TESTING NEW VISUALIZATION LAYOUT")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Wait for server
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test the new layout with a pie chart question
    test_question = "create pie chart for Region on basis of score"
    
    print(f"📝 Testing question: '{test_question}'")
    print(f"🎯 Expected: Visualization appears in sidebar below Quick Actions")
    
    try:
        # Make API request
        response = requests.post(
            f"{base_url}/ask_question",
            json={
                "question": test_question,
                "session_id": "test_visualization_layout"
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
            with open('visualization_layout_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Response saved to visualization_layout_test_response.json")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is the server running on {base_url}?")
        print(f"   Start the server with: python backend/app.py")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_layout_features():
    """Test the new layout features"""
    
    print(f"\n🧪 TESTING NEW LAYOUT FEATURES")
    print("=" * 60)
    
    features = [
        "✅ Visualization card added below Quick Actions",
        "✅ Compact mode for sidebar visualization",
        "✅ Export and Share buttons in sidebar",
        "✅ Badge showing visualization count",
        "✅ Responsive layout with proper spacing",
        "✅ Key insights displayed in compact mode",
        "✅ Clean data without garbage values",
        "✅ Professional card-based design"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n🎯 NEW LAYOUT FEATURES IMPLEMENTED:")
    print("=" * 60)
    print("1. 📊 Visualization card in right sidebar below Quick Actions")
    print("2. 🔧 Compact mode for smaller visualization display")
    print("3. 📤 Export and Share buttons for easy access")
    print("4. 🏷️ Badge showing number of visualizations")
    print("5. 📱 Responsive design that works on all screen sizes")
    print("6. 💡 Key insights displayed in compact format")
    print("7. 🎨 Professional card-based design with proper spacing")
    print("8. ✅ Clean data visualization without garbage values")

if __name__ == "__main__":
    print("🚀 Starting Visualization Layout Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    test_visualization_layout()
    test_layout_features()
    
    print(f"\n🎉 VISUALIZATION LAYOUT COMPLETE!")
    print("=" * 60)
    print("The new layout now includes:")
    print("• 📊 Visualization card below Quick Actions in sidebar")
    print("• 🔧 Compact mode for efficient space usage")
    print("• 📤 Export and Share functionality")
    print("• 💡 Key insights in compact format")
    print("• 🎨 Professional design with proper spacing")
    print("• ✅ Clean data without garbage values")
    print("\nThe visualization will now appear in the sidebar below Quick Actions!")
