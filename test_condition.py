#!/usr/bin/env python3
"""Test condition logic."""

question = 'unique values in Category column'
question_lower = question.lower()

print(f'Question: {question}')
print(f'Lower: {question_lower}')
print(f'unique: {"unique" in question_lower}')
print(f'value: {"value" in question_lower}')
print(f'values: {"values" in question_lower}')
print(f'column: {"column" in question_lower}')
print(f'Condition: {"unique" in question_lower and ("value" in question_lower or "values" in question_lower or "column" in question_lower)}')

# Test other variations
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
