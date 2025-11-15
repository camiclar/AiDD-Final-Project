import sqlite3

# Test what the RAG search finds for "what have we been discussing?"
conn = sqlite3.connect('gemini_demo.db')
conn.row_factory = sqlite3.Row

query = "what have we been discussing?"

print(f'User asked: "{query}"\n')
print('=== Testing RAG Search ===')

# This is what the app does
cursor = conn.execute('''
    SELECT timestamp, model, prompt, response 
    FROM generations 
    WHERE LOWER(prompt) LIKE ? OR LOWER(response) LIKE ?
    ORDER BY timestamp DESC
    LIMIT ?
''', (f'%{query.lower()}%', f'%{query.lower()}%', 3))

results = cursor.fetchall()
print(f'Found {len(results)} results\n')

if results:
    for idx, record in enumerate(results, 1):
        print(f"--- Past Conversation {idx} ({record['timestamp']}) ---")
        print(f"Previous Prompt: {record['prompt'][:100]}")
        print(f"Previous Response: {record['response'][:100]}")
        print()
else:
    print("❌ No matching results found!")
    print("\nLet's see what's actually in the database:")
    cursor = conn.execute('SELECT prompt FROM generations')
    all_prompts = cursor.fetchall()
    print("\nAll prompts in database:")
    for p in all_prompts:
        print(f"  - {p['prompt']}")

conn.close()
