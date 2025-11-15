"""Dashboard routes for the Campus Resource Hub."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime
from src.database import db
from src.models import User, Resource, Booking, Review
from src.views.resources import get_resource_stats

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """User dashboard with stats and overview."""
    # Get user's upcoming bookings
    upcoming_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.start_time >= datetime.utcnow(),
        Booking.status.in_(['approved', 'pending'])
    ).order_by(Booking.start_time).limit(5).all()
    
    # Get all published resources for stats
    published_resources = Resource.query.filter_by(status='published').all()
    
    # Get popular resources (top 4 by booking count)
    popular_resources = db.session.query(
        Resource.id,
        Resource.title,
        Resource.description,
        Resource.category,
        func.count(Booking.id).label('booking_count')
    ).join(Booking, Resource.id == Booking.resource_id, isouter=True)\
     .filter(Resource.status == 'published')\
     .group_by(Resource.id, Resource.title, Resource.description, Resource.category)\
     .order_by(desc('booking_count'))\
     .limit(4).all()
    
    # Add ratings to popular resources
    popular_with_stats = []
    for resource_id, title, description, category, booking_count in popular_resources:
        stats = get_resource_stats(resource_id)
        popular_with_stats.append({
            'id': resource_id,
            'title': title,
            'description': description,
            'category': category,
            'booking_count': booking_count,
            'rating': stats['rating'],
            'review_count': stats['review_count']
        })
    
    # Calculate stats
    active_bookings_count = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.start_time >= datetime.utcnow(),
        Booking.status == 'approved'
    ).count()
    
    resources_available = len(published_resources)
    
    pending_approvals_count = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status == 'pending'
    ).count()
    
    return render_template('dashboard/index.html',
                         upcoming_bookings=upcoming_bookings,
                         popular_resources=popular_with_stats,
                         active_bookings=active_bookings_count,
                         resources_available=resources_available,
                         pending_approvals=pending_approvals_count)

