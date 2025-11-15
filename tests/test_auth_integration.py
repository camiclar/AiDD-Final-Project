"""Integration tests for authentication flow: register → login → access protected route."""
import pytest
from src.database import db
from src.models import User


class TestAuthFlow:
    """Test complete authentication flow."""
    
    def test_register_login_access_protected_route(self, client, app):
        """Test complete flow: register → login → access protected route."""
        with app.app_context():
            # Step 1: Register a new user
            register_response = client.post('/auth/register', data={
                'email': 'newuser@test.com',
                'password': 'testpass123',
                'name': 'New Test User',
                'role': 'student',
                'department': 'Computer Science'
            }, follow_redirects=True)
            
            # Verify registration was successful (should redirect)
            assert register_response.status_code == 200
            
            # Verify user was created in database
            user = User.query.filter_by(email='newuser@test.com').first()
            assert user is not None
            assert user.name == 'New Test User'
            assert user.role == 'student'
            
            # Step 2: Logout (if auto-logged in) and then login
            client.get('/auth/logout', follow_redirects=True)
            
            login_response = client.post('/auth/login', data={
                'email': 'newuser@test.com',
                'password': 'testpass123'
            }, follow_redirects=True)
            
            # Verify login was successful
            assert login_response.status_code == 200
            
            # Step 3: Access a protected route (dashboard)
            dashboard_response = client.get('/dashboard', follow_redirects=True)
            assert dashboard_response.status_code == 200
            # Should not redirect to login page
            assert b'login' not in dashboard_response.data.lower() or b'dashboard' in dashboard_response.data.lower()
            
            # Step 4: Access another protected route (bookings)
            bookings_response = client.get('/bookings', follow_redirects=True)
            assert bookings_response.status_code == 200
    
    def test_register_with_existing_email_fails(self, client, app, test_user):
        """Test that registering with existing email fails."""
        with app.app_context():
            user = User.query.get(test_user)
            response = client.post('/auth/register', data={
                'email': user.email,  # Use existing email
                'password': 'newpass123',
                'name': 'Another User',
                'role': 'student'
            }, follow_redirects=True)
            
            # Should show error message
            assert response.status_code == 200
            # Check that user count didn't increase
            user_count = User.query.filter_by(email=user.email).count()
            assert user_count == 1
    
    def test_login_with_invalid_credentials_fails(self, client, app, test_user):
        """Test that login with invalid credentials fails."""
        with app.app_context():
            user = User.query.get(test_user)
            response = client.post('/auth/login', data={
                'email': user.email,
                'password': 'wrongpassword'
            }, follow_redirects=True)
            
            # Should show error and not redirect to protected route
            assert response.status_code == 200
            # Should still be on login page or show error
            assert b'invalid' in response.data.lower() or b'error' in response.data.lower() or b'login' in response.data.lower()
    
    def test_access_protected_route_without_login_redirects(self, client):
        """Test that accessing protected route without login redirects to login."""
        response = client.get('/dashboard', follow_redirects=False)
        
        # Should redirect (302 or 308)
        assert response.status_code in [302, 308]
        
        # Follow redirects to see where we end up
        final_response = client.get('/dashboard', follow_redirects=True)
        # Should end up on login page or show login form
        assert final_response.status_code == 200
        assert b'login' in final_response.data.lower() or b'sign in' in final_response.data.lower()
    
    def test_logout_clears_session(self, client, app, test_user):
        """Test that logout clears the session."""
        with app.app_context():
            user = User.query.get(test_user)
            # Login first
            client.post('/auth/login', data={
                'email': user.email,
                'password': 'testpass123'
            }, follow_redirects=True)
            
            # Access protected route (should work)
            response = client.get('/dashboard', follow_redirects=True)
            assert response.status_code == 200
            
            # Logout
            logout_response = client.get('/auth/logout', follow_redirects=True)
            assert logout_response.status_code == 200
            
            # Try to access protected route again (should redirect)
            protected_response = client.get('/dashboard', follow_redirects=False)
            assert protected_response.status_code in [302, 308]

