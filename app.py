"""Main Flask application for Campus Resource Hub."""
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from src.database import init_db
from src.models import User
import os

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Secret key for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize database
    init_db(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from src.views.auth import auth_bp
    from src.views.resources import resources_bp
    from src.views.bookings import bookings_bp
    from src.views.notifications import notifications_bp
    from src.views.messages import messages_bp
    from src.views.reviews import reviews_bp
    from src.views.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resources_bp, url_prefix='/resources')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    @app.route('/')
    def index():
        """Home page route."""
        return redirect(url_for('resources.browse'))
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

