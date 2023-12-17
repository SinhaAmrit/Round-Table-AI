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
        return render_template('index.html')
#========================================================================================================