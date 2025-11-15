import os
import sqlite3
from datetime import datetime
from google import genai
from flask import Flask, render_template, request
from markupsafe import Markup
import markdown


# Put your key here temporarily for the demo, or set GEMINI_API_KEY in your .env
HARDCODE_API_KEY = "AIzaSyBW1P_XBFzEdTffzGhR5uPYC-7b1tqkSFM"


# A short list of candidate models for the selector. Update these as needed.
# NOTE: I can't query the remote API from this environment, so adjust this list
# to match the latest available free models for your account.
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.1",
    "gemini-1.5",
    "gemini-ultra-1.0",
]

# Default model
MODEL = MODELS[0]


app = Flask(__name__)


# Simple SQLite database setup
DB_FILE = "gemini_demo.db"

def init_db():
    """Create the database tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    
    # Conversation history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL
        )
    ''')
    
    # Business tables with sample data
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            city TEXT,
            join_date TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # Check if business tables are empty and insert sample data
    cursor = conn.execute('SELECT COUNT(*) FROM customers')
    if cursor.fetchone()[0] == 0:
        # Insert sample customers
        conn.executemany('''
            INSERT INTO customers (name, email, phone, city, join_date)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('John Smith', 'john.smith@email.com', '555-0101', 'New York', '2024-01-15'),
            ('Sarah Johnson', 'sarah.j@email.com', '555-0102', 'Los Angeles', '2024-02-20'),
            ('Mike Chen', 'mike.chen@email.com', '555-0103', 'Chicago', '2024-03-10'),
            ('Emily Davis', 'emily.d@email.com', '555-0104', 'Houston', '2024-04-05'),
            ('Robert Wilson', 'r.wilson@email.com', '555-0105', 'Phoenix', '2024-05-12'),
            ('Lisa Anderson', 'lisa.a@email.com', '555-0106', 'Philadelphia', '2024-06-18'),
            ('David Brown', 'david.b@email.com', '555-0107', 'San Antonio', '2024-07-22'),
            ('Jessica Martinez', 'jessica.m@email.com', '555-0108', 'San Diego', '2024-08-30'),
        ])
        
        # Insert sample products
        conn.executemany('''
            INSERT INTO products (product_name, category, price, stock_quantity)
            VALUES (?, ?, ?, ?)
        ''', [
            ('Laptop Pro 15', 'Electronics', 1299.99, 45),
            ('Wireless Mouse', 'Electronics', 29.99, 150),
            ('Office Chair Deluxe', 'Furniture', 349.99, 30),
            ('Standing Desk', 'Furniture', 599.99, 20),
            ('USB-C Hub', 'Electronics', 49.99, 200),
            ('Desk Lamp LED', 'Furniture', 39.99, 80),
            ('Mechanical Keyboard', 'Electronics', 129.99, 60),
            ('Monitor 27-inch', 'Electronics', 399.99, 35),
            ('Ergonomic Footrest', 'Furniture', 49.99, 100),
            ('Webcam HD', 'Electronics', 89.99, 75),
        ])
        
        # Insert sample orders
        conn.executemany('''
            INSERT INTO orders (customer_id, product_id, quantity, order_date, total_amount)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 1, 1, '2024-09-01', 1299.99),
            (1, 2, 2, '2024-09-01', 59.98),
            (2, 3, 1, '2024-09-05', 349.99),
            (3, 1, 1, '2024-09-10', 1299.99),
            (3, 7, 1, '2024-09-10', 129.99),
            (4, 8, 2, '2024-09-15', 799.98),
            (5, 4, 1, '2024-09-18', 599.99),
            (6, 2, 3, '2024-09-20', 89.97),
            (6, 5, 2, '2024-09-20', 99.98),
            (7, 6, 2, '2024-09-25', 79.98),
            (8, 10, 1, '2024-09-28', 89.99),
            (1, 5, 1, '2024-10-01', 49.99),
            (2, 7, 1, '2024-10-05', 129.99),
            (4, 9, 1, '2024-10-10', 49.99),
            (5, 3, 1, '2024-10-12', 349.99),
        ])
    
    conn.commit()
    conn.close()

def save_generation(model, prompt, response):
    """Save a successful generation to the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        'INSERT INTO generations (timestamp, model, prompt, response) VALUES (?, ?, ?, ?)',
        (datetime.utcnow().isoformat(), model, prompt, response)
    )
    conn.commit()
    conn.close()

