"""Admin routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, desc
from datetime import datetime
from src.database import db
from src.decorators import admin_required
from src.models import User, Resource, Booking, Review
from src.views.resources import get_resource_stats

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    # Get statistics
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    # Get category breakdown
    category_counts = db.session.query(
        Resource.category,
        func.count(Resource.id).label('count')
    ).group_by(Resource.category).all()
    
    category_data = []
    category_labels = {
        'study-room': 'Study Rooms',
        'lab-equipment': 'Lab Equipment',
        'event-space': 'Event Spaces',
        'av-equipment': 'AV Equipment',
        'tutoring': 'Tutoring',
        'other': 'Other'
    }
    
    for category, count in category_counts:
        category_data.append({
            'name': category_labels.get(category, category),
            'count': count
        })
    
    # Get recent bookings (last 5)
    recent_bookings = Booking.query.order_by(desc(Booking.created_at)).limit(5).all()
    
    # Get top resources by booking count
    top_resources = db.session.query(
        Resource.id,
        Resource.title,
        func.count(Booking.id).label('booking_count')
    ).join(Booking, Resource.id == Booking.resource_id, isouter=True)\
     .group_by(Resource.id, Resource.title)\
     .order_by(desc('booking_count'))\
     .limit(5).all()
    
    stats = {
        'total_users': total_users,
        'active_resources': active_resources,
        'pending_approvals': pending_approvals,
        'total_bookings': total_bookings
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         category_data=category_data,
                         recent_bookings=recent_bookings,
                         top_resources=top_resources,
                         active_tab='overview')


@admin_bp.route('/users')
@admin_required
def users():
    """User management page."""
    users_list = User.query.order_by(desc(User.created_at)).all()
    
    # Get stats for overview
    total_users = len(users_list)
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         users=users_list,
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         resources=[],
                         reviews=[],
                         pending_bookings=[],
                         active_tab='users')


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Delete user (cascade will handle related records)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} has been deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Update a user's role."""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['student', 'staff', 'admin']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Prevent changing your own role from admin
    if user.id == current_user.id and user.role == 'admin' and new_role != 'admin':
        flash('You cannot change your own role from admin.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'User {user.name}\'s role has been updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/resources')
@admin_required
def resources():
    """Resource management page."""
    resources_list = Resource.query.order_by(desc(Resource.created_at)).all()
    
    # Add stats to each resource
    resources_with_stats = []
    for resource in resources_list:
        stats = get_resource_stats(resource.id)
        resources_with_stats.append({
            'resource': resource,
            'rating': stats['rating'],
            'review_count': stats['review_count'],
            'booking_count': stats['booking_count']
        })
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         resources=resources_with_stats,
                         users=User.query.all(),
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         reviews=[],
                         pending_bookings=[],
                         active_tab='resources')


@admin_bp.route('/resources/<int:resource_id>/archive', methods=['POST'])
@admin_required
def archive_resource(resource_id):
    """Archive a resource."""
    resource = Resource.query.get_or_404(resource_id)
    resource.status = 'archived'
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Resource "{resource.title}" has been archived.', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/resources/<int:resource_id>/publish', methods=['POST'])
@admin_required
def publish_resource(resource_id):
    """Publish a resource."""
    resource = Resource.query.get_or_404(resource_id)
    resource.status = 'published'
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Resource "{resource.title}" has been published.', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/approvals')
@admin_required
def approvals():
    """Pending booking approvals page."""
    pending_bookings = Booking.query.filter_by(status='pending')\
        .order_by(Booking.created_at).all()
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         pending_bookings=pending_bookings,
                         users=User.query.all(),
                         resources=[],
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': len(pending_bookings), 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         reviews=[],
                         active_tab='approvals')


@admin_bp.route('/approvals/<int:booking_id>/approve', methods=['POST'])
@admin_required
def approve_booking(booking_id):
    """Approve a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('admin.approvals'))
    
    booking.status = 'approved'
    booking.updated_at = datetime.utcnow()
    
    # Create notification
    from src.views.bookings import create_notification
    create_notification(
        booking.user_id,
        'booking_confirmed',
        'Booking Approved',
        f'Your booking for {booking.resource.title} has been approved.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking approved successfully.', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/approvals/<int:booking_id>/reject', methods=['POST'])
@admin_required
def reject_booking(booking_id):
    """Reject a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('admin.approvals'))
    
    booking.status = 'rejected'
    booking.updated_at = datetime.utcnow()
    
    # Create notification
    from src.views.bookings import create_notification
    create_notification(
        booking.user_id,
        'booking_rejected',
        'Booking Rejected',
        f'Your booking request for {booking.resource.title} has been rejected.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking rejected.', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/reviews')
@admin_required
def reviews():
    """Review moderation page."""
    reviews_list = Review.query.order_by(desc(Review.created_at)).all()
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         reviews=reviews_list,
                         users=User.query.all(),
                         resources=[],
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         pending_bookings=[],
                         active_tab='reviews')
