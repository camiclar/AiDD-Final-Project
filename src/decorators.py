"""Decorators for role-based access control."""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def staff_required(f):
    """Decorator to require staff or admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        if not (current_user.is_staff() or current_user.is_admin()):
            flash('You do not have permission to access this page. Staff or Admin access required.', 'danger')
            return redirect(url_for('resources.browse'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('You do not have permission to access this page. Admin access required.', 'danger')
            return redirect(url_for('resources.browse'))
        return f(*args, **kwargs)
    return decorated_function

