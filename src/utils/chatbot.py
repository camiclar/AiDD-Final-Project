"""Chatbot utility functions for the Campus Resource Hub admin dashboard."""
from flask import current_app
from src.database import db
from sqlalchemy import text


def get_database_schema():
    """Return a description of the database schema for the AI."""
    return """
Campus Resource Hub Database Schema:

Table: users
- id (INTEGER, PRIMARY KEY)
- email (TEXT, UNIQUE)
- name (TEXT)
- role (TEXT) - values: 'student', 'staff', 'admin'
- department (TEXT, nullable)
- profile_image (TEXT, nullable)
- created_at (DATETIME)

Table: resources
- id (INTEGER, PRIMARY KEY)
- title (TEXT)
- description (TEXT)
- category (TEXT) - values: 'study-room', 'lab-equipment', 'event-space', 'av-equipment', 'tutoring', 'other'
- location (TEXT)
- capacity (INTEGER)
- status (TEXT) - values: 'draft', 'published', 'archived'
- owner_id (INTEGER, FOREIGN KEY to users.id)
- availability_rules (TEXT, nullable)
- requires_approval (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)

Table: bookings
- id (INTEGER, PRIMARY KEY)
- resource_id (INTEGER, FOREIGN KEY to resources.id)
- user_id (INTEGER, FOREIGN KEY to users.id)
- start_time (DATETIME)
- end_time (DATETIME)
- status (TEXT) - values: 'pending', 'approved', 'rejected', 'completed', 'cancelled'
- notes (TEXT, nullable)
- recurrence (TEXT, nullable) - values: 'none', 'daily', 'weekly'
- created_at (DATETIME)
- updated_at (DATETIME)

Table: reviews
- id (INTEGER, PRIMARY KEY)
- resource_id (INTEGER, FOREIGN KEY to resources.id)
- user_id (INTEGER, FOREIGN KEY to users.id)
- rating (INTEGER) - values: 1-5
- comment (TEXT)
- created_at (DATETIME)
- UNIQUE constraint on (resource_id, user_id)

Sample questions you can help with:
- What time of day do most resources get booked for?
- Which resources are the most popular?
- How many bookings were made this month?
- What is the average rating for resources in each category?
- Which users have the most bookings?
- What is the booking approval rate?
- Show me resources with low ratings
- What are the busiest days of the week for bookings?
- How many resources are in each category?
- What is the average booking duration?
"""


def execute_safe_query(sql_query):
    """
    Execute a SELECT query safely and return results.
    Only allows SELECT statements for safety.
    """
    # Clean up the SQL query
    sql_query = sql_query.strip()
    
    # Remove SQL comments (-- style and /* */ style)
    lines = []
    in_block_comment = False
    for line in sql_query.split('\n'):
        # Handle block comments
        while '/*' in line or '*/' in line:
            if '/*' in line and '*/' in line:
                # Comment on same line
                start = line.find('/*')
                end = line.find('*/') + 2
                line = line[:start] + ' ' + line[end:]
            elif '/*' in line:
                in_block_comment = True
                line = line[:line.find('/*')]
            elif '*/' in line:
                in_block_comment = False
                line = line[line.find('*/') + 2:]
        
        if not in_block_comment:
            # Remove -- style comments
            if '--' in line:
                line = line[:line.find('--')]
            lines.append(line)
    
    sql_query = ' '.join(lines)
    
    # Normalize whitespace
    import re
    sql_query = re.sub(r'\s+', ' ', sql_query).strip()
    
    # Convert to uppercase for checking (but keep original for execution)
    sql_upper = sql_query.upper().strip()
    
    # Check if it's a SELECT query (allowing WITH clauses for CTEs)
    # CTEs start with WITH but contain SELECT, so we need to check for both
    is_select = sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')
    
    if not is_select:
        return {"error": f"Only SELECT queries are allowed for safety reasons. Query starts with: {sql_query[:50]}..."}
    
    # Additional safety - block dangerous keywords (but allow them in string literals would be ideal, 
    # for now we do a simple check)
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
    sql_upper_for_check = sql_upper
    # Remove string literals to avoid false positives (simple approach)
    sql_upper_for_check = re.sub(r"'[^']*'", "''", sql_upper_for_check)
    sql_upper_for_check = re.sub(r'"[^"]*"', '""', sql_upper_for_check)
    
    if any(keyword in sql_upper_for_check for keyword in dangerous_keywords):
        return {"error": "Query contains potentially dangerous operations."}
    
    try:
        # Use SQLAlchemy's text() for safe query execution
        result = db.session.execute(text(sql_query))
        rows = result.fetchall()
        
        # Convert rows to dictionaries
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in rows]
        
        return {"success": True, "data": data, "row_count": len(data)}
    except Exception as e:
        return {"error": str(e)}

