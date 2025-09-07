#!/usr/bin/env python3
"""
Diagnostic script to understand the data structure and pie chart values
"""

import pandas as pd
import json

def analyze_data_structure():
    """Analyze the data structure to understand the pie chart values"""
    
    print("🔍 DIAGNOSING DATA STRUCTURE ISSUE")
    print("=" * 50)
    
    # Let's check what data might be in your system
    print("📊 Checking for data files...")
    
    # Check if there's sample data
    try:
        df = pd.read_csv('sample_data.csv')
        print(f"✅ Found sample_data.csv with {len(df)} rows")
        print(f"📋 Columns: {list(df.columns)}")
        print("\n📊 Sample data:")
        print(df.head())
        
        # Check if there are multiple rows per category
        if 'department' in df.columns:
            print(f"\n🔍 Department value counts:")
            print(df['department'].value_counts())
            
            # Check if we should sum something
            numeric_cols = df.select_dtypes(include=['number']).columns
            print(f"\n📈 Numeric columns: {list(numeric_cols)}")
            
            if len(numeric_cols) > 0:
                print(f"\n📊 Sum by department for {numeric_cols[0]}:")
                grouped = df.groupby('department')[numeric_cols[0]].sum()
                print(grouped)
                
                print(f"\n📊 Count by department:")
                count_grouped = df.groupby('department').size()
                print(count_grouped)
                
                # This might explain the [8, 6, 6, 6, 4] values!
                if list(count_grouped.values) == [8, 6, 6, 6, 4]:
                    print("\n🎯 FOUND THE ISSUE!")
                    print("The pie chart is showing ROW COUNTS instead of SUM of values!")
                    print("This happens when the visualization engine uses .count() instead of .sum()")
        
    except FileNotFoundError:
        print("❌ No sample_data.csv found")
    
    # Check for other data files
    import os
    data_files = []
    for file in os.listdir('.'):
        if file.endswith(('.csv', '.xlsx', '.xls')):
            data_files.append(file)
    
    if data_files:
        print(f"\n📁 Found data files: {data_files}")
    else:
        print("\n📁 No data files found in current directory")
    
    # Let's create a test with the expected data structure
    print("\n🧪 Creating test data with expected structure...")
    
    # This is what your data SHOULD look like for the pie chart
    expected_data = {
        'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech'],
        'Users': [2500, 2968, 3964, 3055, 2144]
    }
    
    df_expected = pd.DataFrame(expected_data)
    print("📊 Expected data structure:")
    print(df_expected)
    
    # Test the grouping
    grouped = df_expected.groupby('Category')['Users'].sum()
    print(f"\n📊 Grouped result (what pie chart should show):")
    print(grouped)
    print(f"Values: {grouped.values.tolist()}")
    
    # Now let's simulate what might be happening with row counts
    print(f"\n🔍 Simulating row count issue...")
    
    # Create data that would give [8, 6, 6, 6, 4] counts
    problematic_data = []
    categories = ['Education', 'Entertainment', 'Finance', 'Health', 'Tech']
    counts = [8, 6, 6, 6, 4]
    
    for cat, count in zip(categories, counts):
        for i in range(count):
            problematic_data.append({
                'Category': cat,
                'Users': 1,  # Each row has 1 user
                'Other_Data': f'data_{i}'
            })
    
    df_problematic = pd.DataFrame(problematic_data)
    print(f"📊 Problematic data (would give counts [8, 6, 6, 6, 4]):")
    print(f"Total rows: {len(df_problematic)}")
    print(f"Category counts: {df_problematic['Category'].value_counts().tolist()}")
    
    # This is what's probably happening
    count_result = df_problematic.groupby('Category').size()
    sum_result = df_problematic.groupby('Category')['Users'].sum()
    
    print(f"\n❌ WRONG: Using .size() (row counts): {count_result.values.tolist()}")
    print(f"✅ CORRECT: Using .sum() (user totals): {sum_result.values.tolist()}")

def check_visualization_logic():
    """Check the visualization logic to see if it's using count vs sum"""
    
    print("\n🔍 CHECKING VISUALIZATION LOGIC")
    print("=" * 50)
    
    # Read the visualization code
    with open('backend/viz/visualization.py', 'r') as f:
        content = f.read()
    
    # Look for the pie chart logic
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'groupby' in line and 'sum' in line:
            print(f"Line {i+1}: {line.strip()}")
            # Show context
            for j in range(max(0, i-2), min(len(lines), i+3)):
                if j != i:
                    print(f"  {j+1}: {lines[j].strip()}")
            print()

if __name__ == "__main__":
    analyze_data_structure()
    check_visualization_logic()
    
    print("\n🎯 SUMMARY")
    print("=" * 50)
    print("The values [8, 6, 6, 6, 4] are likely ROW COUNTS, not user totals.")
    print("This suggests your dataset has multiple rows per category,")
    print("and the visualization is counting rows instead of summing values.")
    print("\nTo fix this, ensure the visualization uses .sum() not .count()")
    print("and that your data has the correct structure for aggregation.")
