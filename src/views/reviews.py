"""Review routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from src.database import db
from src.models import Review, Resource, Booking, Notification

reviews_bp = Blueprint('reviews', __name__)


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


@reviews_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create(resource_id):
    """Create a review for a resource."""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check if user has a completed booking for this resource
    completed_bookings = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.user_id == current_user.id,
        Booking.status == 'completed'
    ).all()
    
    # Also check past approved bookings (treat as completed if end time has passed)
    now = datetime.utcnow()
    past_bookings = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.user_id == current_user.id,
        Booking.status == 'approved',
        Booking.end_time < now
    ).all()
    
    all_eligible_bookings = completed_bookings + past_bookings
    
    if not all_eligible_bookings:
        flash('You can only review resources you have booked and completed.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Check if user already reviewed this resource
    existing_review = Review.query.filter_by(
        resource_id=resource_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this resource.', 'info')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a valid rating (1-5).', 'danger')
            return render_template('reviews/create.html', resource=resource, bookings=all_eligible_bookings)
        
        if not comment:
            flash('Please provide a comment.', 'danger')
            return render_template('reviews/create.html', resource=resource, bookings=all_eligible_bookings)
        
        # Create review
        review = Review(
            resource_id=resource_id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        
        # Notify resource owner
        create_notification(
            resource.owner_id,
            'review_received',
            'New Review',
            f'{current_user.name} left a {rating}-star review for {resource.title}.',
            url_for('resources.detail', resource_id=resource_id)
        )
        
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    return render_template('reviews/create.html', resource=resource, bookings=all_eligible_bookings)


@reviews_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    """Edit an existing review."""
    review = Review.query.get_or_404(review_id)
    
    # Check ownership
    if review.user_id != current_user.id:
        flash('You do not have permission to edit this review.', 'danger')
        return redirect(url_for('resources.detail', resource_id=review.resource_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a valid rating (1-5).', 'danger')
            return render_template('reviews/edit.html', review=review)
        
        if not comment:
            flash('Please provide a comment.', 'danger')
            return render_template('reviews/edit.html', review=review)
        
        review.rating = rating
        review.comment = comment
        
        db.session.commit()
        
        flash('Review updated successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=review.resource_id))
    
    return render_template('reviews/edit.html', review=review)


@reviews_bp.route('/<int:review_id>/delete', methods=['POST'])
@login_required
def delete(review_id):
    """Delete a review."""
    review = Review.query.get_or_404(review_id)
    resource_id = review.resource_id
    
    # Check ownership or admin
    if review.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this review.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('resources.detail', resource_id=resource_id))

