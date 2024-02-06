from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from .forms import SignupForm, SigninForm
from . import db, login_manager
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
import re

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)

#========================================================================================================
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
    if current_user.is_authenticated:
        return redirect(redirect(url_for('views.home')))
    next_url = request.args.get('next')
    form = SignupForm()
    if request.method == 'GET' and next_url:
        session['next_url'] = next_url

    if request.method == 'POST':

        if not form.validate_on_submit():
            flash('Enter all fields.', category='error')

        else:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already exists!', category='error')
            elif User.query.filter_by(username=form.username.data).first():
                flash("Username already exists!", category='error')
            elif not is_valid_username(form.username.data)[0]:
                flash(is_valid_username(form.username.data)[1], category='error')
            elif not is_strong_password(form.password.data)[0]:
                flash(is_strong_password(form.password.data)[1], category='error')

            else:
                # condition passed, create a new user
                new_user = User(
                    email=form.email.data, 
                    name=form.name.data, 
                    username=form.username.data, 
                    password=form.password.data)
                
                try:
                    db.session.add(new_user)
                    db.session.commit()

                    login_user(new_user, remember=False)
                    flash('Account created!', category='success')
                    next_url = session.pop('next_url', None)
                    if not next_url:
                        return redirect('/dashboard')
                    else:
                        return redirect(url_for(next_url))
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"An error occurred: {e}")
                    flash("Error during user registration", category="error")
                    
        return redirect(url_for('auth.sign_up'))
    return render_template("auth/signup.html", title="Sign Up", form=form)
#========================================================================================================
def is_valid_username(username):
    """
    Test if a username is valid.

    Username criteria:
    - Alphanumeric characters and hyphens
    - Between 1 and 39 characters long

    Args:
        username (str): The username to be tested.

    Returns:
        tuple: A tuple containing a boolean indicating if the username is valid,
                and a message indicating any errors if the username is not valid.
    """
    # Check for valid characters (alphanumeric and hyphens)
    if not re.match("^[a-zA-Z0-9-]+$", username):
        return False, "Username can only contain alphanumeric characters and hyphens."

    # Check length
    if not (1 <= len(username) <= 39):
        return False, "Username must be between 1 and 39 characters long."

    # If all conditions are met
    return True, "Username is valid."
#========================================================================================================
def is_strong_password(password):
    """
    Test if a password is strong based on specified conditions.

    Conditions:
    - At least 8 characters long
    - Contains at least 1 special character (!@#$%^&*()-_=+[]{}|;:'",.<>?/)
    - Contains at least 1 digit
    - Contains at least 1 uppercase character
    - Contains at least 1 lowercase character

    Args:
        password (str): The password to be tested.

    Returns:
        tuple: A tuple containing a boolean indicating if the password is strong,
                and a message indicating any errors if the password is not strong.
    """
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Check for at least 1 special character
    if not re.search(r'[!@#$%^&*()-_=+[\]{}|;:\'",.<>?/]', password):
        return False, "Password must contain at least 1 special character."

    # Check for at least 1 digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least 1 digit."

    # Check for at least 1 uppercase character
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least 1 uppercase character."

    # Check for at least 1 lowercase character
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least 1 lowercase character."

    # If all conditions are met
    return True, "Password is strong."
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
    if current_user.is_authenticated:
        return redirect(redirect(url_for('discussion.dashboard')))
    
    next_url = request.args.get('next')

    if request.method == 'GET' and next_url:
        session['next_url'] = next_url

    form = SigninForm()
    is_error_occur = False

    if request.method == 'POST':

        # Check if the form is valid
        if not form.validate_on_submit():
            flash('Enter email and password, try again.', category='error')
            is_error_occur = True
        else:
            user = User.query.filter_by(email=form.email.data).first()

            if user and not user.deleted_at:
            # User found, check the password
                print("User found")
                if user.check_password(form.password.data):
                    login_user(user)
                    user.details.active = True
                    db.session.commit()
                    next_url = session.pop('next_url', None)
                    if not next_url:
                        return redirect('/dashboard')
                    else:
                        return redirect(url_for(next_url))
                
                else:
                    flash('Incorrect password, try again.', category='error')
                    is_error_occur = True
            else:
                print("User not found")
                flash('User does not exist.', category='error')
                is_error_occur = True

    if is_error_occur:
        return redirect(url_for('auth.login'))
    
    print("Handling GET")
    return render_template("auth/signin.html", title="Sign In", form=form)
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
    if request.method == 'POST':
        pass
        

    return render_template("auth/recover-password.html", title="Recover Password")
#========================================================================================================
                                # Sign Out
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
    try:
        # Update last_seen and set active to False
        current_user.details.last_seen = datetime.utcnow()
        current_user.details.active = False
        is_deleted = current_user.deleted_at
        # Commit the changes
        db.session.commit()

        # Logout the user
        logout_user()
        if not is_deleted:
            flash('You have been logged out successfully!', 'success')

        return redirect(url_for('views.home'))

    except Exception as e:
        # If an error occurs, rollback changes and log the error
        db.session.rollback()
        flash(f'Error during logout: {str(e)}', 'error')
        return redirect(url_for('views.home'))
#========================================================================================================
                                # Unauthorized-Callback
#========================================================================================================
@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    Custom unauthorized callback function for Flask-Login.

    This function is triggered when a user attempts to access a protected route without proper authentication.
    It redirects the user to the login page while providing a message prompting the user to sign in first.

    Returns:
        Flask response: Redirects the user to the login page with a flash message.

    Notes:
        This function is designed to work with Flask-Login's unauthorized_handler decorator.
        It uses Flask's flash messaging to display an error message.
        The 'auth.login' endpoint is expected to handle user login functionality.
        The 'next' parameter is used to redirect the user back to the originally requested page after successful login.
    """
    if request.endpoint == 'auth.sign_out':
        return redirect(url_for('views.home'))
    flash('Sign in first to access this page!', category='error')
    # Redirects the user to the login page while preserving the originally requested page (if available)
    return redirect(url_for('auth.login', next=request.endpoint))
#========================================================================================================