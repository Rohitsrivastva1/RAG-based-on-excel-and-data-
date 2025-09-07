#!/usr/bin/env python3
"""
Test script to create and display a pie chart for category vs number of users
"""

import pandas as pd
import json
from backend.viz.visualization import VisualizationEngine

def test_pie_chart_creation():
    """Test creating a pie chart with the provided data"""
    
    print("🧪 TESTING PIE CHART CREATION")
    print("=" * 50)
    
    # Create sample data based on the provided information
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'Users': [2500, 2968, 3964, 3055, 2144]
    }
    
    df = pd.DataFrame(data)
    print(f"📊 Sample Data:")
    print(df)
    print()
    
    # Initialize visualization engine
    engine = VisualizationEngine()
    
    # Test pie chart creation
    print("🎯 Creating pie chart...")
    viz_data = engine.create_visualization(
        data=df,
        question="create pie chart for category vs no of user in each category",
        suggested_chart_type="pie",
        theme="dark"
    )
    
    if viz_data:
        print("✅ Pie chart created successfully!")
        print(f"📊 Chart Type: {viz_data.get('type', 'unknown')}")
        print(f"📊 Title: {viz_data.get('title', 'No title')}")
        
        # Print the data structure
        data_section = viz_data.get('data', {})
        if 'labels' in data_section and 'values' in data_section:
            print(f"📊 Labels: {data_section['labels']}")
            print(f"📊 Values: {data_section['values']}")
        elif 'data' in data_section:
            # Handle nested Plotly data
            plotly_data = data_section['data']
            if isinstance(plotly_data, list) and len(plotly_data) > 0:
                pie_data = plotly_data[0]
                print(f"📊 Plotly Labels: {pie_data.get('labels', [])}")
                print(f"📊 Plotly Values: {pie_data.get('values', [])}")
        
        # Save visualization data for frontend testing
        with open('test_pie_chart_data.json', 'w') as f:
            json.dump(viz_data, f, indent=2)
        print("💾 Visualization data saved to test_pie_chart_data.json")
        
        # Print the full structure for debugging
        print("\n🔍 Full Visualization Structure:")
        print(json.dumps(viz_data, indent=2))
        
    else:
        print("❌ Failed to create pie chart")
        return False
    
    return True

def test_with_different_data_formats():
    """Test with different data formats"""
    
    print("\n🧪 TESTING DIFFERENT DATA FORMATS")
    print("=" * 50)
    
    engine = VisualizationEngine()
    
    # Test 1: Dictionary format
    print("1. Testing dictionary format...")
    dict_data = {
        'x': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'y': [2500, 2968, 3964, 3055, 2144],
        'title': 'Users by Category'
    }
    
    viz1 = engine.create_visualization(
        data=dict_data,
        question="pie chart for users by category",
        suggested_chart_type="pie"
    )
    
    if viz1:
        print("✅ Dictionary format works")
    else:
        print("❌ Dictionary format failed")
    
    # Test 2: DataFrame with different column names
    print("\n2. Testing DataFrame with different columns...")
    df2 = pd.DataFrame({
        'Category_Name': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'User_Count': [2500, 2968, 3964, 3055, 2144]
    })
    
    viz2 = engine.create_visualization(
        data=df2,
        question="show distribution of users across categories",
        suggested_chart_type="pie"
    )
    
    if viz2:
        print("✅ DataFrame with different columns works")
    else:
        print("❌ DataFrame with different columns failed")

if __name__ == "__main__":
    success = test_pie_chart_creation()
    test_with_different_data_formats()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("📝 Next steps:")
        print("   1. Start the backend server")
        print("   2. Start the frontend")
        print("   3. Ask: 'create pie chart for category vs no of user in each category'")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
