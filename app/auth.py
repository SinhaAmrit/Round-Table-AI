from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)

                                # Sign Up
#========================================================================================================
@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """
    Handle user registration.

    If the request method is POST, extract user data from the form,
    validate, and create a new user account. Redirect to the questions
    page upon successful registration.

    If the request method is GET, render the sign-up page.

    Returns:
        If POST: Redirects to the questions page or current path.
        If GET: Renders the sign-up page.
    """
    print("Entering sign_up function")
    if request.method == 'POST':
        print("Handling POST request")
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        opt_in = 'opt-in' in request.form
        print("data accepted from form successfully")
        if not (name and username and email and password):
            flash('Enter all fields.', category='error')
            print("User already exists!")
            return redirect(url_for('auth.sign_up'))
        else:
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', category='error')
                print("User already exists!")
                return redirect(url_for('auth.sign_up'))
            else:
                # condition passed, create a new user
                hashed_password = generate_password_hash(password, method='sha256')
                new_user = User(email=email, name=name, username=username, password_hash=hashed_password)
                print("User created successfully!")

                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                print('session created successfully!')
                if request.endpoint == '/' or request.endpoint == '/signup':
                    # Redirect to '/questions'
                    return redirect('/questions')
                else:
                    # Redirect to the current path
                    return redirect(request.endpoint)
    print("Handling GET")
    return render_template("auth/signup.html", title="Sign Up")
#========================================================================================================
                                # Log In
#========================================================================================================
@auth.route('/signin', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    If the request method is POST, extract user data from the form,
    check if the user exists, and validate the password. Redirect to
    the questions page upon successful login.

    If the request method is GET, render the sign-in page.

    Returns:
        If POST: Redirects to the questions page or current path.
        If GET: Renders the sign-in page.
    """
    print("Entering sign_in function")
    if request.method == 'POST':
        print("Handling POST request")
        email = request.form.get('email')
        password = request.form.get('password')
        print("data accepted from form successfully")
        # Check if the identifier is an email
        user = User.query.filter_by(email=email).first()
        print("data accepted from form successfully")
        # If the identifier is not an email, check if it's a username
        if not user:
            user = User.query.filter_by(username=email).first()

        if user:
            # User found, check the password
            print("User found")
            if check_password_hash(user.password_hash, password):
                login_user(user, remember=True)

                if request.endpoint == '/' or request.endpoint == '/signin':
                    # Redirect to '/questions'
                    return redirect('/questions')
                else:
                    # Redirect to the current path
                    return redirect(request.endpoint)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            print("User not found")
            flash('User does not exist.', category='error')
    
    print("Handling GET")
    return render_template("auth/signin.html", title="Sign In")
#========================================================================================================
                                # Recover Password
#========================================================================================================
@auth.route("/recover-password", methods=['GET', 'POST'])
def recover_password():
    """
    Render the password recovery page.

    Returns:
        Renders the password recovery page.
    """
    return render_template("auth/recover-password.html", title="Recover Password")
#========================================================================================================
                                # Log Out
#========================================================================================================
@auth.route('/signout')
@login_required
def sign_out():
    """
    Handle user logout.

    Updates the last_seen attribute of the current user, logs out the
    user, and flashes a success message. Redirects to the login page.

    Returns:
        Redirects to the login page.
    """
    current_user.last_seen = datetime.utcnow()
    logout_user()
    flash('Signed out successfully!', category='success')
    return redirect(url_for('auth.login'))
#========================================================================================================
