"""Utility functions for the Campus Resource Hub."""
from datetime import datetime
from src.database import db
from src.models import Booking


def mark_past_bookings_completed():
    """Mark approved bookings as completed if their end time has passed."""
    now = datetime.utcnow()
    past_bookings = Booking.query.filter(
        Booking.status == 'approved',
        Booking.end_time < now
    ).all()
    
    for booking in past_bookings:
        booking.status = 'completed'
        booking.updated_at = now
    
    if past_bookings:
        db.session.commit()
        return len(past_bookings)
    
    return 0

