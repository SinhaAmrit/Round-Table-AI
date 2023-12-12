"""
Defines routes and views for the main part of the application.

This file contains the main Blueprint for routes not related to authentication.
"""

from flask import Blueprint, render_template, redirect
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def index_page():
    return render_template("index.html")

@main.route('/profile')
def profile():
    return 'Profile'

@main.route("/dashboard")
def dashboard_page():
    return render_template("/dashboard.html", title = "Dashboard", greeting = greeting())

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = "404"), 404

def greeting():
    current_time = datetime.now().time()
    if current_time.hour < 12:
        return "Good Morning"
    elif current_time.hour < 16:
        return "Good Afternoon"
    else:
        return "Good Evening"
