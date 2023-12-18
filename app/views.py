from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Discussion
from . import db
from datetime import datetime
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

                                # HOME
#========================================================================================================
@views.route('/')
def home():
    is_signed = current_user.is_authenticated
    print(is_signed)
    return render_template('index.html', is_signed=is_signed)
#========================================================================================================
                                # Page Not Found
#========================================================================================================
@views.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page Not Found"), 404
#========================================================================================================
@views.errorhandler(500)
def server_not_found(e):
    return render_template("500.html", title="Server Not Found"),