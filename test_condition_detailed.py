#!/usr/bin/env python3
"""Test condition logic in detail."""

question = 'unique values in Category column'
question_lower = question.lower()

print(f'Question: {question}')
print(f'Lower: {question_lower}')
print()

# Test each part of the condition
print("Testing condition parts:")
print(f"  'unique' in question_lower: {'unique' in question_lower}")
print(f"  'value' in question_lower: {'value' in question_lower}")
print(f"  'values' in question_lower: {'values' in question_lower}")
print(f"  'column' in question_lower: {'column' in question_lower}")
print()

# Test the full condition
condition1 = 'unique' in question_lower and 'value' in question_lower
condition2 = 'unique' in question_lower and 'values' in question_lower
condition3 = 'unique' in question_lower and 'column' in question_lower
full_condition = 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower)

print("Testing conditions:")
print(f"  unique AND value: {condition1}")
print(f"  unique AND values: {condition2}")
print(f"  unique AND column: {condition3}")
print(f"  Full condition: {full_condition}")
print()

# Test the actual condition from the code
actual_condition = 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower)
print(f"Actual condition from code: {actual_condition}")

# Test with different variations
test_questions = [
    'unique value in category columns',
    'unique values in Category column', 
    'what are the unique values in Category?',
    'show me unique values in Category column',
    'list unique values in Category'
]

print("\nTesting all variations:")
for q in test_questions:
    q_lower = q.lower()
    condition = "unique" in q_lower and ("value" in q_lower or "values" in q_lower or "column" in q_lower)
    print(f"'{q}' -> {condition}")
    if condition:
        print(f"  Should match unique values condition")
    else:
        print(f"  Will fall through to else condition")
