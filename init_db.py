"""Database initialization script for Campus Resource Hub."""
from app import create_app
from src.database import db
from src.models import User, Resource, ResourceImage, ResourceEquipment, Booking, Review, Message, Notification

def init_database():
    """Initialize the database with tables."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (use with caution in production!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Get the actual file path
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Extract path from sqlite:/// URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            import os
            abs_path = os.path.abspath(db_path)
            
            print("=" * 60)
            print("Database initialized successfully!")
            print("=" * 60)
            print(f"Database URI: {db_uri}")
            print(f"Database file path: {abs_path}")
            print(f"Database file exists: {os.path.exists(abs_path)}")
            if os.path.exists(abs_path):
                file_size = os.path.getsize(abs_path)
                print(f"Database file size: {file_size} bytes")
            print("=" * 60)

if __name__ == '__main__':
    init_database()

