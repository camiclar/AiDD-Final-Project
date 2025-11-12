"""Script to populate the database with dummy data for testing."""
from app import create_app
from src.database import db
from src.models import User, Resource, ResourceImage, ResourceEquipment, Booking, Review, Message, Notification
from datetime import datetime, timedelta
import random

def populate_dummy_data():
    """Populate database with dummy data."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        Message.query.delete()
        Notification.query.delete()
        Review.query.delete()
        Booking.query.delete()
        ResourceEquipment.query.delete()
        ResourceImage.query.delete()
        Resource.query.delete()
        User.query.delete()
        db.session.commit()
        
        print("Creating users...")
        # Create users
        users = []
        
        # Admin user
        admin = User(
            email='admin@university.edu',
            name='Admin User',
            role='admin',
            department='IT Services',
            profile_image='https://images.unsplash.com/photo-1576558656222-ba66febe3dec?w=400'
        )
        admin.set_password('admin123')
        users.append(admin)
        
        # Staff users
        staff1 = User(
            email='sarah.johnson@university.edu',
            name='Dr. Sarah Johnson',
            role='staff',
            department='Computer Science',
            profile_image='https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400'
        )
        staff1.set_password('staff123')
        users.append(staff1)
        
        staff2 = User(
            email='michael.chen@university.edu',
            name='Prof. Michael Chen',
            role='staff',
            department='Engineering',
            profile_image='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'
        )
        staff2.set_password('staff123')
        users.append(staff2)
        
        # Student users
        student1 = User(
            email='alex.martinez@university.edu',
            name='Alex Martinez',
            role='student',
            department='Engineering',
            profile_image='https://images.unsplash.com/photo-1729697967428-5b98d11486a5?w=400'
        )
        student1.set_password('student123')
        users.append(student1)
        
        student2 = User(
            email='emily.wilson@university.edu',
            name='Emily Wilson',
            role='student',
            department='Business',
            profile_image='https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400'
        )
        student2.set_password('student123')
        users.append(student2)
        
        student3 = User(
            email='john.doe@university.edu',
            name='John Doe',
            role='student',
            department='Business',
            profile_image='https://images.unsplash.com/photo-1672685667592-0392f458f46f?w=400'
        )
        student3.set_password('student123')
        users.append(student3)
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        print(f"Created {len(users)} users")
        
        print("Creating resources...")
        # Create resources
        resources_data = [
            {
                'title': 'Innovation Lab Study Room A',
                'description': 'Modern study room with whiteboard, comfortable seating, and natural lighting. Perfect for group study sessions and project collaboration. Equipped with power outlets and high-speed WiFi.',
                'category': 'study-room',
                'location': 'Library Building, 3rd Floor',
                'capacity': 6,
                'status': 'published',
                'owner': staff1,
                'availability_rules': 'Mon-Fri 8AM-10PM, Sat-Sun 10AM-8PM',
                'requires_approval': False,
                'images': ['https://images.unsplash.com/photo-1643199032520-99230e970fb9?w=800'],
                'equipment': ['Whiteboard', 'Projector', '6 Chairs', 'Large Table']
            },
            {
                'title': 'Engineering Lab - 3D Printer Station',
                'description': 'Advanced 3D printing equipment available for engineering and design projects. Includes Prusa i3 MK3S+ printer with various filament options. Training required before first use.',
                'category': 'lab-equipment',
                'location': 'Engineering Building, Room 201',
                'capacity': 2,
                'status': 'published',
                'owner': staff1,
                'availability_rules': 'Mon-Fri 9AM-6PM (Staff supervision required)',
                'requires_approval': True,
                'images': ['https://images.unsplash.com/photo-1627704671340-0969d7dbac25?w=800'],
                'equipment': ['Prusa i3 MK3S+', 'PLA/ABS Filaments', 'Design Software', 'Safety Equipment']
            },
            {
                'title': 'Student Center Event Hall',
                'description': 'Spacious event venue perfect for student organization meetings, presentations, and social gatherings. Features audio system, projector, and flexible seating arrangements.',
                'category': 'event-space',
                'location': 'Student Center, 2nd Floor',
                'capacity': 100,
                'status': 'published',
                'owner': admin,
                'availability_rules': 'Available daily 8AM-11PM with advance booking',
                'requires_approval': True,
                'images': ['https://images.unsplash.com/photo-1761344580244-767bc4e2e8c8?w=800'],
                'equipment': ['Audio System', 'Projector & Screen', '100 Chairs', 'Stage Area', 'Microphones']
            },
            {
                'title': 'Professional Camera & Lighting Kit',
                'description': 'Complete video production setup including 4K camera, LED lights, tripod, and audio equipment. Ideal for student media projects, interviews, and content creation.',
                'category': 'av-equipment',
                'location': 'Media Lab, Student Center',
                'capacity': 1,
                'status': 'published',
                'owner': staff2,
                'availability_rules': 'Check-out for up to 3 days, training required',
                'requires_approval': True,
                'images': ['https://images.unsplash.com/photo-1625252698782-6f9614445f60?w=800'],
                'equipment': ['Sony A7 III Camera', 'LED Light Panel (2x)', 'Tripod', 'Shotgun Microphone', 'SD Cards']
            },
            {
                'title': 'Math Tutoring with Prof. Chen',
                'description': 'One-on-one calculus and statistics tutoring sessions. Experienced professor available for exam prep, homework help, and concept clarification.',
                'category': 'tutoring',
                'location': 'Mathematics Building, Office 305',
                'capacity': 1,
                'status': 'published',
                'owner': staff2,
                'availability_rules': 'Tuesdays & Thursdays 2PM-5PM',
                'requires_approval': False,
                'images': ['https://images.unsplash.com/photo-1680226426952-514723cee6b8?w=800'],
                'equipment': []
            },
            {
                'title': 'Library Meeting Room B',
                'description': 'Quiet private meeting room perfect for thesis discussions, advisor meetings, or focused group work. Window view and excellent sound insulation.',
                'category': 'study-room',
                'location': 'Library Building, 2nd Floor',
                'capacity': 4,
                'status': 'published',
                'owner': admin,
                'availability_rules': 'Mon-Sun 8AM-11PM',
                'requires_approval': False,
                'images': ['https://images.unsplash.com/photo-1625252698782-6f9614445f60?w=800'],
                'equipment': ['Whiteboard', '4 Chairs', 'Conference Table']
            }
        ]
        
        resources = []
        for data in resources_data:
            resource = Resource(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                location=data['location'],
                capacity=data['capacity'],
                status=data['status'],
                owner_id=data['owner'].id,
                availability_rules=data['availability_rules'],
                requires_approval=data['requires_approval']
            )
            db.session.add(resource)
            db.session.flush()
            
            # Add images
            for img_url in data['images']:
                img = ResourceImage(resource_id=resource.id, image_url=img_url)
                db.session.add(img)
            
            # Add equipment
            for eq_name in data['equipment']:
                equipment = ResourceEquipment(resource_id=resource.id, equipment_name=eq_name)
                db.session.add(equipment)
            
            resources.append(resource)
        
        db.session.commit()
        print(f"Created {len(resources)} resources")
        
        print("Creating bookings...")
        # Create some bookings
        now = datetime.utcnow()
        bookings_data = [
            {
                'resource': resources[0],
                'user': student1,
                'start_time': now + timedelta(days=5, hours=14),
                'end_time': now + timedelta(days=5, hours=16),
                'status': 'approved',
                'notes': 'Working on group project for CS 401'
            },
            {
                'resource': resources[1],
                'user': student1,
                'start_time': now + timedelta(days=7, hours=10),
                'end_time': now + timedelta(days=7, hours=14),
                'status': 'pending',
                'notes': 'Need to print prototype parts for senior design project'
            },
            {
                'resource': resources[4],
                'user': student2,
                'start_time': now + timedelta(days=3, hours=14),
                'end_time': now + timedelta(days=3, hours=15),
                'status': 'approved',
                'notes': 'Help with Calc II midterm prep'
            },
            {
                'resource': resources[2],
                'user': student3,
                'start_time': now + timedelta(days=10, hours=18),
                'end_time': now + timedelta(days=10, hours=22),
                'status': 'pending',
                'notes': 'Business Club networking event'
            },
            # Add some completed bookings for testing reviews
            {
                'resource': resources[0],
                'user': student2,
                'start_time': now - timedelta(days=5, hours=14),
                'end_time': now - timedelta(days=5, hours=16),
                'status': 'completed',
                'notes': 'Group study session'
            },
            {
                'resource': resources[4],
                'user': student1,
                'start_time': now - timedelta(days=3, hours=14),
                'end_time': now - timedelta(days=3, hours=15),
                'status': 'completed',
                'notes': 'Calculus help session'
            }
        ]
        
        for data in bookings_data:
            booking = Booking(
                resource_id=data['resource'].id,
                user_id=data['user'].id,
                start_time=data['start_time'],
                end_time=data['end_time'],
                status=data['status'],
                notes=data['notes']
            )
            db.session.add(booking)
        
        db.session.commit()
        print(f"Created {len(bookings_data)} bookings")
        
        print("Creating reviews...")
        # Create some reviews
        reviews_data = [
            {
                'resource': resources[0],
                'user': student1,
                'rating': 5,
                'comment': 'Perfect study space! Clean, quiet, and all the equipment worked great. Will definitely book again.'
            },
            {
                'resource': resources[0],
                'user': student2,
                'rating': 4,
                'comment': 'Great location and setup. Only minor issue was the whiteboard markers were running low.'
            },
            {
                'resource': resources[1],
                'user': student2,
                'rating': 5,
                'comment': 'Amazing equipment and Dr. Johnson was very helpful with setup. Print quality was excellent!'
            },
            {
                'resource': resources[4],
                'user': student1,
                'rating': 5,
                'comment': 'Prof. Chen is incredibly patient and explains concepts clearly. Helped me ace my exam!'
            }
        ]
        
        for data in reviews_data:
            review = Review(
                resource_id=data['resource'].id,
                user_id=data['user'].id,
                rating=data['rating'],
                comment=data['comment']
            )
            db.session.add(review)
        
        db.session.commit()
        print(f"Created {len(reviews_data)} reviews")
        
        print("Creating messages...")
        # Create some messages
        booking = Booking.query.filter_by(status='pending').first()
        if booking:
            message1 = Message(
                thread_id=f"booking_{booking.id}",
                sender_id=booking.resource.owner_id,
                receiver_id=booking.user_id,
                content="Hi, I've received your booking request for the 3D printer. Could you please confirm you've completed the safety training?",
                read=True
            )
            db.session.add(message1)
            
            message2 = Message(
                thread_id=f"booking_{booking.id}",
                sender_id=booking.user_id,
                receiver_id=booking.resource.owner_id,
                content="Yes, I completed the training last month on October 10th. My certification number is ST-2024-0356.",
                read=False
            )
            db.session.add(message2)
        
        db.session.commit()
        print("Created sample messages")
        
        print("\n" + "="*60)
        print("DUMMY DATA CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nTEST CREDENTIALS:")
        print("-"*60)
        print("Admin:")
        print("  Email: admin@university.edu")
        print("  Password: admin123")
        print("\nStaff:")
        print("  Email: sarah.johnson@university.edu")
        print("  Password: staff123")
        print("\n  Email: michael.chen@university.edu")
        print("  Password: staff123")
        print("\nStudents:")
        print("  Email: alex.martinez@university.edu")
        print("  Password: student123")
        print("\n  Email: emily.wilson@university.edu")
        print("  Password: student123")
        print("\n  Email: john.doe@university.edu")
        print("  Password: student123")
        print("="*60)

if __name__ == '__main__':
    populate_dummy_data()

