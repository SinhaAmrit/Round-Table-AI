from . import db
import uuid
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

                                # USER
#========================================================================================================
class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(16))
    email = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    secret_key = db.Column(db.String(125))
    country = db.Column(db.String(25), default='Country')
    role = db.Column(db.String(25))
    about = db.Column(db.TEXT)
    email_varified_at = db.Column(db.TIMESTAMP)
    update_at = db.Column(db.TIMESTAMP)
    conneted_accounts = db.Column(UUID(as_uuid=True), db.ForeignKey('conn_account.id'))
    mob = db.Column(db.String(10))
    status = db.Column(db.String(16))
    last_seen = db.Column(db.TIMESTAMP)
    score = db.Column(db.Integer, default=0)
    report = db.Column(db.Integer, default=0)
    discussions = db.relationship('Discussion', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user')
    conn_accounts = db.relationship('ConnAccount')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
#========================================================================================================
                                # DISCUSSION
#========================================================================================================
class Discussion(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.TEXT)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    deleted_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    image_id = db.Column(UUID(as_uuid=True), nullable=True, default=None)
    slug = db.Column(db.String(50))
    vote = db.Column(db.Integer, default=0)
    summary = db.Column(db.TEXT)
    archived = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='discussions', overlaps="discussions")
#========================================================================================================
                                # CATEGORY
#========================================================================================================
class Category(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
#========================================================================================================
                                # CONNECTED-ACCOUNT
#========================================================================================================
class ConnAccount(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    github = db.Column(db.String(50))
    stackoverflow = db.Column(db.String(50))
    linkedIn = db.Column(db.String(50))
    facebook = db.Column(db.String(50))
    twitter = db.Column(db.String(50))
    slak = db.Column(db.String(50))
#========================================================================================================
                                # NOTIFICATION
#========================================================================================================
class Notification(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    type = db.Column(db.String(50))
    data = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    read_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    user = db.relationship('User', back_populates='notifications')
#========================================================================================================
                                # REPLY
#========================================================================================================
class Reply(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    discussion_id = db.Column(UUID(as_uuid=True), db.ForeignKey('discussion.id'))
    content = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    deleted_at = db.Column(db.TIMESTAMP)
    vote = db.Column(db.Integer, default=0)
#========================================================================================================
                                # HISTORY
#========================================================================================================
class History(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    discussion_id = db.Column(UUID(as_uuid=True), db.ForeignKey('discussion.id'))
    is_liked = db.Column(db.Boolean)
    reply_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reply.id'))
    visited_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
#========================================================================================================
                                # DISCUSSION-REPLY
#========================================================================================================
class DiscussReply(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    discussion_id = db.Column(UUID(as_uuid=True), db.ForeignKey('discussion.id'))
    reply_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reply.id'))
#========================================================================================================
                                # DISCUSSION-CATEGORY
#========================================================================================================
class DiscussCategory(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    discussion_id = db.Column(UUID(as_uuid=True), db.ForeignKey('discussion.id'))
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('category.id'))
#========================================================================================================