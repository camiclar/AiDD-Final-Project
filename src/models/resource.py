"""Resource model for the Campus Resource Hub."""
from datetime import datetime
from src.database import db


class Resource(db.Model):
    """Resource model representing campus resources available for booking."""
    
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # study-room, lab-equipment, event-space, av-equipment, tutoring, other
    location = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, published, archived
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    availability_rules = db.Column(db.Text, nullable=True)
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    images = db.relationship('ResourceImage', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    equipment = db.relationship('ResourceEquipment', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resource {self.title}>'


class ResourceImage(db.Model):
    """Resource images model."""
    
    __tablename__ = 'resource_images'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ResourceImage {self.id}>'


class ResourceEquipment(db.Model):
    """Resource equipment list model."""
    
    __tablename__ = 'resource_equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    equipment_name = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<ResourceEquipment {self.equipment_name}>'

