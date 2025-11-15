import sqlite3

# Check if history is being saved
conn = sqlite3.connect('gemini_demo.db')

# Count total records
cursor = conn.execute('SELECT COUNT(*) FROM generations')
count = cursor.fetchone()[0]
print(f'Total records in history: {count}')

# Show sample records
if count > 0:
    cursor = conn.execute('SELECT id, timestamp, prompt, response FROM generations ORDER BY id DESC LIMIT 5')
    print('\n=== Recent History Records ===')
    for row in cursor.fetchall():
        print(f'\nID: {row[0]}')
        print(f'Time: {row[1]}')
        print(f'Prompt: {row[2][:80]}...')
        print(f'Response: {row[3][:80]}...')
else:
    print('\n⚠️ No records found in history database!')

# Test the search function
print('\n=== Testing Search Function ===')
query = "discuss"
cursor = conn.execute('''
    SELECT timestamp, prompt, response 
    FROM generations 
    WHERE LOWER(prompt) LIKE ? OR LOWER(response) LIKE ?
    ORDER BY timestamp DESC
    LIMIT 3
''', (f'%{query.lower()}%', f'%{query.lower()}%'))

results = cursor.fetchall()
print(f'Search for "{query}" found {len(results)} results')

conn.close()
