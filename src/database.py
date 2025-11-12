"""Database configuration and initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()


def init_db(app: Flask):
    """Initialize the database with the Flask app."""
    # Configure database URI
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, '..', 'instance', 'campus_resource_hub.db')
    
    # Ensure instance directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return db

