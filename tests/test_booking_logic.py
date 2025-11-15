"""Unit tests for booking logic: conflict detection and status transitions."""
import pytest
from datetime import datetime, timedelta, UTC
from src.database import db
from src.models import Booking, Resource, User
from src.views.bookings import check_booking_conflict, check_user_booking_conflict


class TestBookingConflictDetection:
    """Test booking conflict detection logic."""
    
    def test_no_conflict_when_resource_available(self, app, test_resource, test_user):
        """Test that no conflict is detected when resource is available."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            has_conflict, conflicts = check_booking_conflict(
                resource.id, start_time, end_time
            )
            
            assert has_conflict is False
            assert len(conflicts) == 0
    
    def test_conflict_detected_when_overlapping_approved_booking(self, app, test_resource, test_user):
        """Test that conflict is detected when overlapping with approved booking."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create an existing approved booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            existing_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='approved'
            )
            db.session.add(existing_booking)
            db.session.commit()
            
            # Try to book overlapping time
            new_start = existing_start + timedelta(minutes=30)  # Overlaps
            new_end = new_start + timedelta(hours=2)
            
            has_conflict, conflicts = check_booking_conflict(
                resource.id, new_start, new_end
            )
            
            assert has_conflict is True
            assert len(conflicts) == 1
            assert conflicts[0].id == existing_booking.id
    
    def test_conflict_detected_when_overlapping_pending_booking(self, app, test_resource, test_user):
        """Test that conflict is detected when overlapping with pending booking."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create an existing pending booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            existing_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='pending'
            )
            db.session.add(existing_booking)
            db.session.commit()
            
            # Try to book overlapping time
            new_start = existing_start + timedelta(minutes=30)
            new_end = new_start + timedelta(hours=2)
            
            has_conflict, conflicts = check_booking_conflict(
                resource.id, new_start, new_end
            )
            
            assert has_conflict is True
            assert len(conflicts) == 1
    
    def test_no_conflict_with_cancelled_booking(self, app, test_resource, test_user):
        """Test that cancelled bookings don't cause conflicts."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create a cancelled booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            cancelled_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='cancelled'
            )
            db.session.add(cancelled_booking)
            db.session.commit()
            
            # Try to book same time
            has_conflict, conflicts = check_booking_conflict(
                resource.id, existing_start, existing_end
            )
            
            assert has_conflict is False
            assert len(conflicts) == 0
    
    def test_no_conflict_when_adjacent_times(self, app, test_resource, test_user):
        """Test that adjacent bookings (no overlap) don't conflict."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create an existing booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            existing_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='approved'
            )
            db.session.add(existing_booking)
            db.session.commit()
            
            # Try to book immediately after (no overlap)
            new_start = existing_end  # Starts exactly when previous ends
            new_end = new_start + timedelta(hours=2)
            
            has_conflict, conflicts = check_booking_conflict(
                resource.id, new_start, new_end
            )
            
            assert has_conflict is False
    
    def test_exclude_booking_id_from_conflict_check(self, app, test_resource, test_user):
        """Test that a booking can be excluded from conflict check (for updates)."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create a booking
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Check conflict excluding this booking (should not conflict with itself)
            has_conflict, conflicts = check_booking_conflict(
                resource.id, start_time, end_time, exclude_booking_id=booking.id
            )
            
            assert has_conflict is False


class TestUserBookingConflictDetection:
    """Test user's own booking conflict detection."""
    
    def test_user_conflict_detected_when_overlapping(self, app, test_user, test_resource):
        """Test that user's own overlapping bookings are detected."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create another resource
            staff = User.query.filter_by(role='staff').first()
            resource2 = Resource(
                title='Another Resource',
                description='Another test resource',
                category='study-room',
                location='Building B, Room 202',
                capacity=2,
                status='published',
                owner_id=staff.id,
                requires_approval=False
            )
            db.session.add(resource2)
            db.session.commit()
            
            # Create an existing booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            existing_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='approved'
            )
            db.session.add(existing_booking)
            db.session.commit()
            
            # Try to book different resource at overlapping time
            new_start = existing_start + timedelta(minutes=30)
            new_end = new_start + timedelta(hours=2)
            
            has_conflict, conflicts = check_user_booking_conflict(
                user.id, new_start, new_end
            )
            
            assert has_conflict is True
            assert len(conflicts) == 1
    
    def test_no_user_conflict_when_different_times(self, app, test_user, test_resource):
        """Test that no conflict when user books at different times."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create an existing booking
            existing_start = datetime.now(UTC) + timedelta(hours=1)
            existing_end = existing_start + timedelta(hours=2)
            
            existing_booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=existing_start,
                end_time=existing_end,
                status='approved'
            )
            db.session.add(existing_booking)
            db.session.commit()
            
            # Try to book at different time (no overlap)
            new_start = existing_end + timedelta(hours=1)
            new_end = new_start + timedelta(hours=2)
            
            has_conflict, conflicts = check_user_booking_conflict(
                user.id, new_start, new_end
            )
            
            assert has_conflict is False


class TestBookingStatusTransitions:
    """Test booking status transitions."""
    
    def test_booking_created_with_pending_status_when_approval_required(self, app, test_user, test_staff):
        """Test that booking is created as pending when resource requires approval."""
        with app.app_context():
            user = User.query.get(test_user)
            staff = User.query.get(test_staff)
            resource = Resource(
                title='Approval Required Resource',
                description='Requires approval',
                category='lab-equipment',
                location='Lab 101',
                capacity=1,
                status='published',
                owner_id=staff.id,
                requires_approval=True
            )
            db.session.add(resource)
            db.session.commit()
            
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            assert booking.status == 'pending'
    
    def test_booking_created_with_approved_status_when_no_approval_required(self, app, test_user, test_resource):
        """Test that booking is created as approved when no approval needed."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            assert booking.status == 'approved'
    
    def test_booking_status_transition_pending_to_approved(self, app, test_user, test_resource):
        """Test status transition from pending to approved."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Transition to approved
            booking.status = 'approved'
            db.session.commit()
            
            assert booking.status == 'approved'
    
    def test_booking_status_transition_pending_to_rejected(self, app, test_user, test_resource):
        """Test status transition from pending to rejected."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Transition to rejected
            booking.status = 'rejected'
            db.session.commit()
            
            assert booking.status == 'rejected'
    
    def test_booking_status_transition_approved_to_cancelled(self, app, test_user, test_resource):
        """Test status transition from approved to cancelled."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(hours=2)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=start_time,
                end_time=end_time,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Transition to cancelled
            booking.status = 'cancelled'
            db.session.commit()
            
            assert booking.status == 'cancelled'
    
    def test_booking_status_transition_approved_to_completed(self, app, test_user, test_resource):
        """Test status transition from approved to completed (via utility function)."""
        with app.app_context():
            resource = Resource.query.get(test_resource)
            user = User.query.get(test_user)
            # Create a past booking
            past_start = datetime.now(UTC) - timedelta(hours=3)
            past_end = datetime.now(UTC) - timedelta(hours=1)
            
            booking = Booking(
                resource_id=resource.id,
                user_id=user.id,
                start_time=past_start,
                end_time=past_end,
                status='approved'
            )
            db.session.add(booking)
            db.session.commit()
            
            # Mark past bookings as completed
            from src.utils import mark_past_bookings_completed
            mark_past_bookings_completed()
            
            # Refresh booking from database
            db.session.refresh(booking)
            
            assert booking.status == 'completed'

