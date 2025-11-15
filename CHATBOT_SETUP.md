# AI Chatbot Setup Guide

The Campus Resource Hub includes an AI-powered analytics assistant on the admin dashboard that allows admins to ask questions about resource usage, bookings, and analytics in natural language.

## Setup Instructions

### 1. Get a Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure the API Key

Create a `.env` file in the root directory of the project (same level as `app.py`) with the following content:

```
GEMINI_API_KEY=your-api-key-here
```

**Important:** The `.env` file is already in `.gitignore`, so your API key will NOT be committed to GitHub.

### 3. Install Dependencies

Make sure you have installed all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `google-genai` - Google Gemini API client
- `python-dotenv` - For loading environment variables from `.env` file
- `Markdown` - For formatting AI responses

## Usage

1. Log in as an admin user
2. Navigate to the Admin Panel
3. Scroll down to the "AI Analytics Assistant" section
4. Click to expand the chatbot
5. Ask questions like:
   - "What time of day do most resources get booked for?"
   - "Which resources are the most popular?"
   - "How many bookings were made this month?"
   - "What is the average rating for resources in each category?"
   - "Which users have the most bookings?"

The chatbot will:
1. Generate a SQL query based on your question
2. Execute the query safely (SELECT only)
3. Summarize the results in natural language

## Security

- Only SELECT queries are allowed (no INSERT, UPDATE, DELETE, etc.)
- The API key is stored securely in environment variables
- The `.env` file is excluded from version control

