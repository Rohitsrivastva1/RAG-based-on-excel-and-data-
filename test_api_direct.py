#!/usr/bin/env python3
"""Test API processing directly."""

import sys
sys.path.append('backend')

import pandas as pd
from datetime import datetime

# Simulate the simple processing function
def test_simple_processing(question, df):
    """Test the simple processing logic directly."""
    
    start_time = datetime.utcnow()
    
    # Simple rule-based processing
    question_lower = question.lower()
    print(f"Processing question with simple logic: '{question}' -> '{question_lower}'")
    print(f"Checking conditions: unique={('unique' in question_lower)}, value={('value' in question_lower)}, values={('values' in question_lower)}, column={('column' in question_lower)}")
    
    if 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower):
        print("✅ Matched unique values query")
        # Handle unique values query
        if 'category' in question_lower or 'categor' in question_lower:
            print("✅ Matched category column query")
            if 'Category' in df.columns:
                unique_values = df['Category'].unique().tolist()
                answer = f"Unique values in Category column: {', '.join(map(str, unique_values))}"
                print(f"✅ Found unique values: {unique_values}")
            else:
                answer = "Category column not found in dataset"
                print("❌ Category column not found")
        else:
            print("Looking for mentioned column")
            # Find the column mentioned in the question
            mentioned_col = None
            for col in df.columns:
                if col.lower() in question_lower:
                    mentioned_col = col
                    break
            
            if mentioned_col:
                unique_values = df[mentioned_col].unique().tolist()
                answer = f"Unique values in {mentioned_col} column: {', '.join(map(str, unique_values))}"
                print(f"✅ Found unique values for {mentioned_col}: {unique_values}")
            else:
                answer = "Please specify which column you want unique values for"
                print("❌ No column mentioned in question")
        query_type = "pandas"
    elif 'columns' in question_lower and 'unique' not in question_lower:
        print("✅ Matched columns query")
        answer = f"The dataset has {len(df.columns)} columns: {', '.join(df.columns.tolist())}"
        query_type = "pandas"
    elif 'first' in question_lower and 'row' in question_lower:
        print("✅ Matched first rows query")
        n_rows = 5 if '5' in question_lower else 3
        answer = f"First {n_rows} rows:\n{df.head(n_rows).to_string()}"
        query_type = "pandas"
    elif 'total' in question_lower or 'sum' in question_lower:
        print("✅ Matched total/sum query")
        import numpy as np
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            total = df[col].sum()
            answer = f"Total {col}: {total:,.2f}"
        else:
            answer = "No numeric columns found for calculation"
        query_type = "pandas"
    else:
        print("❌ No condition matched, using default summary")
        answer = f"Dataset summary: {len(df)} rows, {len(df.columns)} columns. "
        answer += f"Columns: {', '.join(df.columns.tolist())}"
        query_type = "pandas"
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        'question': question,
        'answer': answer,
        'query_type': query_type,
        'duration_ms': duration * 1000
    }

# Test data
df = pd.DataFrame({
    'Category': ['Education', 'Entertainment', 'Finance'],
    'Revenue': [1000, 1500, 1200],
    'Users': [100, 150, 120]
})

print("Testing simple processing directly:")
print("=" * 50)

test_questions = [
    'unique value in category columns',
    'unique values in Category column', 
    'what are the unique values in Category?',
    'show me unique values in Category column',
    'list unique values in Category'
]

for question in test_questions:
    print(f"\n📝 Testing: {question}")
    result = test_simple_processing(question, df)
    print(f"   Result: {result['answer']}")
    print(f"   Type: {result['query_type']}")
    print()