def search_history(query, limit=3):
    """
    Search the database for relevant past conversations (simple keyword search).
    This is a basic RAG implementation - searches prompts and responses for matching keywords.
    Returns up to 'limit' relevant past conversations.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    
    # Check if this is a general "history" or "discussion" query
    general_history_keywords = ['history', 'discuss', 'conversation', 'talked about', 'previous', 'before', 'earlier']
    is_general_query = any(keyword in query.lower() for keyword in general_history_keywords)
    
    if is_general_query:
        # For general queries, return the most recent conversations
        cursor = conn.execute('''
            SELECT timestamp, model, prompt, response 
            FROM generations 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
    else:
        # For specific queries, search for matching keywords
        # For production, you'd want vector embeddings, but this demonstrates the concept
        cursor = conn.execute('''
            SELECT timestamp, model, prompt, response 
            FROM generations 
            WHERE LOWER(prompt) LIKE ? OR LOWER(response) LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query.lower()}%', f'%{query.lower()}%', limit))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_business_schema():
    """Return a description of the business database schema for the AI."""
    return """
Business Database Schema:

Table: customers
- customer_id (INTEGER, PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- phone (TEXT)
- city (TEXT)
- join_date (TEXT, format: YYYY-MM-DD)

Table: products
- product_id (INTEGER, PRIMARY KEY)
- product_name (TEXT)
- category (TEXT) - values: 'Electronics' or 'Furniture'
- price (REAL)
- stock_quantity (INTEGER)

Table: orders
- order_id (INTEGER, PRIMARY KEY)
- customer_id (INTEGER, FOREIGN KEY to customers)
- product_id (INTEGER, FOREIGN KEY to products)
- quantity (INTEGER)
- order_date (TEXT, format: YYYY-MM-DD)
- total_amount (REAL)

Sample queries you can help with:
- Show all customers from a specific city
- List products by category or price range
- Calculate total sales or revenue
- Find top customers by purchase amount
- Show order history for a customer
- Check product stock levels
"""

def execute_safe_query(sql_query):
    """
    Execute a SELECT query safely and return results.
    Only allows SELECT statements for safety.
    """
    sql_query = sql_query.strip()
    
    # Safety check - only allow SELECT queries
    if not sql_query.upper().startswith('SELECT'):
        return {"error": "Only SELECT queries are allowed for safety reasons."}
    
    # Additional safety - block dangerous keywords
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
        return {"error": "Query contains potentially dangerous operations."}
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql_query)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"success": True, "data": results, "row_count": len(results)}
    except Exception as e:
        return {"error": str(e)}

# Initialize database on startup
init_db()

# Create the client at startup. If it fails, client will be None and we show a friendly message.
client = None
init_error = None
api_key = HARDCODE_API_KEY
client = genai.Client(api_key=api_key)




@app.route('/history')
def history():
    """Show all past generations from the database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.execute('SELECT * FROM generations ORDER BY id DESC')
    records = cursor.fetchall()
    conn.close()
    return render_template('history.html', records=records)


@app.route('/', methods=['GET', 'POST'])
def index():
    user_prompt = ""
    result_text = None
    error = None

    # Defaults for rendering the form
    selected_model = MODEL
    form_api_key = os.environ.get('GEMINI_API_KEY', '') or ''
    use_rag = False
    rag_context = ""
    use_business_data = False
    business_query_result = ""

    if request.method == 'POST':
        user_prompt = request.form.get('prompt', '').strip()
        # The API key provided by the user in the form (if any)
        form_api_key = request.form.get('api_key', '').strip() or form_api_key
        # Model selected by the user
        selected_model = request.form.get('model', '') or selected_model
        # Check if RAG (search history) is enabled
        use_rag = request.form.get('use_rag') == 'on'
        # Check if business data query is enabled
        use_business_data = request.form.get('use_business_data') == 'on'

        if not user_prompt:
            error = "Please enter a prompt."
        else:
            try:
                enhanced_prompt = user_prompt
                
                # Business Data Query Mode: AI generates SQL and we execute it
                if use_business_data:
                    schema_info = get_business_schema()
                    sql_prompt = f"""{schema_info}

User Question: {user_prompt}

Please generate a SQL SELECT query to answer this question. Return ONLY the SQL query, nothing else.
Make sure the query is safe (SELECT only) and follows SQLite syntax."""
                    
                    # First API call: Generate SQL query
                    local_client = genai.Client(api_key=form_api_key or api_key)
                    sql_response = local_client.models.generate_content(model=selected_model, contents=sql_prompt)
                    generated_sql = sql_response.text.strip()
                    
                    # Clean up the SQL (remove markdown code blocks if present)
                    if '```sql' in generated_sql:
                        generated_sql = generated_sql.split('```sql')[1].split('```')[0].strip()
                    elif '```' in generated_sql:
                        generated_sql = generated_sql.split('```')[1].split('```')[0].strip()
                    
                    # Execute the query
                    query_result = execute_safe_query(generated_sql)
                    
                    if 'error' in query_result:
                        business_query_result = f"SQL Query:\n{generated_sql}\n\nError: {query_result['error']}"
                        error = f"Database query error: {query_result['error']}"
                    else:
                        # Second API call: Summarize results in natural language
                        result_data = query_result['data']
                        business_query_result = f"Generated SQL:\n{generated_sql}\n\nQuery returned {query_result['row_count']} rows."
                        
                        summary_prompt = f"""User asked: {user_prompt}

I executed this SQL query:
{generated_sql}

Results ({query_result['row_count']} rows):
{result_data}

Please provide a clear, natural language answer to the user's question based on these results."""
                        
                        summary_response = local_client.models.generate_content(model=selected_model, contents=summary_prompt)
                        result_text = summary_response.text
                        
                        # Save to history
                        save_generation(selected_model, user_prompt, result_text)
                
                # RAG Implementation: If enabled, search the database for relevant context
                elif use_rag:
                    history_results = search_history(user_prompt, limit=3)
                    if history_results:
                        # Build context from past conversations (plain text for AI)
                        context_parts_ai = ["Here is relevant context from past conversations:\n"]
                        for idx, record in enumerate(history_results, 1):
                            context_parts_ai.append(f"\n--- Past Conversation {idx} ({record['timestamp']}) ---")
                            context_parts_ai.append(f"Previous Prompt: {record['prompt']}")
                            context_parts_ai.append(f"Previous Response: {record['response']}")
                        
                        context_for_ai = "\n".join(context_parts_ai)
                        
                        # Build formatted HTML context for display
                        context_html = ["<p><strong>Retrieved " + str(len(history_results)) + " relevant conversation(s):</strong></p>"]
                        for idx, record in enumerate(history_results, 1):
                            context_html.append(f'<div style="background: #fff; border-left: 3px solid #0066cc; padding: 0.8rem; margin: 0.8rem 0; border-radius: 4px;">')
                            context_html.append(f'<div style="color: #666; font-size: 0.85rem; margin-bottom: 0.5rem;">📅 {record["timestamp"]}</div>')
                            context_html.append(f'<div style="margin-bottom: 0.5rem;"><strong>Prompt:</strong> {record["prompt"][:150]}{"..." if len(record["prompt"]) > 150 else ""}</div>')
                            context_html.append(f'<div><strong>Response:</strong> {record["response"][:150]}{"..." if len(record["response"]) > 150 else ""}</div>')
                            context_html.append('</div>')
                        
                        rag_context = "".join(context_html)
                        # Prepend context to the user's prompt
                        enhanced_prompt = f"{context_for_ai}\n\n--- Current Question ---\n{user_prompt}"
                    
                    local_client = genai.Client(api_key=form_api_key or api_key)
                    resp = local_client.models.generate_content(model=selected_model, contents=enhanced_prompt)
                    result_text = resp.text
                    save_generation(selected_model, user_prompt, result_text)
                
                # Standard mode: Just send the prompt
                else:
                    local_client = genai.Client(api_key=form_api_key or api_key)
                    resp = local_client.models.generate_content(model=selected_model, contents=user_prompt)
                    result_text = resp.text
                    save_generation(selected_model, user_prompt, result_text)
                    
            except Exception as e:
                # Keep the message short for students; print full exception to console.
                print("Generation error:", e)
                error = f"API error: {e}"

    # Convert markdown to HTML for better formatting
    if result_text:
        result_html = Markup(markdown.markdown(result_text, extensions=['fenced_code', 'tables', 'nl2br']))
    else:
        result_html = None
    
    return render_template('index.html', prompt=user_prompt, result=result_html, error=error, model=selected_model, models=MODELS, api_key=form_api_key, init_error=init_error, use_rag=use_rag, rag_context=rag_context, use_business_data=use_business_data, business_query_result=business_query_result)




if __name__ == '__main__':
    # For classroom demos it's convenient to enable debug mode.
    app.run(debug=True, port=int(os.getenv('PORT', '5001')))