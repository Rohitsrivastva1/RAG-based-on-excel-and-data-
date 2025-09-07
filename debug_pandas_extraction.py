#!/usr/bin/env python3
"""
Debug script to understand why pandas series extraction is failing
"""

from backend.agents.llm_agent import LLMAgent

def debug_pandas_extraction():
    """Debug the pandas series extraction"""
    
    print("🔍 DEBUGGING PANDAS SERIES EXTRACTION")
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
    print(repr(llm_answer))
    print()
    
    # Test the extraction with debug
    agent = LLMAgent()
    
    # Debug the extraction step by step
    print("🔍 Debugging extraction step by step...")
    
    lines = llm_answer.split('\n')
    print(f"📊 Total lines: {len(lines)}")
    
    result = {}
    in_series = False
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        print(f"Line {i}: '{line_stripped}'")
        
        # Check if we're starting a pandas series
        if 'Region' in line and 'East' in llm_answer:
            print(f"  -> Starting pandas series detection")
            in_series = True
            continue
        
        # Skip empty lines and metadata
        if not line_stripped or 'Name:' in line or 'dtype:' in line:
            print(f"  -> Skipping (empty or metadata)")
            continue
        
        # Extract category and value pairs
        if in_series:
            print(f"  -> Processing series line")
            # Pattern: "CategoryName    Value" or "CategoryName         Value" (supports floats)
            import re
            match = re.match(r'^([A-Za-z]+)\s+([\d.]+)$', line_stripped)
            if match:
                category = match.group(1)
                try:
                    value = float(match.group(2))
                    result[category] = value
                    print(f"  -> Extracted: {category} = {value}")
                except ValueError as e:
                    print(f"  -> ValueError: {e}")
                    continue
            else:
                print(f"  -> No regex match, trying flexible pattern")
                # Try more flexible pattern
                parts = line_stripped.split()
                print(f"  -> Parts: {parts}")
                if len(parts) >= 2:
                    try:
                        category = parts[0]
                        value = float(parts[-1])  # Last part should be the number
                        result[category] = value
                        print(f"  -> Extracted (flexible): {category} = {value}")
                    except (ValueError, IndexError) as e:
                        print(f"  -> Error: {e}")
                        continue
                else:
                    print(f"  -> Not enough parts")
    
    print(f"\n📊 Final result: {result}")
    print(f"📊 Result length: {len(result)}")
    
    # Test the actual method
    print(f"\n🧪 Testing actual method...")
    pandas_data = agent._extract_pandas_series_from_answer(llm_answer)
    print(f"📊 Method result: {pandas_data}")

if __name__ == "__main__":
    debug_pandas_extraction()
