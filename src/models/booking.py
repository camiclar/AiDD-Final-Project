"""Booking model for the Campus Resource Hub."""
from datetime import datetime
from src.database import db


class Booking(db.Model):
    """Booking model representing resource reservations."""
    
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    recurrence = db.Column(db.String(20), nullable=True, default='none')  # none, daily, weekly
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Booking {self.id}>'

