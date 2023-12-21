from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Discussion, Notification
from werkzeug.utils import secure_filename
from . import db
from datetime import datetime, timedelta
import arrow
from flask_login import login_required, current_user

# Create a Blueprint named 'acc'
acc = Blueprint('account', __name__)

@acc.route('/notifications', methods=['GET', 'POST'])
@login_required
def all_notification():
    if request.method == 'POST':
        pass
    else:
        return render_template("account/notifications.html", 
                                title="Notifications", 
                                notifications=current_user.notifications)


@acc.route('/notifications/<id>', methods=['GET', 'POST'])
@login_required
def notification(id):
    if request.method == 'POST':
        pass
    else:
        current_notifications = Notification.query.filter_by(id=id, user_id=current_user.id).first()

        if current_notifications:
            return render_template("notification/details.html", title="Notifications", notification=current_notifications)


@acc.route('/user-profile/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):

    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect(url_for('views.home'))
    # Convert current_user_created_at to datetime object
    else:
        created_at = datetime.utcfromtimestamp(user.created_at.timestamp())
        # Calculate the time difference
        time_difference = datetime.utcnow() - created_at

        # Get the formatted time difference
        time_ago = format_time_difference(time_difference)

        return render_template("account/user-profile.html", title=user.name, user=user, time_ago=time_ago)

# Define a function to format the time difference
def format_time_difference(time_difference):

    # Calculate years, months, and days
    years = time_difference.days // 365
    months = (time_difference.days % 365) // 30
    days = (time_difference.days % 365) % 30

    if years > 0:
        return f"{years} {'year' if years == 1 else 'years'} ago"
    elif months > 0:
        return f"{months} {'month' if months == 1 else 'months'} ago"
    else:
        return f"{days} {'day' if days == 1 else 'days'} ago"
