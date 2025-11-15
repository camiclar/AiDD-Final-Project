"""Unit tests for Data Access Layer - CRUD operations independent of Flask routes."""
import pytest
from datetime import datetime, timedelta, UTC
from src.database import db
from src.models import User, Resource, Booking, Review


class TestUserCRUD:
    """Test User model CRUD operations."""
    
    def test_create_user(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(
                email='newuser@example.com',
                name='New User',
                role='student',
                department='Computer Science'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            retrieved_user = User.query.filter_by(email='newuser@example.com').first()
            assert retrieved_user is not None
            assert retrieved_user.name == 'New User'
            assert retrieved_user.role == 'student'
            assert retrieved_user.check_password('password123')
    
    def test_read_user(self, app, test_user):
        """Test reading a user."""
        with app.app_context():
            user = User.query.get(test_user)
            retrieved_user = User.query.get(user.id)
            assert retrieved_user is not None
            assert retrieved_user.email == user.email
            assert retrieved_user.name == user.name
    
    def test_update_user(self, app, test_user):
        """Test updating a user."""
        with app.app_context():
            user = User.query.get(test_user)
            user.name = 'Updated Name'
            user.department = 'Updated Department'
            db.session.commit()
            
            # Verify update
            updated_user = User.query.get(test_user)
            assert updated_user.name == 'Updated Name'
            assert updated_user.department == 'Updated Department'
    
    def test_delete_user(self, app, test_user):
        """Test deleting a user."""
        with app.app_context():
            user = User.query.get(test_user)
            user_id = user.id
            db.session.delete(user)
            db.session.commit()
            
            # Verify deletion
            deleted_user = User.query.get(user_id)
            assert deleted_user is None


class TestResourceCRUD:
    """Test Resource model CRUD operations."""
    
    def test_create_resource(self, app, test_staff):
        """Test creating a resource."""
        with app.app_context():
            staff = User.query.get(test_staff)
            resource = Resource(
                title='New Resource',
                description='A new test resource',
                category='study-room',
                location='Building C, Room 303',
                capacity=6,
                status='published',
                owner_id=staff.id,
                requires_approval=True
            )
            
            db.session.add(resource)
            db.session.commit()
            
            # Verify resource was created
            retrieved_resource = Resource.query.filter_by(title='New Resource').first()
            assert retrieved_resource is not None
            assert retrieved_resource.description == 'A new test resource'
            assert retrieved_resource.capacity == 6
            assert retrieved_resource.owner_id == staff.id
    
    def test_read_resource(self, app, test_resource):
        """Test reading a resource."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            retrieved_resource = Resource.query.get(resource.id)
            assert retrieved_resource is not None
            assert retrieved_resource.title == resource.title
            assert retrieved_resource.category == resource.category
    
    def test_update_resource(self, app, test_resource):
        """Test updating a resource."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            resource.title = 'Updated Title'
            resource.capacity = 10
            resource.status = 'archived'
            db.session.commit()
            
            # Verify update
            updated_resource = Resource.query.get(test_resource)
            assert updated_resource.title == 'Updated Title'
            assert updated_resource.capacity == 10
            assert updated_resource.status == 'archived'
    
    def test_delete_resource(self, app, test_resource):
        """Test deleting a resource."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            resource_id = resource.id
            db.session.delete(resource)
            db.session.commit()
            
            # Verify deletion
            deleted_resource = Resource.query.get(resource_id)
            assert deleted_resource is None


class TestBookingCRUD:
    """Test Booking model CRUD operations."""
    
    def test_create_booking(self, app, test_user, test_resource):
        """Test creating a booking."""
        with app.app_context():
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                start_time=start_time,
                end_time=end_time,
                status='pending',
                notes='Test booking notes'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Verify booking was created
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            retrieved_booking = Booking.query.filter_by(
                resource_id=resource.id,
                user_id=user.id
            ).first()
            assert retrieved_booking is not None
            assert retrieved_booking.status == 'pending'
            assert retrieved_booking.notes == 'Test booking notes'
    
    def test_read_booking(self, app, test_user, test_resource):
        """Test reading a booking."""
        with app.app_context():
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                start_time=start_time,
                end_time=end_time,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            retrieved_booking = Booking.query.get(booking.id)
            assert retrieved_booking is not None
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            assert retrieved_booking.resource_id == resource.id
            assert retrieved_booking.user_id == user.id
    
    def test_update_booking(self, app, test_user, test_resource):
        """Test updating a booking."""
        with app.app_context():
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                start_time=start_time,
                end_time=end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Update booking
            booking.status = 'approved'
            booking.notes = 'Updated notes'
            db.session.commit()
            
            # Verify update
            updated_booking = Booking.query.get(booking.id)
            assert updated_booking.status == 'approved'
            assert updated_booking.notes == 'Updated notes'
    
    def test_delete_booking(self, app, test_user, test_resource):
        """Test deleting a booking."""
        with app.app_context():
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                start_time=start_time,
                end_time=end_time,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            booking_id = booking.id
            db.session.delete(booking)
            db.session.commit()
            
            # Verify deletion
            deleted_booking = Booking.query.get(booking_id)
            assert deleted_booking is None


class TestReviewCRUD:
    """Test Review model CRUD operations."""
    
    def test_create_review(self, app, test_user, test_resource):
        """Test creating a review."""
        with app.app_context():
            review = Review(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                rating=5,
                comment='Great resource!'
            )
            
            db.session.add(review)
            db.session.commit()
            
            # Verify review was created
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            retrieved_review = Review.query.filter_by(
                resource_id=resource.id,
                user_id=user.id
            ).first()
            assert retrieved_review is not None
            assert retrieved_review.rating == 5
            assert retrieved_review.comment == 'Great resource!'
    
    def test_read_review(self, app, test_user, test_resource):
        """Test reading a review."""
        with app.app_context():
            review = Review(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                rating=4,
                comment='Good resource'
            )
            db.session.add(review)
            db.session.commit()
            
            retrieved_review = Review.query.get(review.id)
            assert retrieved_review is not None
            assert retrieved_review.rating == 4
    
    def test_update_review(self, app, test_user, test_resource):
        """Test updating a review."""
        with app.app_context():
            review = Review(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                rating=3,
                comment='Initial comment'
            )
            db.session.add(review)
            db.session.commit()
            
            # Update review
            review.rating = 5
            review.comment = 'Updated comment'
            db.session.commit()
            
            # Verify update
            updated_review = Review.query.get(review.id)
            assert updated_review.rating == 5
            assert updated_review.comment == 'Updated comment'
    
    def test_delete_review(self, app, test_user, test_resource):
        """Test deleting a review."""
        with app.app_context():
            review = Review(
                resource_id=Resource.query.get(test_resource).id,
                user_id=User.query.get(test_user).id,
                rating=4,
                comment='Test review'
            )
            db.session.add(review)
            db.session.commit()
            
            review_id = review.id
            db.session.delete(review)
            db.session.commit()
            
            # Verify deletion
            deleted_review = Review.query.get(review_id)
            assert deleted_review is None


class TestDataAccessQueries:
    """Test complex queries in Data Access Layer."""
    
    def test_query_user_bookings(self, app, test_user, test_resource):
        """Test querying all bookings for a user."""
        with app.app_context():
            # Create multiple bookings
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            for i in range(3):
                start_time = datetime.now(UTC) + timedelta(hours=i+1)
                end_time = start_time + timedelta(hours=1)
                booking = Booking(
                    resource_id=resource.id,
                    user_id=user.id,
                    start_time=start_time,
                    end_time=end_time,
                    status='approved'
                )
                db.session.add(booking)
            db.session.commit()
            
            # Query user bookings
            user_bookings = Booking.query.filter_by(user_id=user.id).all()
            assert len(user_bookings) == 3
    
    def test_query_resource_bookings(self, app, test_user, test_resource):
        """Test querying all bookings for a resource."""
        with app.app_context():
            # Create another user
            user2 = User(
                email='user2@example.com',
                name='User 2',
                role='student'
            )
            user2.set_password('pass123')
            db.session.add(user2)
            db.session.commit()
            
            # Create bookings by both users
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            for booking_user in [user, user2]:
                start_time = datetime.now(UTC) + timedelta(hours=1)
                end_time = start_time + timedelta(hours=1)
                booking = Booking(
                    resource_id=resource.id,
                    user_id=booking_user.id,
                    start_time=start_time,
                    end_time=end_time,
                    status='approved'
                )
                db.session.add(booking)
            db.session.commit()
            
            # Query resource bookings
            resource_bookings = Booking.query.filter_by(resource_id=resource.id).all()
            assert len(resource_bookings) == 2
    
    def test_query_pending_bookings(self, app, test_user, test_resource):
        """Test querying pending bookings."""
        with app.app_context():
            # Create bookings with different statuses
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            statuses = ['pending', 'approved', 'pending', 'rejected']
            for status in statuses:
                start_time = datetime.now(UTC) + timedelta(hours=1)
                end_time = start_time + timedelta(hours=1)
                booking = Booking(
                    resource_id=resource.id,
                    user_id=user.id,
                    start_time=start_time,
                    end_time=end_time,
                    status=status
                )
                db.session.add(booking)
            db.session.commit()
            
            # Query pending bookings
            pending_bookings = Booking.query.filter_by(status='pending').all()
            assert len(pending_bookings) == 2

