"""Notification routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from src.database import db
from src.models import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/')
@login_required
def list_notifications():
    """List all notifications for the current user."""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read when viewing
    unread_count = sum(1 for n in notifications if not n.read)
    for notification in notifications:
        if not notification.read:
            notification.read = True
    db.session.commit()
    
    return render_template('notifications/list.html', notifications=notifications)


@notifications_bp.route('/api/unread-count')
@login_required
def unread_count():
    """API endpoint to get unread notification count."""
    count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
    return jsonify({'count': count})


@notifications_bp.route('/api/list')
@login_required
def list_notifications_api():
    """API endpoint to get recent notifications."""
    limit = request.args.get('limit', 5, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'read': n.read,
            'link': n.link,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
    })


@notifications_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read for the current user."""
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    for notification in notifications:
        notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})


@notifications_bp.route('/<int:notification_id>/mark-read', methods=['POST'])
@login_required
def mark_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.read = True
    db.session.commit()
    
    return jsonify({'success': True})

