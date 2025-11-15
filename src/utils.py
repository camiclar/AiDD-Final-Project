"""Utility functions for the Campus Resource Hub."""
import os
import uuid
from flask import current_app
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_profile_picture(file, user_id):
    """
    Save a profile picture file and return the relative path.
    
    Args:
        file: The uploaded file from request.files
        user_id: The ID of the user uploading the picture
        
    Returns:
        str: Relative path to the saved image, or None if upload failed
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return None
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pictures')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    filepath = os.path.join(upload_dir, filename)
    
    try:
        # Open and process image
        image = Image.open(file)
        
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to max 400x400 while maintaining aspect ratio
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Save as JPEG for consistency
        if file_ext != 'jpg' and file_ext != 'jpeg':
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(upload_dir, filename)
        
        image.save(filepath, 'JPEG', quality=85, optimize=True)
        
        # Return relative path from static folder
        return f"uploads/profile_pictures/{filename}"
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def delete_profile_picture(image_path):
    """Delete a profile picture file."""
    if not image_path:
        return
    
    try:
        filepath = os.path.join(current_app.root_path, 'static', image_path)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error deleting image: {e}")


def mark_past_bookings_completed():
    """Mark approved bookings that have passed their end time as completed."""
    from datetime import datetime
    from src.database import db
    from src.models import Booking
    
    now = datetime.utcnow()
    
    # Find all approved bookings that have ended
    past_bookings = Booking.query.filter(
        Booking.status == 'approved',
        Booking.end_time < now
    ).all()
    
    # Mark them as completed
    for booking in past_bookings:
        booking.status = 'completed'
    
    if past_bookings:
        db.session.commit()
