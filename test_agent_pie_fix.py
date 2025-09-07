#!/usr/bin/env python3
"""
Test script to verify the agent pie chart fix
"""

import pandas as pd
from backend.agents.llm_agent import LLMAgent

def test_pie_chart_extraction():
    """Test the pie chart extraction from LLM results"""
    
    print("🧪 TESTING AGENT PIE CHART FIX")
    print("=" * 50)
    
    # Create test data (simulating your current data structure)
    data = []
    categories = ['Education', 'Entertainment', 'Finance', 'Health', 'Tech']
    row_counts = [8, 6, 6, 6, 4]  # This is what the DataFrame would show
    
    for cat, count in zip(categories, row_counts):
        for i in range(count):
            data.append({
                'Category': cat,
                'Users': 1,  # Each row = 1 user
                'Revenue': 1000 + i * 100
            })
    
    df = pd.DataFrame(data)
    print(f"📊 Test DataFrame: {len(df)} rows")
    print(f"📊 Category distribution: {df['Category'].value_counts().to_dict()}")
    
    # Simulate LLM result with real counts
    llm_result = """
    Here's the data suitable for creating a pie chart showing the number of users per category:

    Category
    Education        2500
    Entertainment    2968
    Finance          3964
    Health           3055
    Tech             2144
    Name: Users, dtype: int64
    """
    
    print(f"\n🤖 Simulated LLM Result:")
    print(llm_result)
    
    # Test the extraction method
    agent = LLMAgent()
    
    # Test the extraction directly
    extracted = agent._extract_counts_from_llm_result(llm_result, 'Category')
    if extracted:
        print(f"\n✅ Extraction successful!")
        print(f"📊 Labels: {extracted['labels']}")
        print(f"📊 Values: {extracted['values']}")
        
        # Compare with expected
        expected = {
            'Finance': 3964,
            'Entertainment': 2968, 
            'Health': 3055,
            'Education': 2500,
            'Tech': 2144
        }
        
        print(f"\n🎯 Expected values: {expected}")
        
        # Check if we got the right values
        extracted_dict = dict(zip(extracted['labels'], extracted['values']))
        if extracted_dict == expected:
            print("✅ PERFECT MATCH! Real counts extracted correctly")
        else:
            print("⚠️ Partial match - some values may be different")
            print(f"Extracted: {extracted_dict}")
    else:
        print("❌ Extraction failed")
    
    # Test the full pie chart visualization
    print(f"\n🧪 Testing full pie chart visualization...")
    viz = agent._create_pie_chart_visualization(df, "create pie chart for category vs users", llm_result)
    
    if viz and viz.get('data'):
        pie_data = viz['data']
        print(f"✅ Pie chart created successfully!")
        print(f"📊 Type: {viz.get('type')}")
        print(f"📊 Labels: {pie_data.get('labels', [])}")
        print(f"📊 Values: {pie_data.get('values', [])}")
        
        # Check if we got real counts or row counts
        values = pie_data.get('values', [])
        if values == [3964, 3055, 2968, 2500, 2144]:  # Real counts (sorted)
            print("🎉 SUCCESS! Using real counts from LLM result!")
        elif values == [8, 6, 6, 6, 4]:  # Row counts
            print("❌ Still using row counts - extraction failed")
        else:
            print(f"⚠️ Unexpected values: {values}")
    else:
        print("❌ Pie chart creation failed")

def test_different_llm_formats():
    """Test extraction with different LLM result formats"""
    
    print(f"\n🧪 TESTING DIFFERENT LLM RESULT FORMATS")
    print("=" * 50)
    
    agent = LLMAgent()
    
    test_cases = [
        {
            "name": "Format 1: Category: Value",
            "text": "Education: 2500\nEntertainment: 2968\nFinance: 3964\nHealth: 3055\nTech: 2144",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "Format 2: Category Value (space separated)",
            "text": "Education 2500\nEntertainment 2968\nFinance 3964\nHealth 3055\nTech 2144",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "Format 3: Mixed format",
            "text": "Here are the results:\nEducation: 2500\nEntertainment 2968\nFinance: 3964\nHealth 3055\nTech: 2144",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Text: {test_case['text']}")
        
        extracted = agent._extract_counts_from_llm_result(test_case['text'], 'Category')
        if extracted:
            extracted_dict = dict(zip(extracted['labels'], extracted['values']))
            print(f"   ✅ Extracted: {extracted_dict}")
            
            if extracted_dict == test_case['expected']:
                print(f"   🎉 Perfect match!")
            else:
                print(f"   ⚠️ Partial match")
        else:
            print(f"   ❌ Extraction failed")

if __name__ == "__main__":
    test_pie_chart_extraction()
    test_different_llm_formats()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 50)
    print("The fix should now extract real counts from LLM results")
    print("and use them in pie charts instead of row counts.")
    print("\nTo test with real data:")
    print("1. Start the backend server")
    print("2. Ask: 'create pie chart for category vs no of user in each category'")
    print("3. Check if the pie chart shows [2500, 2968, 3964, 3055, 2144] instead of [8, 6, 6, 6, 4]")
