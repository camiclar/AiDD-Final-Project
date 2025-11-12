"""Message routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from datetime import datetime
from src.database import db
from src.models import Message, Resource, Booking, Notification

messages_bp = Blueprint('messages', __name__)


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


@messages_bp.route('/')
@login_required
def list_messages():
    """List all message threads for the current user."""
    # Get all threads where user is sender or receiver
    # Group by thread_id and get the most recent message for each thread
    threads = {}
    
    # Get all messages involving current user
    all_messages = Message.query.filter(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).all()
    
    # Group by thread_id
    for message in all_messages:
        thread_id = message.thread_id or f"resource_{message.receiver_id if message.sender_id == current_user.id else message.sender_id}"
        
        if thread_id not in threads:
            threads[thread_id] = {
                'thread_id': thread_id,
                'last_message': message,
                'unread_count': 0,
                'other_user': None,
                'resource': None,
                'booking': None
            }
        
        # Count unread messages
        if not message.read and message.receiver_id == current_user.id:
            threads[thread_id]['unread_count'] += 1
        
        # Get other user info
        if message.sender_id == current_user.id:
            other_user_id = message.receiver_id
        else:
            other_user_id = message.sender_id
        
        if not threads[thread_id]['other_user']:
            from src.models import User
            other_user = User.query.get(other_user_id)
            threads[thread_id]['other_user'] = other_user
        
        # Try to get resource/booking info from thread_id
        if thread_id.startswith('resource_'):
            try:
                resource_id = int(thread_id.split('_')[1])
                resource = Resource.query.get(resource_id)
                threads[thread_id]['resource'] = resource
            except (ValueError, IndexError):
                pass
        elif thread_id.startswith('booking_'):
            try:
                booking_id = int(thread_id.split('_')[1])
                booking = Booking.query.get(booking_id)
                threads[thread_id]['booking'] = booking
                if booking:
                    threads[thread_id]['resource'] = booking.resource
            except (ValueError, IndexError):
                pass
    
    # Sort by last message time
    thread_list = sorted(threads.values(), key=lambda x: x['last_message'].created_at, reverse=True)
    
    return render_template('messages/list.html', threads=thread_list)


@messages_bp.route('/thread/<thread_id>')
@login_required
def view_thread(thread_id):
    """View messages in a specific thread."""
    # Get all messages in this thread
    messages = Message.query.filter_by(thread_id=thread_id).order_by(Message.created_at.asc()).all()
    
    # Get resource/booking info from thread_id to determine other user if no messages yet
    resource = None
    booking = None
    other_user = None
    
    if thread_id.startswith('resource_'):
        try:
            resource_id = int(thread_id.split('_')[1])
            resource = Resource.query.get(resource_id)
            if resource:
                from src.models import User
                other_user = User.query.get(resource.owner_id)
                # Verify user is not the owner
                if resource.owner_id == current_user.id:
                    flash('You cannot message yourself.', 'danger')
                    return redirect(url_for('resources.detail', resource_id=resource_id))
        except (ValueError, IndexError):
            pass
    elif thread_id.startswith('booking_'):
        try:
            booking_id = int(thread_id.split('_')[1])
            booking = Booking.query.get(booking_id)
            if booking:
                resource = booking.resource
                from src.models import User
                # Other user is the opposite party
                if booking.user_id == current_user.id:
                    other_user = User.query.get(booking.resource.owner_id)
                else:
                    other_user = User.query.get(booking.user_id)
        except (ValueError, IndexError):
            pass
    
    # If we have messages, verify user is part of thread and get other user
    if messages:
        first_message = messages[0]
        if first_message.sender_id != current_user.id and first_message.receiver_id != current_user.id:
            flash('You do not have permission to view this thread.', 'danger')
            return redirect(url_for('messages.list_messages'))
        
        # Mark messages as read
        for message in messages:
            if message.receiver_id == current_user.id and not message.read:
                message.read = True
        db.session.commit()
        
        # Get other user from messages
        if messages[0].sender_id == current_user.id:
            other_user_id = messages[0].receiver_id
        else:
            other_user_id = messages[0].sender_id
        
        from src.models import User
        other_user = User.query.get(other_user_id)
    
    if not other_user:
        flash('User not found.', 'danger')
        return redirect(url_for('messages.list_messages'))
    
    return render_template('messages/thread.html',
                         messages=messages,
                         thread_id=thread_id,
                         other_user=other_user,
                         resource=resource,
                         booking=booking)


@messages_bp.route('/start/<int:resource_id>')
@login_required
def start_conversation(resource_id):
    """Start a conversation with a resource owner."""
    resource = Resource.query.get_or_404(resource_id)
    
    # Don't allow messaging yourself
    if resource.owner_id == current_user.id:
        flash('You cannot message yourself.', 'danger')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    # Create thread_id
    thread_id = f"resource_{resource_id}"
    
    # Check if thread already exists
    existing_messages = Message.query.filter_by(thread_id=thread_id).first()
    
    if existing_messages:
        return redirect(url_for('messages.view_thread', thread_id=thread_id))
    
    # Redirect to thread (will create first message when sent)
    return redirect(url_for('messages.view_thread', thread_id=thread_id))


@messages_bp.route('/thread/<thread_id>/send', methods=['POST'])
@login_required
def send_message(thread_id):
    """Send a message in a thread."""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('messages.view_thread', thread_id=thread_id))
    
    # Determine receiver based on thread
    receiver_id = None
    if thread_id.startswith('resource_'):
        resource_id = int(thread_id.split('_')[1])
        resource = Resource.query.get(resource_id)
        if not resource:
            flash('Resource not found.', 'danger')
            return redirect(url_for('messages.list_messages'))
        
        # Receiver is the resource owner
        receiver_id = resource.owner_id
        
        # Verify user is not the owner
        if receiver_id == current_user.id:
            flash('You cannot message yourself.', 'danger')
            return redirect(url_for('resources.detail', resource_id=resource_id))
    
    elif thread_id.startswith('booking_'):
        booking_id = int(thread_id.split('_')[1])
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('messages.list_messages'))
        
        # Receiver is the other party (owner if user is requester, requester if user is owner)
        if booking.user_id == current_user.id:
            receiver_id = booking.resource.owner_id
        else:
            receiver_id = booking.user_id
    
    else:
        # Try to get from existing messages
        existing_message = Message.query.filter_by(thread_id=thread_id).first()
        if existing_message:
            if existing_message.sender_id == current_user.id:
                receiver_id = existing_message.receiver_id
            else:
                receiver_id = existing_message.sender_id
        else:
            flash('Invalid thread.', 'danger')
            return redirect(url_for('messages.list_messages'))
    
    # Create message
    message = Message(
        thread_id=thread_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        read=False
    )
    
    db.session.add(message)
    
    # Create notification for receiver
    create_notification(
        receiver_id,
        'new_message',
        'New Message',
        f'{current_user.name} sent you a message.',
        url_for('messages.view_thread', thread_id=thread_id)
    )
    
    db.session.commit()
    
    flash('Message sent!', 'success')
    return redirect(url_for('messages.view_thread', thread_id=thread_id))

