"""Review model for the Campus Resource Hub."""
from datetime import datetime
from src.database import db


class Review(db.Model):
    """Review model representing user reviews of resources."""
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure one review per user per resource
    __table_args__ = (db.UniqueConstraint('resource_id', 'user_id', name='unique_user_resource_review'),)
    
    def __repr__(self):
        return f'<Review {self.id}>'

