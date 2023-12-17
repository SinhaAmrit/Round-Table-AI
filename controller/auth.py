from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':

        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        opt_in = 'opt-in' in request.form

        conditions = [
            (User.query.filter_by(email=email).first(), 'Email already exists.'),
            (User.query.filter_by(username=username).first(), 'Username already exists.'),
            (len(email) < 4, 'Invalid email address.'),
            (len(password) < 8, 'Password must be at least 8 characters.')]

        for condition, error_message in conditions:
            if condition:
                flash(error_message, category='error')
                return redirect(url_for('auth.sign_up'))

        else:
        # All conditions passed, create a new user
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(email=email, F_name=name, username=username, password=hashed_password, created_at=datetime.utcnow())

        if opt_in:
            current_user.email = new_user.email
            current_user.F_name = new_user.F_name
            current_user.username = new_user.username
            current_user.password_hash = new_user.password_hash

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('views.home'))

    return render_template("auth/signup.html", title="Sign Up")


@auth.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':

        identifier = request.form.get('identifier')  # This can be either email or username
        password = request.form.get('password')

        # Check if the identifier is an email
        user = User.query.filter_by(email=identifier).first()

        # If the identifier is not an email, check if it's a username
        if not user:
            user = User.query.filter_by(username=identifier).first()

        if user:
            # User found, check the password
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template("auth/signin.html", title="Sign In")


@auth.route("/recover-password", methods=['GET', 'POST'])
def recover_password():
    return render_template("auth/recover-password.html", title="Recover Password")


@auth.route('/signout')
@login_required
def sign_out():
    current_user.last_seen = datetime.utcnow()
    logout_user()
    return redirect(url_for('auth.sign_in'))