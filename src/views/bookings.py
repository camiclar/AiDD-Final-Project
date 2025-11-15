"""Booking routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from src.database import db
from src.models import Booking, Resource, Notification

bookings_bp = Blueprint('bookings', __name__)


def check_booking_conflict(resource_id, start_time, end_time, exclude_booking_id=None):
    """Check if a booking conflicts with existing approved/pending bookings."""
    # Query for overlapping bookings
    # A booking conflicts if:
    # - It starts before another booking ends AND
    # - It ends after another booking starts
    conflict_query = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.status.in_(['approved', 'pending']),
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )
    
    if exclude_booking_id:
        conflict_query = conflict_query.filter(Booking.id != exclude_booking_id)
    
    conflicting_bookings = conflict_query.all()
    return len(conflicting_bookings) > 0, conflicting_bookings


def check_user_booking_conflict(user_id, start_time, end_time, exclude_booking_id=None):
    """Check if a booking conflicts with user's own existing bookings."""
    # Query for overlapping bookings by the same user
    conflict_query = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status.in_(['approved', 'pending']),
        Booking.start_time < end_time,
        Booking.end_time > start_time
    )
    
    if exclude_booking_id:
        conflict_query = conflict_query.filter(Booking.id != exclude_booking_id)
    
    conflicting_bookings = conflict_query.all()
    return len(conflicting_bookings) > 0, conflicting_bookings


