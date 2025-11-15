"""
Manual End-to-End Test Script for Booking Flow

This script provides step-by-step instructions for manually testing the booking flow.
It can also be run as a semi-automated test with user interaction.

Usage:
    python tests/manual_e2e_booking.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from src.database import db
from src.models import User, Resource, Booking
from datetime import datetime, timedelta

def print_step(step_num, description):
    """Print a test step."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)

def manual_e2e_test():
    """Manual E2E test for booking flow."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("MANUAL END-TO-END BOOKING TEST")
        print("="*60)
        print("\nThis script will guide you through testing the booking flow.")
        print("You can also use this to verify the application works correctly.")
        
        # Step 1: Setup test data
        print_step(1, "Setting up test data")
        
        # Create test users
        student = User.query.filter_by(email='e2e_student@test.com').first()
        if not student:
            student = User(
                email='e2e_student@test.com',
                name='E2E Test Student',
                role='student',
                department='Computer Science'
            )
            student.set_password('student123')
            db.session.add(student)
            print("✓ Created test student: e2e_student@test.com / student123")
        else:
            print("✓ Test student already exists")
        
        staff = User.query.filter_by(email='e2e_staff@test.com').first()
        if not staff:
            staff = User(
                email='e2e_staff@test.com',
                name='E2E Test Staff',
                role='staff',
                department='Engineering'
            )
            staff.set_password('staff123')
            db.session.add(staff)
            print("✓ Created test staff: e2e_staff@test.com / staff123")
        else:
            print("✓ Test staff already exists")
        
        # Create test resource
        resource = Resource.query.filter_by(title='E2E Test Resource').first()
        if not resource:
            resource = Resource(
                title='E2E Test Resource',
                description='Resource for E2E testing',
                category='study-room',
                location='Test Building, Room 100',
                capacity=4,
                status='published',
                owner_id=staff.id,
                requires_approval=False
            )
            db.session.add(resource)
            print("✓ Created test resource: E2E Test Resource")
        else:
            print("✓ Test resource already exists")
        
        db.session.commit()
        
        print_step(2, "Test Instructions")
        print("\nFollow these steps in your browser:")
        print("\n1. Start the Flask application:")
        print("   python app.py")
        print("\n2. Open your browser and navigate to: http://localhost:5000")
        print("\n3. Register/Login as the test student:")
        print(f"   Email: e2e_student@test.com")
        print(f"   Password: student123")
        print("\n4. Navigate to 'Browse Resources'")
        print("\n5. Find and click on 'E2E Test Resource'")
        print("\n6. Click 'Book Now' button")
        print("\n7. Fill in the booking form:")
        print("   - Select a date (future date)")
        print("   - Select start time")
        print("   - Select end time")
        print("   - Add optional notes")
        print("\n8. Submit the booking")
        print("\n9. Verify the booking appears in 'My Bookings'")
        print("\n10. Check that the booking status is 'Approved' (since no approval required)")
        
        print_step(3, "Verification")
        print("\nAfter completing the manual steps, this script will verify the booking was created.")
        
        input("\nPress Enter after you have completed the booking in the browser...")
        
        # Verify booking was created
        booking = Booking.query.filter_by(
            resource_id=resource.id,
            user_id=student.id
        ).order_by(Booking.created_at.desc()).first()
        
        if booking:
            print("\n✓ SUCCESS: Booking was created!")
            print(f"  Booking ID: {booking.id}")
            print(f"  Resource: {booking.resource.title}")
            print(f"  User: {booking.user.name}")
            print(f"  Status: {booking.status}")
            print(f"  Start: {booking.start_time}")
            print(f"  End: {booking.end_time}")
        else:
            print("\n✗ FAILED: No booking found. Please check:")
            print("  - Did you complete the booking form?")
            print("  - Did you submit the form?")
            print("  - Are you logged in as the correct user?")
        
        print("\n" + "="*60)
        print("MANUAL E2E TEST COMPLETE")
        print("="*60)

if __name__ == '__main__':
    manual_e2e_test()

