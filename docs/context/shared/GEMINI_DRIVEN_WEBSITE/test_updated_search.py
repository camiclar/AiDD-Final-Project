import sys
sys.path.insert(0, '.')
from app import search_history

# Test the updated search_history function
query = "what have we been discussing?"
print(f'Testing query: "{query}"\n')

results = search_history(query, limit=3)
print(f'Found {len(results)} results\n')

if results:
    for idx, record in enumerate(results, 1):
        print(f"--- Past Conversation {idx} ---")
        print(f"Timestamp: {record['timestamp']}")
        print(f"Prompt: {record['prompt'][:100]}")
        print(f"Response: {record['response'][:100]}")
        print()
else:
    print("No results found")
