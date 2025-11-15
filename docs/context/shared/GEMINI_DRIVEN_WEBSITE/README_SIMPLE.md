Simple Gemini Classroom Demo
=============================

This folder includes a tiny, easy-to-read Flask app for teaching students how to call the Gemini API.

Files:
- `app.py` - Minimal Flask app. Edit `HARDCODE_API_KEY` to paste a temporary API key for classroom testing (do not commit).
- `templates/index.html` - Minimal HTML form and result display.

How to run (Windows PowerShell, with your virtualenv activated):

1. Activate your venv if not already active:

   .\.venv\Scripts\Activate.ps1

2. Start the simple app:

   .\.venv\Scripts\python.exe simple_app.py

Security note:
- This simplified app is intentionally explicit and contains a placeholder for a hard-coded key. Never commit real API keys to a public repo. Use environment variables or secrets managers for production.
