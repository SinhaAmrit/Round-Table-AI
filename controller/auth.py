from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    print("Entering sign_up function")
    if request.method == 'POST':
        print("Handling POST request")
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        opt_in = 'opt-in' in request.form
        print("data excepted from form successfully")
        if not (name and username and email and password):
            flash('Enter all fields.', category='error')
            print("User already exist!")
            return redirect(url_for('auth.sign_up'))
        else:
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', category='error')
                print("User already exist!")
                return redirect(url_for('auth.sign_up'))

            else:
                #condition passed, create a new user
                hashed_password = generate_password_hash(password, method='sha256')
                new_user = User(email=email, F_name=name, username=username, password_hash=hashed_password, created_at=datetime.utcnow())
                print("User created successfully!")

                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                print('session created successfully!')
                return redirect(url_for('views.home'))
    print("Handling GET")
    return render_template("auth/signup.html", title="Sign Up" )


@auth.route('/signin', methods=['GET', 'POST'])
def sign_in():
    print("Entering sign_in function")
    if request.method == 'POST':
        print("Handling POST request")
        email = request.form.get('email')
        password = request.form.get('password')
        print("data excepted from form successfully")
        # Check if the identifier is an email
        user = User.query.filter_by(email=email).first()
        print("data excepted from form successfully")
        # If the identifier is not an email, check if it's a username
        if not user:
            user = User.query.filter_by(username=email).first()

        if user:
            # User found, check the password
            print("User found")
            if check_password_hash(user.password_hash, password):
                print("Password matched")
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            print("User not found")
            flash('User does not exist.', category='error')
    print("Handling GET")
    return render_template("auth/signin.html", title="Sign In")


@auth.route("/recover-password", methods=['GET', 'POST'])
def recover_password():
    return render_template("auth/recover-password.html", title="Recover Password")


@auth.route('/signout')
@login_required
def sign_out():
    current_user.last_seen = datetime.utcnow()
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('auth.sign_in'))