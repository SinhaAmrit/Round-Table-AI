from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Discussion, Notification
from werkzeug.utils import secure_filename
from . import db
from datetime import datetime
from flask_login import login_required, current_user


notif = Blueprint('notification', __name__)

@notif.route('/notifications', methods=['GET', 'POST'])
@login_required
def all_notification():
    if request.method == 'POST':
        pass
    else:
        _notifications = Notification.query.filter_by(user_id=current_user.id).all()

        if _notifications:
            return render_template("notification/notifications.html", title="Notifications", all_notifications=_notifications)
        else:
            flash('No Notification Found', 'error')
            return redirect(url_for('notification.all_notification'))

@notif.route('/notifications/<id>', methods=['GET', 'POST'])
@login_required
def notification(id):
    if request.method == 'POST':
        pass
    else:
        current_notifications = Notification.query.filter_by(id=id, user_id=current_user.id).first()

        if current_notifications:
            return render_template("notification/details.html", title="Notifications", notification=current_notifications)
        else:
            flash('No Notification Found', 'error')
            return redirect(url_for('notification.all_notification'))