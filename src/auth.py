"""
Defines routes and views for user authentication.

This file contains the Blueprint for authentication-related routes.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    """
    Handle user signup.

    Returns:
        str: Rendered HTML for the signup page.
    """
    if request.method == 'POST':
        # code to validate and add user to database goes here
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists!')
            return redirect(url_for('auth.signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, password=generate_password_hash(password))
        flash('You are new')
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.signin'))

    return render_template("auth/signup.html", title="Sign Up")

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    """
    Handle user login.

    Returns:
        str: Rendered HTML for the login page.
    """
    if request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.signin')) # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user)
        return redirect(url_for('main.profile'))
        
    return render_template("auth/signin.html", title="Sign In")

@auth.route('/logout')
@login_required
def logout(user):
    """
    Handle user logout.

    Returns:
        str: Redirects to the index page after successful logout.
    """
    # Implement session/logout handling
    logout_user(user)
    flash('Logout successful.')
    return redirect(url_for('main.index'))
