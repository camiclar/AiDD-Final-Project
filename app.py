"""Main Flask application for Campus Resource Hub."""
from flask import Flask
from src.database import init_db
import os

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Secret key for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize database
    init_db(app)
    
    # Register blueprints (will be added as we create routes)
    # from src.views.auth import auth_bp
    # app.register_blueprint(auth_bp)
    
    @app.route('/')
    def index():
        """Home page route."""
        return '<h1>Campus Resource Hub</h1><p>Application is running!</p>'
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

