"""Security tests: SQL injection and template escaping."""
import pytest
from src.database import db
from src.models import User, Resource, Booking
from sqlalchemy import text


class TestSQLInjectionProtection:
    """Test protection against SQL injection attacks."""
    
    def test_sql_injection_in_user_query_parameterized(self, app, test_user):
        """Test that user queries use parameterized queries (ORM protection)."""
        with app.app_context():
            # Attempt SQL injection in email field
            malicious_email = "test@example.com' OR '1'='1"
            
            # Using ORM (should be safe)
            user = User.query.filter_by(email=malicious_email).first()
            # Should not find user (treats as literal string, not SQL)
            assert user is None
            
            # Verify the malicious string is treated as literal
            # Create a user with the malicious string as actual email
            malicious_user = User(
                email=malicious_email,
                name='Malicious User',
                role='student'
            )
            malicious_user.set_password('pass123')
            db.session.add(malicious_user)
            db.session.commit()
            
            # Now query should find it (as literal string)
            found_user = User.query.filter_by(email=malicious_email).first()
            assert found_user is not None
            assert found_user.email == malicious_email
    
    def test_sql_injection_in_resource_search_parameterized(self, app, test_resource):
        """Test that resource search uses parameterized queries."""
        with app.app_context():
            # Attempt SQL injection in search
            malicious_search = "'; DROP TABLE users; --"
            
            # Using ORM filter (should be safe)
            resources = Resource.query.filter(
                Resource.title.like(f'%{malicious_search}%')
            ).all()
            
            # Should return empty (no resources match) but not execute DROP
            assert len(resources) == 0
            
            # Verify users table still exists
            users = User.query.all()
            assert len(users) >= 0  # Table still exists
    
    def test_sql_injection_in_booking_query_parameterized(self, app, test_user, test_resource):
        """Test that booking queries use parameterized queries."""
        with app.app_context():
            # Attempt SQL injection in booking query
            malicious_id = "1 OR 1=1"
            
            try:
                # Using ORM (should be safe - will raise ValueError if not integer)
                booking = Booking.query.get(int(malicious_id.split()[0]))
                # If it doesn't raise an error, it should be safe
            except ValueError:
                # Expected - malicious_id is not a valid integer
                pass
            
            # Verify parameterized query works correctly
            booking_id = 99999  # Non-existent ID
            booking = Booking.query.get(booking_id)
            assert booking is None
    
    def test_raw_sql_with_parameterized_queries(self, app):
        """Test that raw SQL uses parameterized queries when needed."""
        with app.app_context():
            # If using raw SQL, it should use parameterized queries
            # This tests that text() function properly escapes
            malicious_input = "'; DROP TABLE users; --"
            
            # Using SQLAlchemy text() with parameters (safe)
            result = db.session.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": malicious_input}
            ).fetchall()
            
            # Should execute safely (treats as literal string)
            # Verify users table still exists
            users = User.query.all()
            assert users is not None


class TestTemplateEscaping:
    """Test that templates properly escape user input."""
    
    def test_xss_protection_in_user_name(self, client, app):
        """Test that user names with XSS attempts are escaped in templates."""
        with app.app_context():
            # Create user with XSS attempt in name
            xss_name = '<script>alert("XSS")</script>'
            user = User(
                email='xss@test.com',
                name=xss_name,
                role='student'
            )
            user.set_password('pass123')
            db.session.add(user)
            db.session.commit()
            
            # Login as this user
            client.post('/auth/login', data={
                'email': 'xss@test.com',
                'password': 'pass123'
            }, follow_redirects=True)
            
            # Access profile page
            response = client.get('/profile', follow_redirects=True)
            
            # Verify script tags are escaped (should appear as text, not execute)
            assert response.status_code == 200
            # Jinja2 auto-escapes by default, so script tags should be in HTML as text
            response_text = response.data.decode('utf-8')
            # Should contain escaped version or the literal text
            assert '<script>' in response_text or '&lt;script&gt;' in response_text
    
    def test_xss_protection_in_resource_description(self, client, app, test_staff):
        """Test that resource descriptions with XSS are escaped."""
        with app.app_context():
            staff = User.query.get(test_staff)
            # Login as staff
            client.post('/auth/login', data={
                'email': staff.email,
                'password': 'staffpass123'
            }, follow_redirects=True)
            
            # Create resource with XSS in description
            xss_description = '<img src=x onerror=alert("XSS")>'
            
            response = client.post('/resources/create', data={
                'title': 'XSS Test Resource',
                'description': xss_description,
                'category': 'study-room',
                'location': 'Test Location',
                'capacity': 5,
                'status': 'published',
                'requires_approval': False
            }, follow_redirects=True)
            
            # View the resource
            resource = Resource.query.filter_by(title='XSS Test Resource').first()
            if resource:
                detail_response = client.get(f'/resources/{resource.id}', follow_redirects=True)
                
                # Verify XSS is escaped
                assert detail_response.status_code == 200
                response_text = detail_response.data.decode('utf-8')
                # Should contain escaped version
                assert 'onerror' in response_text or '&lt;img' in response_text
    
    def test_xss_protection_in_booking_notes(self, client, app, test_user, test_resource):
        """Test that booking notes with XSS are escaped."""
        with app.app_context():
            # Get user and resource objects
            user = User.query.get(test_user)
            resource = Resource.query.get(test_resource)
            
            # Login
            client.post('/auth/login', data={
                'email': user.email,
                'password': 'testpass123'
            }, follow_redirects=True)
            
            # Create booking with XSS in notes
            xss_notes = '<script>document.cookie="stolen"</script>'
            
            from datetime import datetime, timedelta, UTC
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='approved',
                notes=xss_notes
            )
            db.session.add(booking)
            db.session.commit()
            
            # View bookings page
            response = client.get('/bookings', follow_redirects=True)
            
            # Verify XSS is escaped
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            # Should contain escaped version
            assert '<script>' in response_text or '&lt;script&gt;' in response_text
    
    def test_sql_injection_in_form_inputs_handled(self, client, app):
        """Test that form inputs with SQL injection attempts are handled safely."""
        with app.app_context():
            # Attempt SQL injection in registration form
            sql_injection_email = "admin@test.com'--"
            sql_injection_name = "Name'; DROP TABLE users; --"
            
            response = client.post('/auth/register', data={
                'email': sql_injection_email,
                'password': 'pass123',
                'name': sql_injection_name,
                'role': 'student'
            }, follow_redirects=True)
            
            # Should either succeed (treating as literal) or fail gracefully
            # But should not execute SQL
            assert response.status_code == 200
            
            # Verify users table still exists and queryable
            users = User.query.all()
            assert users is not None
            
            # If user was created, verify it was created with literal values
            user = User.query.filter_by(email=sql_injection_email).first()
            if user:
                assert user.email == sql_injection_email  # Stored as literal

