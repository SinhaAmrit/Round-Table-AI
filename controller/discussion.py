from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Discussion
from werkzeug.utils import secure_filename
from . import db
from datetime import datetime
from flask_login import login_required, current_user


disc = Blueprint('discussion', __name__)

                                # QUESTIONS
#========================================================================================================
@disc.route('/questions', methods=['GET', 'POST'])
def questions():
    print("Entering questions function")
    if request.method == 'POST':
        pass
    else:
        pass
    
    return render_template("discussion/questions.html", title="Questions" )
#========================================================================================================
                                # QUESTION
#========================================================================================================
@disc.route('/question/<slug>', methods=['GET', 'POST'])
def question(discussion_id=''):
    if request.method == 'POST':
        pass
    else:
        discussion = Discussion.query.filter_by(id=discussion_id).first()

        if discussion:
            return render_template("discussion/question.html", title="Questions", discussion=discussion)
        else:
            flash('Discussion not found', 'error')
            return redirect(url_for('discussions.questions'))
#========================================================================================================
                                # ASK-QUESTION
#========================================================================================================
@disc.route('/ask-question', methods=['GET', 'POST'])
@login_required
def ask_question():
    print("Entering new_discussion function")
    if request.method == 'POST':
        title = request.form.get('text')
        details = request.form.get('details')

        if title and details:
            new_discussion = Discussion(title=title, description=details, slug=generate_slug(title))

            db.session.add(new_discussion)
            db.session.commit()

            flash('Question uploaded successfully', category='success')
            return redirect(url_for('discussion.question', slug=new_discussion.slug))
        else:
            flash('Title and description are required', 'error')

    return render_template("discussion/ask-question.html", title="Ask Question")

def generate_slug(title):
    # Convert to lowercase, replace spaces with hyphens, and take the first 50 characters
    slug = secure_filename(title.lower().replace(' ', '-'))[:50]
    return slug
#========================================================================================================
                                # CATEGORY
#========================================================================================================
@disc.route('/category', methods=['GET', 'POST'])
def category():
    print("Entering category function")
    if request.method == 'POST':
        pass
    else:
        pass
    
    return render_template("discussion/category.html", title="Questions" )
#========================================================================================================