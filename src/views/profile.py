"""Profile routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from src.database import db
from src.models import User

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/')
@login_required
def index():
    """User profile page."""
    return render_template('profile/index.html', user=current_user)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile."""
    if request.method == 'POST':
        # Update user profile
        current_user.name = request.form.get('name', current_user.name)
        current_user.email = request.form.get('email', current_user.email)
        current_user.department = request.form.get('department', current_user.department)
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            from src.utils import save_profile_picture, delete_profile_picture
            file = request.files['profile_picture']
            if file and file.filename:
                # Delete old profile picture if it exists
                if current_user.profile_image:
                    delete_profile_picture(current_user.profile_image)
                
                image_path = save_profile_picture(file, current_user.id)
                if image_path:
                    current_user.profile_image = image_path
                else:
                    flash('Invalid image file. Please upload a PNG, JPG, JPEG, GIF, or WEBP image (max 5MB).', 'warning')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('profile/edit.html', user=current_user)

