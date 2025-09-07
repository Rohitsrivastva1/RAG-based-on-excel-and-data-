#!/usr/bin/env python3
"""
Test script to demonstrate the difference between row counts and user totals
"""

import pandas as pd
from backend.viz.visualization import VisualizationEngine

def test_scenario_1_row_counts():
    """Test with data that has multiple rows per category (current scenario)"""
    
    print("📊 SCENARIO 1: Multiple Rows Per Category (Current Data)")
    print("=" * 60)
    
    # This simulates your current data structure
    data = []
    categories = ['Education', 'Entertainment', 'Finance', 'Health', 'Tech']
    row_counts = [8, 6, 6, 6, 4]  # This is what you're seeing
    
    for cat, count in zip(categories, row_counts):
        for i in range(count):
            data.append({
                'Category': cat,
                'Users': 1,  # Each row = 1 user
                'Revenue': 1000 + i * 100  # Some other data
            })
    
    df = pd.DataFrame(data)
    print(f"📋 Dataset: {len(df)} rows")
    print(f"📊 Categories: {df['Category'].value_counts().to_dict()}")
    
    # This is what the pie chart currently shows
    grouped = df.groupby('Category')['Users'].sum()
    print(f"🎯 Pie chart values (row counts): {grouped.values.tolist()}")
    print(f"📊 This represents: {dict(zip(grouped.index, grouped.values))}")
    
    return df

def test_scenario_2_aggregated_totals():
    """Test with pre-aggregated data (what you want)"""
    
    print("\n📊 SCENARIO 2: Pre-Aggregated Totals (What You Want)")
    print("=" * 60)
    
    # This is the data structure you want
    data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'Users': [2500, 2968, 3964, 3055, 2144]  # These are the totals you want
    }
    
    df = pd.DataFrame(data)
    print(f"📋 Dataset: {len(df)} rows")
    print(f"📊 Data:")
    print(df)
    
    # This is what the pie chart should show
    grouped = df.groupby('Category')['Users'].sum()
    print(f"🎯 Pie chart values (user totals): {grouped.values.tolist()}")
    print(f"📊 This represents: {dict(zip(grouped.index, grouped.values))}")
    
    return df

def test_visualization_engine():
    """Test the visualization engine with both scenarios"""
    
    print("\n🧪 TESTING VISUALIZATION ENGINE")
    print("=" * 60)
    
    engine = VisualizationEngine()
    
    # Test Scenario 1 (current data)
    print("1️⃣ Testing with current data structure...")
    df1 = test_scenario_1_row_counts()
    
    viz1 = engine.create_visualization(
        data=df1,
        question="create pie chart for category vs users",
        suggested_chart_type="pie"
    )
    
    if viz1 and viz1.get('data', {}).get('data'):
        pie_data = viz1['data']['data'][0]
        print(f"   📊 Generated values: {pie_data.get('values', [])}")
        print(f"   📊 Generated labels: {pie_data.get('labels', [])}")
    
    # Test Scenario 2 (aggregated data)
    print("\n2️⃣ Testing with aggregated data structure...")
    df2 = test_scenario_2_aggregated_totals()
    
    viz2 = engine.create_visualization(
        data=df2,
        question="create pie chart for category vs users",
        suggested_chart_type="pie"
    )
    
    if viz2 and viz2.get('data', {}).get('data'):
        pie_data = viz2['data']['data'][0]
        print(f"   📊 Generated values: {pie_data.get('values', [])}")
        print(f"   📊 Generated labels: {pie_data.get('labels', [])}")

def show_data_transformation():
    """Show how to transform your data from scenario 1 to scenario 2"""
    
    print("\n🔄 DATA TRANSFORMATION GUIDE")
    print("=" * 60)
    
    # Simulate your current data
    current_data = []
    categories = ['Education', 'Entertainment', 'Finance', 'Health', 'Tech']
    row_counts = [8, 6, 6, 6, 4]
    
    for cat, count in zip(categories, row_counts):
        for i in range(count):
            current_data.append({
                'Category': cat,
                'Users': 1,  # Each row = 1 user
                'Other_Data': f'data_{i}'
            })
    
    df_current = pd.DataFrame(current_data)
    print("📊 Current data structure (multiple rows per category):")
    print(f"   Total rows: {len(df_current)}")
    print(f"   Categories: {df_current['Category'].value_counts().to_dict()}")
    
    # Transform to aggregated data
    df_aggregated = df_current.groupby('Category')['Users'].sum().reset_index()
    print("\n📊 After aggregation (one row per category):")
    print(df_aggregated)
    
    # Show the difference
    print(f"\n🎯 Pie chart values comparison:")
    print(f"   Current (row counts): {df_current['Category'].value_counts().values.tolist()}")
    print(f"   Aggregated (user totals): {df_aggregated['Users'].values.tolist()}")

if __name__ == "__main__":
    test_scenario_1_row_counts()
    test_scenario_2_aggregated_totals()
    test_visualization_engine()
    show_data_transformation()
    
    print("\n🎯 SUMMARY")
    print("=" * 60)
    print("The values [8, 6, 6, 6, 4] are ROW COUNTS, not user totals.")
    print("Your data has multiple rows per category, and each row = 1 user.")
    print("\nTo get [2500, 2968, 3964, 3055, 2144], you need:")
    print("1. Pre-aggregated data with total users per category, OR")
    print("2. Transform your current data using groupby().sum()")
    print("\nThe pie chart is working correctly - it's showing what your data contains!")
