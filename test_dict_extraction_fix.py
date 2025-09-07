#!/usr/bin/env python3
"""
Test script to verify the dictionary extraction fix works with the exact data provided
"""

from backend.agents.llm_agent import LLMAgent

def test_dict_extraction():
    """Test dictionary extraction from the exact LLM answer provided"""
    
    print("🧪 TESTING DICTIONARY EXTRACTION FIX")
    print("=" * 60)
    
    # Exact answer from your data
    llm_answer = """Here's the data suitable for creating a pie chart showing the number of users per category:

```
{'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
```

I am here to help you with any other questions about your data!"""
    
    print("📝 LLM Answer:")
    print(llm_answer)
    print()
    
    # Test the extraction
    agent = LLMAgent()
    
    # Test dictionary extraction
    print("🔍 Testing dictionary extraction...")
    dict_data = agent._extract_dict_from_answer(llm_answer)
    
    if dict_data:
        print(f"✅ Dictionary extracted successfully!")
        print(f"📊 Extracted data: {dict_data}")
        
        # Check if it matches expected
        expected = {
            'Education': 2500,
            'Entertainment': 2968,
            'Finance': 3964,
            'Health': 3055,
            'Tech': 2144
        }
        
        if dict_data == expected:
            print("🎉 PERFECT MATCH! Dictionary extraction works correctly")
        else:
            print("⚠️ Partial match - some values may be different")
            print(f"Expected: {expected}")
            print(f"Got: {dict_data}")
    else:
        print("❌ Dictionary extraction failed")
    
    # Test full visualization building
    print(f"\n🧪 Testing full visualization building...")
    viz = agent._build_visualization_from_answer(llm_answer, "create pie chart for category vs no of user in each category")
    
    if viz:
        print(f"✅ Visualization built successfully!")
        print(f"📊 Type: {viz.get('type')}")
        print(f"📊 Labels: {viz.get('data', {}).get('labels', [])}")
        print(f"📊 Values: {viz.get('data', {}).get('values', [])}")
        
        # Check if values are correct
        values = viz.get('data', {}).get('values', [])
        expected_values = [3964, 3055, 2968, 2500, 2144]  # Sorted descending
        
        if values == expected_values:
            print("🎉 SUCCESS! Visualization has correct values!")
        else:
            print(f"⚠️ Values don't match expected: {expected_values}")
            print(f"Got: {values}")
    else:
        print("❌ Visualization building failed")

def test_different_dict_formats():
    """Test with different dictionary formats"""
    
    print(f"\n🧪 TESTING DIFFERENT DICTIONARY FORMATS")
    print("=" * 60)
    
    agent = LLMAgent()
    
    test_cases = [
        {
            "name": "Single line dict",
            "answer": "Here's the data: {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "Multi-line dict",
            "answer": """Results:
            {
                'Education': 2500,
                'Entertainment': 2968,
                'Finance': 3964,
                'Health': 3055,
                'Tech': 2144
            }""",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "Dict in code block",
            "answer": "```\n{'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}\n```",
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        },
        {
            "name": "Double quotes",
            "answer": 'Data: {"Education": 2500, "Entertainment": 2968, "Finance": 3964, "Health": 3055, "Tech": 2144}',
            "expected": {'Education': 2500, 'Entertainment': 2968, 'Finance': 3964, 'Health': 3055, 'Tech': 2144}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Answer: {test_case['answer'][:100]}...")
        
        dict_data = agent._extract_dict_from_answer(test_case['answer'])
        if dict_data:
            print(f"   ✅ Extracted: {dict_data}")
            if dict_data == test_case['expected']:
                print(f"   🎉 Perfect match!")
            else:
                print(f"   ⚠️ Partial match")
        else:
            print(f"   ❌ Extraction failed")

if __name__ == "__main__":
    test_dict_extraction()
    test_different_dict_formats()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 60)
    print("The fix should now:")
    print("1. ✅ Extract dictionaries from LLM answers")
    print("2. ✅ Build correct pie chart visualizations")
    print("3. ✅ Show [3964, 3055, 2968, 2500, 2144] instead of junk tokens")
    print("\nThis addresses the core issue where visualization was pulling")
    print("random tokens from dataset context instead of using the LLM's dict.")
