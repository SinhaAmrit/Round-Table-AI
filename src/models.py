"""
Defines the data models for the application.

This file contains the User class, representing the user model.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from datetime import datetime
import uuid
from . import db

class User(db.Model):
    """
    User model class representing a user in the application.

    Attributes:
        id (UUID): The unique identifier for the user.
        username (str): The username of the user.
        # ... (Other attributes of the User model)
    """
    
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    F_name = db.Column(db.String(16))
    L_name = db.Column(db.String(16))
    email = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    secret_key = db.Column(db.String(125))
    country = db.Column(db.String(25))
    role = db.Column(db.String(25))
    email_varified_at = db.Column(db.TIMESTAMP)
    update_at = db.Column(db.TIMESTAMP)
    conneted_accounts = db.Column(UUID(as_uuid=True), db.ForeignKey('conn_accounts.id'))
    mob = db.Column(db.String(10))
    status = db.Column(db.String(16))
    last_seen = db.Column(db.TIMESTAMP)
    score = db.Column(db.Integer)
    report = db.Column(db.Integer)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)