def create_notification(user_id, notification_type, title, message, link=None):
    """Helper function to create notifications."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        link=link,
        read=False
    )
    db.session.add(notification)
    return notification


@bookings_bp.route('/')
@login_required
def list_bookings():
    """List all bookings for the current user."""
    # Mark past bookings as completed
    from src.utils import mark_past_bookings_completed
    mark_past_bookings_completed()
    
    now = datetime.utcnow()
    
    # Get all bookings for current user
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_time.desc()).all()
    
    # Categorize bookings
    upcoming = []
    pending = []
    past = []
    
    for booking in all_bookings:
        if booking.status in ['pending']:
            pending.append(booking)
        elif booking.status in ['approved'] and booking.start_time > now:
            upcoming.append(booking)
        elif booking.status in ['approved', 'completed', 'cancelled', 'rejected'] or booking.end_time < now:
            past.append(booking)
    
    return render_template('bookings/list.html',
                         upcoming_bookings=upcoming,
                         pending_bookings=pending,
                         past_bookings=past)


@bookings_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create(resource_id):
    """Create a new booking."""
    from sqlalchemy.orm import joinedload
    resource = Resource.query.options(joinedload(Resource.owner)).get_or_404(resource_id)
    
    # Only allow booking published resources
    if resource.status != 'published':
        flash('This resource is not available for booking.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    if request.method == 'POST':
        # Parse form data
        date_str = request.form.get('date')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        notes = request.form.get('notes', '').strip()
        recurrence = request.form.get('recurrence', 'none')
        
        if not all([date_str, start_time_str, end_time_str]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        try:
            # Combine date and time
            start_datetime = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        # Validate times
        if start_datetime >= end_datetime:
            flash('End time must be after start time.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        if start_datetime < datetime.utcnow():
            flash('Cannot book in the past.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        # Check for resource conflicts (other users' bookings)
        has_resource_conflict, resource_conflicting_bookings = check_booking_conflict(resource_id, start_datetime, end_datetime)
        
        if has_resource_conflict:
            flash('This time slot conflicts with an existing booking. Please choose another time.', 'danger')
            return render_template('bookings/create.html', resource=resource)
        
        # Check for user's own booking conflicts
        # This will be handled via JavaScript modal on the frontend
        # For now, we'll proceed with the booking and let the frontend handle the conflict warning
        
        # Determine booking status based on resource requirements
        if resource.requires_approval:
            booking_status = 'pending'
        else:
            booking_status = 'approved'
        
        # Create booking
        booking = Booking(
            resource_id=resource_id,
            user_id=current_user.id,
            start_time=start_datetime,
            end_time=end_datetime,
            status=booking_status,
            notes=notes,
            recurrence=recurrence
        )
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID
        
        # Create notifications
        if booking_status == 'approved':
            # Notify user of confirmation
            create_notification(
                current_user.id,
                'booking_confirmed',
                'Booking Confirmed',
                f'Your booking for {resource.title} on {start_datetime.strftime("%B %d, %Y")} has been confirmed.',
                url_for('bookings.list_bookings')
            )
            # Notify resource owner
            create_notification(
                resource.owner_id,
                'booking_confirmed',
                'New Booking',
                f'{current_user.name} has booked {resource.title} on {start_datetime.strftime("%B %d, %Y")}.',
                url_for('bookings.list_bookings')
            )
            flash('Booking confirmed!', 'success')
        else:
            # Notify user of pending status
            create_notification(
                current_user.id,
                'booking_pending',
                'Booking Pending Approval',
                f'Your booking request for {resource.title} is pending approval from {resource.owner.name}.',
                url_for('bookings.list_bookings')
            )
            # Notify resource owner
            create_notification(
                resource.owner_id,
                'booking_pending',
                'Booking Request Pending',
                f'{current_user.name} has requested to book {resource.title} on {start_datetime.strftime("%B %d, %Y")}.',
                url_for('bookings.manage')
            )
            flash('Booking request submitted. You will be notified once it\'s approved.', 'info')
        
        db.session.commit()
        
        return redirect(url_for('bookings.list_bookings'))
    
    # Get existing bookings for this resource to show on calendar
    existing_bookings = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.status.in_(['approved', 'pending']),
        Booking.start_time >= datetime.utcnow()
    ).all()
    
    return render_template('bookings/create.html',
                         resource=resource,
                         existing_bookings=existing_bookings)


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    """Cancel a booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check ownership
    if booking.user_id != current_user.id and not current_user.is_admin():
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You do not have permission to cancel this booking.', 'danger')
        return redirect(url_for('bookings.list_bookings'))
    
    # Can only cancel pending or approved bookings
    if booking.status not in ['pending', 'approved']:
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Booking cannot be cancelled'}), 400
        flash('This booking cannot be cancelled.', 'danger')
        return redirect(url_for('bookings.list_bookings'))
    
    booking.status = 'cancelled'
    booking.updated_at = datetime.utcnow()
    
    # Notify resource owner
    resource = Resource.query.get(booking.resource_id)
    create_notification(
        resource.owner_id,
        'booking_cancelled',
        'Booking Cancelled',
        f'{current_user.name} has cancelled their booking for {resource.title}.',
        url_for('bookings.manage')
    )
    
    # Notify user
    create_notification(
        booking.user_id,
        'booking_cancelled',
        'Booking Cancelled',
        f'Your booking for {resource.title} has been cancelled.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('bookings.list_bookings'))


@bookings_bp.route('/manage')
@login_required
def manage():
    """Manage bookings for resources owned by current user (for owners/admins)."""
    # Get resources owned by current user
    owned_resources = Resource.query.filter_by(owner_id=current_user.id).all()
    resource_ids = [r.id for r in owned_resources]
    
    # Get all bookings for owned resources
    if resource_ids:
        all_bookings = Booking.query.filter(Booking.resource_id.in_(resource_ids)).order_by(Booking.start_time.desc()).all()
    else:
        all_bookings = []
    
    # Categorize by status
    pending_bookings = [b for b in all_bookings if b.status == 'pending']
    upcoming_bookings = [b for b in all_bookings if b.status == 'approved' and b.start_time > datetime.utcnow()]
    past_bookings = [b for b in all_bookings if b.status in ['approved', 'completed', 'cancelled', 'rejected'] or b.end_time < datetime.utcnow()]
    
    return render_template('bookings/manage.html',
                         pending_bookings=pending_bookings,
                         upcoming_bookings=upcoming_bookings,
                         past_bookings=past_bookings,
                         owned_resources=owned_resources)


@bookings_bp.route('/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve(booking_id):
    """Approve a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    resource = Resource.query.get(booking.resource_id)
    
    # Check ownership or admin
    if resource.owner_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to approve this booking.', 'danger')
        return redirect(url_for('bookings.manage'))
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('bookings.manage'))
    
    # Check for conflicts before approving
    has_conflict, conflicting_bookings = check_booking_conflict(
        booking.resource_id,
        booking.start_time,
        booking.end_time,
        exclude_booking_id=booking.id
    )
    
    if has_conflict:
        flash('Cannot approve: This booking conflicts with an existing approved booking.', 'danger')
        return redirect(url_for('bookings.manage'))
    
    booking.status = 'approved'
    booking.updated_at = datetime.utcnow()
    
    # Notify user
    create_notification(
        booking.user_id,
        'booking_approved',
        'Booking Approved',
        f'Your booking request for {resource.title} has been approved.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking approved successfully.', 'success')
    return redirect(url_for('bookings.manage'))


@bookings_bp.route('/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject(booking_id):
    """Reject a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    resource = Resource.query.get(booking.resource_id)
    
    # Check ownership or admin
    if resource.owner_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to reject this booking.', 'danger')
        return redirect(url_for('bookings.manage'))
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('bookings.manage'))
    
    booking.status = 'rejected'
    booking.updated_at = datetime.utcnow()
    
    # Notify user
    create_notification(
        booking.user_id,
        'booking_rejected',
        'Booking Rejected',
        f'Your booking request for {resource.title} has been rejected.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking rejected.', 'info')
    return redirect(url_for('bookings.manage'))


@bookings_bp.route('/api/check-conflict', methods=['POST'])
@login_required
def check_conflict_api():
    """API endpoint to check for booking conflicts."""
    data = request.get_json()
    resource_id = data.get('resource_id')
    date_str = data.get('date')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    if not all([resource_id, date_str, start_time_str, end_time_str]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        start_datetime = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid date/time format'}), 400
    
    # Check resource conflicts
    has_resource_conflict, resource_conflicting_bookings = check_booking_conflict(resource_id, start_datetime, end_datetime)
    
    # Check user's own booking conflicts
    has_user_conflict, user_conflicting_bookings = check_user_booking_conflict(current_user.id, start_datetime, end_datetime)
    
    response = {
        'has_resource_conflict': has_resource_conflict,
        'resource_conflicting_count': len(resource_conflicting_bookings),
        'has_user_conflict': has_user_conflict,
        'user_conflicting_bookings': []
    }
    
    if has_user_conflict:
        response['user_conflicting_bookings'] = [{
            'id': b.id,
            'resource_title': b.resource.title,
            'start_time': b.start_time.isoformat(),
            'end_time': b.end_time.isoformat(),
            'location': b.resource.location
        } for b in user_conflicting_bookings]
    
    return jsonify(response)

