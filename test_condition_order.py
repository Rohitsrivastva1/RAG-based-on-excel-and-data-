#!/usr/bin/env python3
"""Test condition ordering."""

question = 'unique value in category columns'
question_lower = question.lower()

print(f'Question: {question}')
print(f'Lower: {question_lower}')
print()

print("Testing condition order:")
print(f"1. unique in question_lower: {'unique' in question_lower}")
print(f"2. columns in question_lower: {'columns' in question_lower}")
print(f"3. unique condition: {'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower)}")
print(f"4. columns condition: {'columns' in question_lower and 'unique' not in question_lower}")
print()

print("Which condition should match:")
if 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower):
    print("✅ Should match UNIQUE VALUES condition")
elif 'columns' in question_lower and 'unique' not in question_lower:
    print("✅ Should match COLUMNS condition")
else:
    print("✅ Should match DEFAULT condition")

print()
print("Actual condition results:")
condition1 = 'unique' in question_lower and ('value' in question_lower or 'values' in question_lower or 'column' in question_lower)
condition2 = 'columns' in question_lower and 'unique' not in question_lower

print(f"Unique values condition: {condition1}")
print(f"Columns condition: {condition2}")

if condition1:
    print("✅ UNIQUE VALUES condition matches first")
elif condition2:
    print("❌ COLUMNS condition matches (but shouldn't)")
else:
    print("❌ No condition matches")
