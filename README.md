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
- **Database**: SQLite
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

### Populating Dummy Data

To populate the database with test data (users, resources, bookings, etc.), run:

```bash
python populate_dummy_data.py
```

This will create:
- 6 users (1 admin, 2 staff, 3 students)
- 6 resources (study rooms, lab equipment, event spaces, etc.)
- 4 bookings
- 4 reviews
- Sample messages

**Test credentials are available in `TEST_CREDENTIALS.md`**

**Note:** Running this script will clear all existing data in the database!

## Testing

The project includes comprehensive tests using pytest. To run the tests:

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Unit tests for booking logic
pytest tests/test_booking_logic.py

# Data access layer tests
pytest tests/test_data_access.py

# Authentication integration tests
pytest tests/test_auth_integration.py

# Security tests
pytest tests/test_security.py

# End-to-end booking tests
pytest tests/test_e2e_booking.py
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Test Structure

- **`tests/test_booking_logic.py`**: Unit tests for booking conflict detection and status transitions
- **`tests/test_data_access.py`**: Unit tests for Data Access Layer (CRUD operations independent of Flask routes)
- **`tests/test_auth_integration.py`**: Integration tests for authentication flow (register → login → access protected route)
- **`tests/test_security.py`**: Security tests for SQL injection protection and template escaping
- **`tests/test_e2e_booking.py`**: End-to-end tests for booking a resource through the UI (automated)
- **`tests/manual_e2e_booking.py`**: Manual end-to-end test script with step-by-step instructions

## Development Notes

This project follows MVC architecture:
- **Models**: Database models in `src/models/`
- **Views**: Controllers/routes in `src/views/`
- **Templates**: Jinja2 templates in `templates/`

