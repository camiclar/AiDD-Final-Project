# Campus Resource Hub

A full-stack web application that enables university departments, student organizations, and individuals to list, share, and reserve campus resources.

## Features

- Search & booking with calendar integration
- Role-based access control (Student, Staff, Admin)
- Ratings, reviews, and messaging between users
- Administrative workflows for approvals, moderation, and analytics
- AI-powered analytics assistant for admins

## Tech Stack

- **Backend**: Flask (Python 3.10+)
- **Frontend**: Jinja2 templates + Bootstrap 5
- **Database**: SQLite
- **Authentication**: Flask-Login with bcrypt password hashing
- **AI Integration**: Google Gemini API for analytics chatbot

---

## Setup & Run Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd AiDD-Final-Project
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)

For AI chatbot functionality, create a `.env` file in the root directory:

```bash
# .env
GEMINI_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

**Note:** The `.env` file is already in `.gitignore` and will not be committed to version control.

See `CHATBOT_SETUP.md` for detailed instructions on obtaining a Google Gemini API key.

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 6: Access the Application

Open your browser and navigate to:
- **Home**: `http://localhost:5000`
- **Login**: `http://localhost:5000/auth/login`
- **Register**: `http://localhost:5000/auth/register`

---

## Database Migration Steps

The application uses SQLite with SQLAlchemy ORM. Database tables are automatically created on first run.

### Automatic Database Initialization

The database is automatically initialized when you run the application for the first time. The database file is created at:
```
instance/campus_resource_hub.db
```

### Manual Database Initialization

If you need to manually initialize or reset the database:

```bash
python init_db.py
```

### Populating Test Data

To populate the database with sample data (users, resources, bookings, reviews, messages):

```bash
python populate_dummy_data.py
```

**Warning:** This script will **clear all existing data** in the database before populating test data.

**Test credentials are available in `TEST_CREDENTIALS.md`**

### Database Schema

The database includes the following tables:
- `users` - User accounts (students, staff, admins)
- `resources` - Campus resources (rooms, equipment, etc.)
- `bookings` - Resource reservations
- `reviews` - User reviews and ratings
- `messages` - Direct messages between users
- `notifications` - System notifications
- `resource_images` - Resource image attachments
- `resource_equipment` - Equipment associated with resources

For a detailed Entity-Relationship Diagram, see `docs/context/shared/Campus_Resource_Hub_ERD.pdf`

---

## Repository Structure

```
.
├── app.py                      # Main Flask application entry point
├── init_db.py                  # Database initialization script
├── populate_dummy_data.py      # Script to populate test data
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
│
├── src/                        # Application source code
│   ├── __init__.py
│   ├── database.py             # Database configuration and initialization
│   ├── decorators.py           # Role-based access control decorators
│   │
│   ├── models/                 # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── resource.py         # Resource model
│   │   ├── booking.py          # Booking model
│   │   ├── review.py           # Review model
│   │   ├── message.py          # Message model
│   │   └── notification.py     # Notification model
│   │
│   ├── views/                  # Flask route handlers (controllers)
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── dashboard.py        # Dashboard routes
│   │   ├── resources.py        # Resource management routes
│   │   ├── bookings.py         # Booking routes
│   │   ├── reviews.py          # Review routes
│   │   ├── messages.py         # Messaging routes
│   │   ├── notifications.py    # Notification routes
│   │   ├── profile.py          # User profile routes
│   │   └── admin.py            # Admin panel routes
│   │
│   └── utils/                  # Utility functions
│       ├── __init__.py         # Image processing, booking utilities
│       └── chatbot.py          # AI chatbot utilities
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template with navigation
│   ├── auth/                   # Authentication templates
│   ├── dashboard/              # Dashboard templates
│   ├── resources/              # Resource templates
│   ├── bookings/               # Booking templates
│   ├── reviews/                # Review templates
│   ├── messages/               # Messaging templates
│   ├── notifications/          # Notification templates
│   ├── profile/                # Profile templates
│   └── admin/                  # Admin panel templates
│
├── static/                     # Static files (CSS, JS, images)
│   └── uploads/                # User-uploaded files
│       └── profile_pictures/   # Profile picture uploads
│
├── instance/                   # Instance-specific files
│   └── campus_resource_hub.db  # SQLite database file
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures and configuration
│   ├── test_booking_logic.py   # Unit tests for booking logic
│   ├── test_data_access.py     # Data Access Layer tests
│   ├── test_auth_integration.py # Authentication integration tests
│   ├── test_security.py        # Security tests (SQL injection, XSS)
│   ├── test_e2e_booking.py     # End-to-end booking tests
│   └── manual_e2e_booking.py   # Manual E2E test script
│
├── docs/                       # Project documentation
│   └── context/                # AI context files
│       ├── APA/                # Agility, Processes & Automation artifacts
│       ├── DT/                 # Design Thinking artifacts (wireframes, prototype)
│       ├── PM/                 # Product Management materials (PRD)
│       └── shared/             # Shared documentation (ERD, main context)
│
├── prompt/                     # AI interaction logs
│   ├── dev_notes.md            # Development notes and AI interactions
│   └── golden_prompts.md       # High-impact prompts
│
├── CHATBOT_SETUP.md            # AI chatbot setup instructions
├── TEST_CREDENTIALS.md         # Test account credentials
└── README.md                   # This file
```

