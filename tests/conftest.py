"""Pytest configuration and fixtures."""
import pytest
import os
import tempfile
from app import create_app
from src.database import db
from src.models import User, Resource, Booking, Review, Message, Notification


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Create app with test configuration
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        db.session.remove()
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user. Returns user ID - query for user object in tests."""
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User',
            role='student',
            department='Computer Science'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        yield user_id


@pytest.fixture
def test_staff(app):
    """Create a test staff user. Returns staff ID - query for user object in tests."""
    with app.app_context():
        staff = User(
            email='staff@example.com',
            name='Staff Member',
            role='staff',
            department='Engineering'
        )
        staff.set_password('staffpass123')
        db.session.add(staff)
        db.session.commit()
        staff_id = staff.id
        yield staff_id


@pytest.fixture
def test_admin(app):
    """Create a test admin user. Returns admin ID - query for user object in tests."""
    with app.app_context():
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin',
            department='IT'
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        yield admin_id


@pytest.fixture
def test_resource(app, test_staff):
    """Create a test resource. Returns resource ID - query for resource object in tests."""
    with app.app_context():
        staff = User.query.get(test_staff)
        resource = Resource(
            title='Test Study Room',
            description='A test study room',
            category='study-room',
            location='Building A, Room 101',
            capacity=4,
            status='published',
            owner_id=staff.id,
            requires_approval=False
        )
        db.session.add(resource)
        db.session.commit()
        resource_id = resource.id
        yield resource_id


@pytest.fixture
def authenticated_client(client, app, test_user):
    """Create an authenticated test client."""
    with app.app_context():
        user = User.query.get(test_user)
        # Login the user
        response = client.post('/auth/login', data={
            'email': user.email,
            'password': 'testpass123'
        }, follow_redirects=True)
    return client

