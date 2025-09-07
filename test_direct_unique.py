#!/usr/bin/env python3
"""Test unique values logic directly."""

import pandas as pd

# Create test data
df = pd.DataFrame({
    'Category': ['Education', 'Entertainment', 'Finance', 'Health', 'Tech', 'Education', 'Entertainment', 'Finance'],
    'Revenue': [1000, 1500, 1200, 800, 2000, 1100, 1600, 1300],
    'Users': [100, 150, 120, 80, 200, 110, 160, 130],
    'Growth_%': [5.2, 8.1, 3.4, 2.1, 12.5, 6.3, 9.2, 4.7]
})

def test_unique_values_logic(question, df):
    """Test the unique values logic directly."""
    question_lower = question.lower()
    print(f"Testing: '{question}' -> '{question_lower}'")
    
    if 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower):
        print("  Matched unique values query")
        if 'category' in question_lower or 'categor' in question_lower:
            print("  Matched category column query")
            if 'Category' in df.columns:
                unique_values = df['Category'].unique().tolist()
                answer = f"Unique values in Category column: {', '.join(map(str, unique_values))}"
                print(f"  Answer: {answer}")
                return answer
            else:
                answer = "Category column not found in dataset"
                print(f"  Answer: {answer}")
                return answer
        else:
            print("  Looking for mentioned column")
            mentioned_col = None
            for col in df.columns:
                if col.lower() in question_lower:
                    mentioned_col = col
                    break
            
            if mentioned_col:
                unique_values = df[mentioned_col].unique().tolist()
                answer = f"Unique values in {mentioned_col} column: {', '.join(map(str, unique_values))}"
                print(f"  Answer: {answer}")
                return answer
            else:
                answer = "Please specify which column you want unique values for"
                print(f"  Answer: {answer}")
                return answer
    else:
        print("  Did not match unique values condition")
        return None

# Test all variations
test_questions = [
    'unique value in category columns',
    'unique values in Category column', 
    'what are the unique values in Category?',
    'show me unique values in Category column',
    'list unique values in Category'
]

print("Testing unique values logic directly:")
print("=" * 50)

for question in test_questions:
    result = test_unique_values_logic(question, df)
    print(f"Result: {result}")
    print()
