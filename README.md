# Campus Resource Hub

A full-stack web application that enables university departments, student organizations, and individuals to list, share, and reserve campus resources.

## Features

- Search & booking with calendar integration
- Role-based access control (Student, Staff, Admin)
- Ratings, reviews, and messaging between users
- Administrative workflows for approvals, moderation, and analytics

## Tech Stack

- **Backend**: Flask (Python 3.10+)
- **Frontend**: Jinja2 templates + Bootstrap 5
- **Database**: SQLite (local) with optional PostgreSQL for deployment
- **Authentication**: Flask-Login with bcrypt password hashing

## Project Structure

```
.
├── src/
│   ├── models/          # Database models
│   ├── views/           # Controllers/routes
│   └── database.py      # Database configuration
├── templates/           # Jinja2 templates
├── static/              # CSS, JS, images
├── instance/            # Database files
├── tests/               # Unit/integration tests
├── docs/                # Project documentation
└── app.py               # Main Flask application
```

## Setup Instructions

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Database

The database is located at `instance/campus_resource_hub.db` and is included in the repository for this school project. The database will be automatically created with all tables on first run of the application.

## Development Notes

This project follows MVC architecture:
- **Models**: Database models in `src/models/`
- **Views**: Controllers/routes in `src/views/`
- **Templates**: Jinja2 templates in `templates/`

