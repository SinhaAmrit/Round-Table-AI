from . import db
import uuid
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
    secret_key = db.Column(db.String(125))
    email_varified_at = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    update_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
    details = db.relationship('UserDetail', uselist=False, back_populates='user', cascade="all, delete-orphan")
    conn_accounts = db.relationship('ConnAccount', uselist=False, back_populates='user', cascade="all, delete-orphan")
    email_settings = db.relationship('EmailSetting',uselist=False, back_populates='user')
    privacy_settings = db.relationship('Privacy',uselist=False, back_populates='user')
    questions = db.relationship('Question', back_populates='user')
    answers = db.relationship('Answer', back_populates='user')
    notifications = db.relationship('Notification', back_populates='user')

    def __init__(self, email, name, username, password):
        self.email=email
        self.name=name
        self.username=username
        self.password_hash = generate_password_hash(password, method='sha256')
        self.email_settings = EmailSetting(id=self.id)
        self.privacy_settings = Privacy(id=self.id)
        self.conn_accounts = ConnAccount(id=self.id)
        self.details = UserDetail(id=self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
#========================================================================================================
                                # UserDetail
#========================================================================================================
class UserDetail(db.Model):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    about = db.Column(db.TEXT)
    role = db.Column(db.String(25), default='user')
    country = db.Column(db.String(25))
    status = db.Column(db.String(16), default='Using RoundTable')
    active = db.Column(db.Boolean, default=True)
    reputation = db.Column(db.Integer, default=0)
    gold = db.Column(db.Integer, default=0)
    silver = db.Column(db.Integer, default=0)
    bronze = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.TIMESTAMP)
    report = db.Column(db.Integer, default=0)
    profile_photo = db.Column(db.String(255))
    user = db.relationship('User', back_populates='details')
    def __init__(self, id):
        self.id = id
#========================================================================================================
                                # Privacy
#========================================================================================================
class Privacy(db.Model):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    profile_photo = db.Column(db.String(10), default='Public')
    email = db.Column(db.String(10), default='Only me')
    biography = db.Column(db.String(10), default='Public')
    country = db.Column(db.String(10), default='Public')
    social_links = db.Column(db.String(10), default='Followers')
    user = db.relationship('User', back_populates='privacy_settings')
    def __init__(self, id):
        self.id = id
#========================================================================================================
                                # QUESTION-TAG
#========================================================================================================
class QuestionTagAssociation(db.Model):
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('question.id'), primary_key=True)
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tag.id'), primary_key=True)
#========================================================================================================
                                # QUESTION
#========================================================================================================
class Question(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.TEXT)
    category = db.Column(db.String(50))
    slug = db.Column(db.String(50))
    vote = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    summary = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    deleted_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    archived = db.Column(db.Boolean, default=False)
    is_answered = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='questions')
    images = db.relationship('Image', back_populates='question') 
    answers = db.relationship('Answer', back_populates='question')
    tags = db.relationship('Tag', secondary='question_tag_association', back_populates='questions')
#========================================================================================================
                                # TAGS
#========================================================================================================
class Tag(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    questions = db.relationship('Question', secondary='question_tag_association', back_populates='tags')
#========================================================================================================
                                # IMAGE
#========================================================================================================
class Image(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('question.id'))
    question = db.relationship('Question', back_populates='images')
#========================================================================================================
                                # NOTIFICATION
#========================================================================================================
class Notification(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    type = db.Column(db.String(50))
    data = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    deleted_at = db.Column(db.TIMESTAMP, default=None)
    read_at = db.Column(db.TIMESTAMP, nullable=True, default=None)
    user = db.relationship('User', back_populates='notifications')
#========================================================================================================
                                # ANSWER
#========================================================================================================
class Answer(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('question.id'))
    body = db.Column(db.TEXT)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
    vote = db.Column(db.Integer, default=0)
    question = db.relationship('Question', back_populates='answers')
    user = db.relationship('User', back_populates='answers')
#========================================================================================================
                                # CONNECTED-ACCOUNT
#========================================================================================================
class ConnAccount(db.Model):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    website = db.Column(db.String(50))
    twitter = db.Column(db.String(50))
    facebook = db.Column(db.String(50))
    instagram = db.Column(db.String(50))
    linkedIn = db.Column(db.String(50))
    youtube = db.Column(db.String(50))
    vimeo = db.Column(db.String(50))
    github = db.Column(db.String(50))
    user = db.relationship('User', back_populates='conn_accounts')
#========================================================================================================
                                # HISTORY
#========================================================================================================
class History(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('question.id'))
    is_liked = db.Column(db.Boolean, default=False)
    answer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('answer.id'))
    visited_at = db.Column(db.TIMESTAMP)
    deleted_at = db.Column(db.TIMESTAMP)
#========================================================================================================
                                # EmailSettings
#========================================================================================================
class EmailSetting(db.Model):
    id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(50))
    feature_announcements = db.Column(db.String(3), default='Off')
    round_table = db.Column(db.String(3), default='Off')
    tips_reminders = db.Column(db.String(3), default='On')
    inbox = db.Column(db.String(7), default='Daily')
    community_milestones = db.Column(db.String(3), default='On')
    research = db.Column(db.String(3), default='Off')
    recommended_jobs = db.Column(db.String(3), default='Off')
    company_alerts = db.Column(db.String(6), default='Off')
    user = db.relationship('User', back_populates='email_settings')
    def __init__(self, id):
        self.id = id
#========================================================================================================