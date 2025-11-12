"""User model for the Campus Resource Hub."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import db


class User(db.Model):
    """User model representing students, staff, and admins."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, staff, admin
    department = db.Column(db.String(255), nullable=True)
    profile_image = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    resources = db.relationship('Resource', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    def is_staff(self):
        """Check if user is staff."""
        return self.role == 'staff'
    
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def __repr__(self):
        return f'<User {self.email}>'