### Architecture

This project follows **MVC (Model-View-Controller)** architecture:

- **Models** (`src/models/`): Database models using SQLAlchemy ORM
- **Views** (`src/views/`): Route handlers (controllers) that process requests
- **Templates** (`templates/`): Jinja2 templates that render HTML responses

---

## MCP Usage

This project uses an **AI-First Repository Layout** designed to support context-aware development with AI tools like Cursor. The repository structure includes context files that help AI assistants understand the project better.

### Context Files Location

Context files are located in `docs/context/`:

- **`docs/context/shared/`**: Common reference materials
  - `main-context.md` - High-level project overview and glossary
  - `Campus_Resource_Hub_ERD.pdf` - Entity-Relationship Diagram
  - `Project-Description.docx` - Original project requirements

- **`docs/context/DT/`**: Design Thinking artifacts
  - Wireframes and design mockups
  - Prototype code exported from Figma

- **`docs/context/PM/`**: Product Management materials
  - Product Requirements Document (PRD)
  - User stories and success metrics

- **`docs/context/APA/`**: Agility, Processes & Automation artifacts

### AI Interaction Logs

The `prompt/` directory contains logs of AI interactions:

- **`prompt/dev_notes.md`**: Development notes documenting AI-assisted development sessions
- **`prompt/golden_prompts.md`**: High-impact prompts that produced excellent results

### Using Context Files with AI Tools

When working with AI coding assistants (like Cursor):

1. The context files in `docs/context/` provide background information about the project
2. The repository structure follows AI-first principles for better context understanding
3. Development notes in `prompt/` help track AI-assisted development decisions

### AI Features in the Application

The application includes an **AI-powered analytics assistant** on the admin dashboard:

- Uses Google Gemini API to answer questions about resource usage
- Generates SQL queries from natural language questions
- Provides insights about bookings, resources, and user activity

See `CHATBOT_SETUP.md` for setup instructions.

---

## Test Instructions

The project includes comprehensive tests using pytest.

### Install Test Dependencies

Test dependencies are included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Specific Test Files

```bash
# Unit tests for booking logic
pytest tests/test_booking_logic.py

# Data Access Layer tests (CRUD operations)
pytest tests/test_data_access.py

# Authentication integration tests
pytest tests/test_auth_integration.py

# Security tests (SQL injection, XSS protection)
pytest tests/test_security.py

# End-to-end booking tests
pytest tests/test_e2e_booking.py
```

### Run Tests with Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

This generates a coverage report in `htmlcov/index.html`. Open it in a browser to view detailed coverage information.

### Test Structure

- **`tests/conftest.py`**: Pytest fixtures for test setup (app, client, test users, test resources)
- **`tests/test_booking_logic.py`**: Unit tests for booking conflict detection and status transitions
- **`tests/test_data_access.py`**: Unit tests for Data Access Layer (CRUD operations independent of Flask routes)
- **`tests/test_auth_integration.py`**: Integration tests for authentication flow (register → login → access protected route)
- **`tests/test_security.py`**: Security tests for SQL injection protection and template escaping (XSS)
- **`tests/test_e2e_booking.py`**: End-to-end tests for booking a resource through the UI (automated)
- **`tests/manual_e2e_booking.py`**: Manual end-to-end test script with step-by-step instructions

### Running Manual E2E Tests

For manual testing with a real browser:

```bash
python tests/manual_e2e_booking.py
```

This script provides step-by-step instructions for manually testing the booking flow.

---

## Additional Resources

- **Test Credentials**: See `TEST_CREDENTIALS.md` for test account information
- **Chatbot Setup**: See `CHATBOT_SETUP.md` for AI chatbot configuration
- **Project Documentation**: See `docs/context/shared/main-context.md` for detailed project overview

---

## Development Notes

This project demonstrates AI-first full-stack development using:
- Cursor for AI-assisted coding
- Context-aware repository design
- Comprehensive testing with pytest
- MVC architecture with Flask

For development notes and AI interaction logs, see `prompt/dev_notes.md`.
