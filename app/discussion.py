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
        title = request.form.get('title')
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
                                # DASHBOARD
#========================================================================================================
@disc.route("/dashboard")
def dashboard():
    # Sample data, replace it with your actual data retrieval logic
    discussions = get_discussions()
    categories = get_categories()
    tags = get_tags()

    # Retrieve filters from query parameters
    selected_category = request.args.get('category', 'All')
    selected_tag = request.args.get('tag', 'All')

    # Apply filters
    filtered_discussions = filter_discussions(discussions, selected_category, selected_tag)

    return render_template("discussion/dashboard.html", title="Dashboard",
                            discussions=filtered_discussions, categories=categories, tags=tags, 
                            selected_category=selected_category, selected_tag=selected_tag)

# Add helper functions to retrieve data and filter discussions
def get_discussions():
    # Implement your logic to retrieve discussions from the database or any other source
    pass

def get_categories():
    # Implement your logic to retrieve categories from the database or any other source
    pass

def get_tags():
    # Implement your logic to retrieve tags from the database or any other source
    pass

def filter_discussions(discussions, category, tag):
    # Implement your logic to filter discussions based on the selected category and tag
    pass

#========================================================================================================