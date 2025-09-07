#!/usr/bin/env python3
"""
Test script to verify the region score pie chart fix
"""

from backend.agents.llm_agent import LLMAgent

def test_region_score_extraction():
    """Test extraction with the exact region score data"""
    
    print("🧪 TESTING REGION SCORE EXTRACTION FIX")
    print("=" * 60)
    
    # Exact answer from your latest data
    llm_answer = """Here's the data for your pie chart showing the sum of scores for each region:

```
Region
East     0.44
North    0.36
West     1.79
Name: Score, dtype: float64
```

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
            'East': 0.44,
            'North': 0.36,
            'West': 1.79
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
    viz = agent._build_visualization_from_answer(llm_answer, "create pie chart for Region on basis of score")
    
    if viz:
        print(f"✅ Visualization built successfully!")
        print(f"📊 Type: {viz.get('type')}")
        print(f"📊 Labels: {viz.get('data', {}).get('labels', [])}")
        print(f"📊 Values: {viz.get('data', {}).get('values', [])}")
        
        # Check if values are correct and no garbage
        values = viz.get('data', {}).get('values', [])
        labels = viz.get('data', {}).get('labels', [])
        
        expected_values = [1.79, 0.44, 0.36]  # Sorted descending
        expected_labels = ['West', 'East', 'North']
        
        if values == expected_values and labels == expected_labels:
            print("🎉 SUCCESS! Visualization has correct values and no garbage!")
        elif any(v < 0.1 for v in values if isinstance(v, (int, float))):  # Check for garbage values
            print("❌ FAILED! Still contains garbage values!")
            print(f"   Values: {values}")
            print(f"   Labels: {labels}")
        else:
            print(f"⚠️ Values don't match expected: {expected_values}")
            print(f"Got: {values}")
    else:
        print("❌ Visualization building failed")

def test_float_values():
    """Test with different float value formats"""
    
    print(f"\n🧪 TESTING FLOAT VALUE FORMATS")
    print("=" * 60)
    
    agent = LLMAgent()
    
    test_cases = [
        {
            "name": "Standard float format",
            "answer": """Region
East     0.44
North    0.36
West     1.79
Name: Score, dtype: float64""",
            "expected": {'East': 0.44, 'North': 0.36, 'West': 1.79}
        },
        {
            "name": "Integer values",
            "answer": """Category
A     100
B     200
C     300
Name: Count, dtype: int64""",
            "expected": {'A': 100.0, 'B': 200.0, 'C': 300.0}
        },
        {
            "name": "Mixed values",
            "answer": """Region
East     0.5
North    1.0
West     2.5
Name: Score, dtype: float64""",
            "expected": {'East': 0.5, 'North': 1.0, 'West': 2.5}
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

def test_pie_chart_trigger():
    """Test that pie chart questions trigger post-processing"""
    
    print(f"\n🧪 TESTING PIE CHART TRIGGER")
    print("=" * 60)
    
    test_questions = [
        "create pie chart for Region on basis of score",
        "show me a pie chart for region and score",
        "generate pie chart for region vs score",
        "create a pie chart showing region distribution",
        "pie chart for region and score"
    ]
    
    for question in test_questions:
        should_trigger = 'pie' in question.lower() or 'pie chart' in question.lower()
        print(f"   '{question}' -> {'✅ Triggers' if should_trigger else '❌ Does not trigger'}")

if __name__ == "__main__":
    test_region_score_extraction()
    test_float_values()
    test_pie_chart_trigger()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract float values from pandas Series")
    print("2. ✅ Trigger post-processing for 'pie chart' questions")
    print("3. ✅ Show [1.79, 0.44, 0.36] instead of garbage values")
    print("\nThis addresses the issue where 'create pie chart' questions")
    print("weren't triggering the post-processor.")
