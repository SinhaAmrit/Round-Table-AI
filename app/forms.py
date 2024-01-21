from flask import Blueprint
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, validators, PasswordField, SubmitField, RadioField, SelectField, BooleanField, validators
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from . import db
from .models import Tag

# Create a Blueprint named 'acc'
form = Blueprint('forms', __name__)

#========================================================================================================
                                # Signup Form
#========================================================================================================
class SignupForm(FlaskForm):
    name = StringField('name', [validators.DataRequired()])
    email = StringField('email', [validators.DataRequired()])
    username = StringField('username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6), validators.DataRequired()])

#========================================================================================================
                                # Signin Form
#========================================================================================================
class SigninForm(FlaskForm):
    email = StringField('email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=6), validators.DataRequired()])

#========================================================================================================
                                # Change Password Form
#========================================================================================================
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [validators.DataRequired()])
    new_password = PasswordField('New Password', [validators.DataRequired(), validators.Length(min=8), validators.EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()])
    submit = SubmitField('Change Password')

#========================================================================================================
                                # User Profile Form
#========================================================================================================
class UserProfileForm(FlaskForm):

    full_name = StringField('Full Name', [validators.DataRequired()])
    location = StringField('Location', [validators.DataRequired()])
    about_me = TextAreaField('About Me')

    website_link = StringField('Website Link', [validators.URL()])
    twitter_link = StringField('Twitter Link', [validators.URL()])
    facebook_link = StringField('Facebook Link', [validators.URL()])
    instagram_link = StringField('Instagram Link', [validators.URL()])
    youtube_link = StringField('Youtube Link', [validators.URL()])
    vimeo_link = StringField('Vimeo Link', [validators.URL()])
    github_link = StringField('GitHub Link', [validators.URL()])

    profile_photo = StringField('Profile Photo')

    submit = SubmitField('Save Changes')

#========================================================================================================
                                # Email Settings Form
#========================================================================================================
class EmailSettingsForm(FlaskForm):
    email = StringField('Email Address')
    feature_announcements = RadioField('Features & Announcements', choices=[('Off', 'On')])
    round_table = RadioField('The RoundTable', choices=['Off','On'])
    tips_reminders = RadioField('Tips & Reminders', choices=['Off', 'On'])
    inbox = RadioField('Inbox', choices=['Off', 'Weekly', 'Daily', '3 hrs'])
    community_milestones = RadioField('Community Milestones', choices=['Off', 'On'])
    research = RadioField('Research', choices=['Off', 'On'])
    recommended_jobs = RadioField('Recommended Jobs', choices=['Off', 'On'])
    company_alerts = RadioField('Company Alerts', choices=['Off', 'Weekly'])
    
    submit = SubmitField('Save')

#========================================================================================================
                                # validate_tags function
#========================================================================================================
def validate_tags(form, field):
    # Split the tags using a separator (e.g., comma) and remove any leading/trailing spaces
    tags_data = [tag.strip() for tag in field.data.split(',') if tag.strip()]

    # Create a list to store Tag objects
    tags = []

    # Loop through each tag in the input data
    for tag_name in tags_data:
        # Try to find an existing tag with the same name
        tag = Tag.query.filter_by(title=tag_name).first()

        # If the tag does not exist, create a new one
        if not tag:
            tag = Tag(title=tag_name)
            db.session.add(tag)

        # Add the tag to the list
        tags.append(tag)

    # Set the tags property on the form, which can be used later
    form.tags = tags

#========================================================================================================
                                # Ask-Question Form
#========================================================================================================
class AskQuestionForm(FlaskForm):
    question_title = StringField('Question Title', [validators.DataRequired()])
    tags = StringField('Tags', validators=[validate_tags])
    category = SelectField('Category', choices=[('1', 'JavaScript'), ('2', 'Java'), ('3', 'Python'), ('4', 'C/C++'), ('5', 'JQuery'), ('6', 'SQL'), ('7', 'MongoDB'), ('8', 'PHP')], coerce=int)
    details = TextAreaField('Details', [validators.DataRequired()])
    image = MultipleFileField('Image')
    notified_me = BooleanField('Get notified by email when someone answers this question.', default=True)
    you_agree = BooleanField('By asking your question, you agree to the Privacy Policy.', default=True)