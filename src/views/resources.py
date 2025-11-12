"""Resource routes for CRUD operations."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, or_, and_
from datetime import datetime
from src.database import db
from src.models import Resource, ResourceImage, ResourceEquipment, Review, Booking
from src.decorators import staff_required

resources_bp = Blueprint('resources', __name__)


def get_resource_stats(resource_id):
    """Get statistics for a resource (rating, review count, booking count)."""
    reviews = Review.query.filter_by(resource_id=resource_id).all()
    bookings = Booking.query.filter_by(resource_id=resource_id).all()
    
    review_count = len(reviews)
    booking_count = len(bookings)
    
    if review_count > 0:
        rating = sum(r.rating for r in reviews) / review_count
    else:
        rating = 0.0
    
    return {
        'rating': round(rating, 1),
        'review_count': review_count,
        'booking_count': booking_count
    }


@resources_bp.route('/')
@resources_bp.route('/browse')
def browse():
    """Browse all published resources."""
    # Get query parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'recent')
    status_filter = request.args.get('status', 'published')  # For owners/admins
    
    # Base query - only published resources for non-owners
    query = Resource.query
    
    # If user is viewing their own resources or is admin, show all statuses
    if status_filter != 'published' and (current_user.is_authenticated and 
                                         (current_user.is_admin() or status_filter == 'my-resources')):
        if status_filter == 'my-resources':
            query = query.filter_by(owner_id=current_user.id)
        elif status_filter in ['draft', 'archived']:
            query = query.filter_by(status=status_filter, owner_id=current_user.id)
    else:
        query = query.filter_by(status='published')
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Resource.title.ilike(f'%{search}%'),
                Resource.description.ilike(f'%{search}%'),
                Resource.location.ilike(f'%{search}%')
            )
        )
    
    # Category filter
    if category != 'all':
        query = query.filter_by(category=category)
    
    # Get all resources
    resources = query.all()
    
    # Add stats to each resource
    resources_with_stats = []
    for resource in resources:
        stats = get_resource_stats(resource.id)
        resource_dict = {
            'resource': resource,
            'rating': stats['rating'],
            'review_count': stats['review_count'],
            'booking_count': stats['booking_count']
        }
        resources_with_stats.append(resource_dict)
    
    # Sort resources
    if sort_by == 'recent':
        resources_with_stats.sort(key=lambda x: x['resource'].created_at, reverse=True)
    elif sort_by == 'rating':
        resources_with_stats.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'popular':
        resources_with_stats.sort(key=lambda x: x['booking_count'], reverse=True)
    
    categories = [
        {'value': 'all', 'label': 'All Categories'},
        {'value': 'study-room', 'label': 'Study Rooms'},
        {'value': 'lab-equipment', 'label': 'Lab Equipment'},
        {'value': 'event-space', 'label': 'Event Spaces'},
        {'value': 'av-equipment', 'label': 'AV Equipment'},
        {'value': 'tutoring', 'label': 'Tutoring'},
        {'value': 'other', 'label': 'Other'}
    ]
    
    return render_template('resources/browse.html',
                         resources=resources_with_stats,
                         search=search,
                         category=category,
                         sort_by=sort_by,
                         categories=categories)


@resources_bp.route('/<int:resource_id>')
def detail(resource_id):
    """View resource details."""
    resource = Resource.query.get_or_404(resource_id)
    
    # Only show published resources to non-owners, unless user is admin
    if resource.status != 'published':
        if not current_user.is_authenticated or (resource.owner_id != current_user.id and not current_user.is_admin()):
            flash('Resource not found.', 'danger')
            return redirect(url_for('resources.browse'))
    
    stats = get_resource_stats(resource_id)
    images = resource.images.all()
    equipment = [eq.equipment_name for eq in resource.equipment.all()]
    reviews = Review.query.filter_by(resource_id=resource_id).order_by(Review.created_at.desc()).all()
    
    # Check if current user can review (has completed booking and hasn't reviewed yet)
    can_review = False
    user_review = None
    if current_user.is_authenticated:
        # Check for completed or past bookings
        now = datetime.utcnow()
        has_completed_booking = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.user_id == current_user.id,
            or_(
                Booking.status == 'completed',
                and_(Booking.status == 'approved', Booking.end_time < now)
            )
        ).first()
        
        if has_completed_booking:
            user_review = Review.query.filter_by(
                resource_id=resource_id,
                user_id=current_user.id
            ).first()
            can_review = user_review is None
    
    return render_template('resources/detail.html',
                         resource=resource,
                         images=images,
                         equipment=equipment,
                         reviews=reviews,
                         can_review=can_review,
                         user_review=user_review,
                         **stats)


@resources_bp.route('/create', methods=['GET', 'POST'])
@staff_required
def create():
    """Create a new resource."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location')
        capacity = request.form.get('capacity', type=int)
        availability_rules = request.form.get('availability_rules')
        requires_approval = request.form.get('requires_approval') == 'on'
        status = request.form.get('status', 'draft')
        image_urls = request.form.getlist('image_urls[]')
        equipment_list = request.form.get('equipment', '')
        
        if not all([title, description, category, location, capacity]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('resources/create.html')
        
        # Create resource
        resource = Resource(
            title=title,
            description=description,
            category=category,
            location=location,
            capacity=capacity,
            availability_rules=availability_rules,
            requires_approval=requires_approval,
            status=status,
            owner_id=current_user.id
        )
        
        db.session.add(resource)
        db.session.flush()  # Get the resource ID
        
        # Add images
        for image_url in image_urls:
            if image_url.strip():
                img = ResourceImage(resource_id=resource.id, image_url=image_url.strip())
                db.session.add(img)
        
        # Add equipment
        if equipment_list:
            equipment_items = [eq.strip() for eq in equipment_list.split(',') if eq.strip()]
            for eq_name in equipment_items:
                equipment = ResourceEquipment(resource_id=resource.id, equipment_name=eq_name)
                db.session.add(equipment)
        
        db.session.commit()
        
        flash('Resource created successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=resource.id))
    
    categories = [
        {'value': 'study-room', 'label': 'Study Room'},
        {'value': 'lab-equipment', 'label': 'Lab Equipment'},
        {'value': 'event-space', 'label': 'Event Space'},
        {'value': 'av-equipment', 'label': 'AV Equipment'},
        {'value': 'tutoring', 'label': 'Tutoring'},
        {'value': 'other', 'label': 'Other'}
    ]
    
    return render_template('resources/create.html', categories=categories)


@resources_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit(resource_id):
    """Edit an existing resource."""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check ownership (staff can only edit their own, admins can edit any)
    if resource.owner_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this resource.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    if request.method == 'POST':
        resource.title = request.form.get('title')
        resource.description = request.form.get('description')
        resource.category = request.form.get('category')
        resource.location = request.form.get('location')
        resource.capacity = request.form.get('capacity', type=int)
        resource.availability_rules = request.form.get('availability_rules')
        resource.requires_approval = request.form.get('requires_approval') == 'on'
        resource.status = request.form.get('status', 'draft')
        resource.updated_at = datetime.utcnow()
        
        # Update images
        ResourceImage.query.filter_by(resource_id=resource.id).delete()
        image_urls = request.form.getlist('image_urls[]')
        for image_url in image_urls:
            if image_url.strip():
                img = ResourceImage(resource_id=resource.id, image_url=image_url.strip())
                db.session.add(img)
        
        # Update equipment
        ResourceEquipment.query.filter_by(resource_id=resource.id).delete()
        equipment_list = request.form.get('equipment', '')
        if equipment_list:
            equipment_items = [eq.strip() for eq in equipment_list.split(',') if eq.strip()]
            for eq_name in equipment_items:
                equipment = ResourceEquipment(resource_id=resource.id, equipment_name=eq_name)
                db.session.add(equipment)
        
        db.session.commit()
        
        flash('Resource updated successfully!', 'success')
        return redirect(url_for('resources.detail', resource_id=resource.id))
    
    categories = [
        {'value': 'study-room', 'label': 'Study Room'},
        {'value': 'lab-equipment', 'label': 'Lab Equipment'},
        {'value': 'event-space', 'label': 'Event Space'},
        {'value': 'av-equipment', 'label': 'AV Equipment'},
        {'value': 'tutoring', 'label': 'Tutoring'},
        {'value': 'other', 'label': 'Other'}
    ]
    
    images = [img.image_url for img in resource.images.all()]
    equipment = ', '.join([eq.equipment_name for eq in resource.equipment.all()])
    
    return render_template('resources/edit.html',
                         resource=resource,
                         categories=categories,
                         images=images,
                         equipment=equipment)


@resources_bp.route('/<int:resource_id>/delete', methods=['POST'])
@staff_required
def delete(resource_id):
    """Delete a resource."""
    resource = Resource.query.get_or_404(resource_id)
    
    # Check ownership (staff can only delete their own, admins can delete any)
    if resource.owner_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this resource.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    db.session.delete(resource)
    db.session.commit()
    
    flash('Resource deleted successfully.', 'success')
    return redirect(url_for('resources.browse'))


@resources_bp.route('/my-resources')
@staff_required
def my_resources():
    """View resources owned by the current user (staff and admins only)."""
    resources = Resource.query.filter_by(owner_id=current_user.id).all()
    
    resources_with_stats = []
    for resource in resources:
        stats = get_resource_stats(resource.id)
        resource_dict = {
            'resource': resource,
            'rating': stats['rating'],
            'review_count': stats['review_count'],
            'booking_count': stats['booking_count']
        }
        resources_with_stats.append(resource_dict)
    
    return render_template('resources/my_resources.html', resources=resources_with_stats)

