#!/usr/bin/env python3
"""
Test script to verify the pandas Series extraction fix
"""

from backend.agents.llm_agent import LLMAgent

def test_pandas_series_extraction():
    """Test extraction with the exact pandas Series format from your data"""
    
    print("🧪 TESTING PANDAS SERIES EXTRACTION FIX")
    print("=" * 60)
    
    # Exact answer from your latest data
    llm_answer = """Here's the data for your pie chart showing the number of users per category:

```
Category
Education        2500
Entertainment    2968
Finance          3964
Health           3055
Tech             2144
Name: Users, dtype: int64
```

This data represents the sum of users for each category.  You can use this data with a plotting library like matplotlib or seaborn to create your pie chart.

I am here to help you with any other questions about your data!"""
    
    print("📝 LLM Answer:")
    print(llm_answer)
    print()
    
    # Test the extraction
    agent = LLMAgent()
    
    # Test pandas series extraction
    print("🔍 Testing pandas series extraction...")
    pandas_data = agent._extract_pandas_series_from_answer(llm_answer)
    
    if pandas_data:
        print(f"✅ Pandas series extracted successfully!")
        print(f"📊 Extracted data: {pandas_data}")
        
        # Check if it matches expected
        expected = {
            'Education': 2500,
            'Entertainment': 2968,
            'Finance': 3964,
            'Health': 3055,
            'Tech': 2144
        }
        
        if pandas_data == expected:
            print("🎉 PERFECT MATCH! Pandas series extraction works correctly")
        else:
            print("⚠️ Partial match - some values may be different")
            print(f"Expected: {expected}")
            print(f"Got: {pandas_data}")
    else:
        print("❌ Pandas series extraction failed")
    
    # Test full visualization building
    print(f"\n🧪 Testing full visualization building...")
    viz = agent._build_visualization_from_answer(llm_answer, "create pie chart for category vs no of user in each category")
    
    if viz:
        print(f"✅ Visualization built successfully!")
        print(f"📊 Type: {viz.get('type')}")
        print(f"📊 Labels: {viz.get('data', {}).get('labels', [])}")
        print(f"📊 Values: {viz.get('data', {}).get('values', [])}")
        
        # Check if values are correct and no garbage
        values = viz.get('data', {}).get('values', [])
        labels = viz.get('data', {}).get('labels', [])
        
        expected_values = [3964, 3055, 2968, 2500, 2144]  # Sorted descending
        expected_labels = ['Finance', 'Health', 'Entertainment', 'Education', 'Tech']
        
        if values == expected_values and labels == expected_labels:
            print("🎉 SUCCESS! Visualization has correct values and no garbage!")
        elif any(v < 100 for v in values):  # Check for garbage values
            print("❌ FAILED! Still contains garbage values!")
            print(f"   Values: {values}")
            print(f"   Labels: {labels}")
        else:
            print(f"⚠️ Values don't match expected: {expected_values}")
            print(f"Got: {values}")
    else:
        print("❌ Visualization building failed")

def test_different_pandas_formats():
    """Test with different pandas Series formats"""
    
    print(f"\n🧪 TESTING DIFFERENT PANDAS SERIES FORMATS")
    print("=" * 60)
    
    agent = LLMAgent()
    
    test_cases = [
        {
            "name": "Standard pandas format",
            "answer": """Category
Education        2500
Entertainment    2968
Finance          3964
Health           3055
Tech             2144
Name: Users, dtype: int64""",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "With extra text",
            "answer": """Here's the data:
Category
Education        2500
Entertainment    2968
Finance          3964
Health           3055
Tech             2144
Name: Users, dtype: int64
Use this for your chart.""",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "In code block",
            "answer": """```
Category
Education        2500
Entertainment    2968
Finance          3964
Health           3055
Tech             2144
Name: Users, dtype: int64
```""",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Answer: {test_case['answer'][:100]}...")
        
        pandas_data = agent._extract_pandas_series_from_answer(test_case['answer'])
        if pandas_data:
            print(f"   ✅ Extracted: {pandas_data}")
            if pandas_data == test_case['expected']:
                print(f"   🎉 Perfect match!")
            else:
                print(f"   ⚠️ Partial match")
        else:
            print(f"   ❌ Extraction failed")

if __name__ == "__main__":
    test_pandas_series_extraction()
    test_different_pandas_formats()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract pandas Series format from LLM answers")
    print("2. ✅ Build clean pie charts with only real data")
    print("3. ✅ Show [3964, 3055, 2968, 2500, 2144] without garbage values")
    print("\nThis addresses the issue where garbage values like [range, statistics, 22, 23, 24]")
    print("were being included alongside the real data.")
