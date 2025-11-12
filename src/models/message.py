"""Message model for the Campus Resource Hub."""
from datetime import datetime
from src.database import db


class Message(db.Model):
    """Message model representing user-to-user messaging."""
    
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.String(100), nullable=True, index=True)  # Can link to booking_id or be a conversation thread
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Message {self.id}>'

