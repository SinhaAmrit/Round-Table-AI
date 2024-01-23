from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Question, Image
from .forms import AskQuestionForm
import os
from werkzeug.utils import secure_filename


disc = Blueprint('discussion', __name__)


#========================================================================================================
                                # QUESTION
#========================================================================================================
@disc.route('/question/<slug>', methods=['GET'])
def question(slug):
        question = Question.query.filter_by(slug=slug).first()

        if question:
            return render_template("discussion/question.html", title="Questions", question=question)
        else:
            flash('Discussion not found', 'error')
            return redirect(url_for('discussion.dashboard'))
#========================================================================================================
                                # ASK-QUESTION
#========================================================================================================

@disc.route('/ask-question', methods=['GET', 'POST'])
@login_required
def ask_question():
    form = AskQuestionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # Process the form data
            question = Question(
                title=form.question_title.data,
                tags=form.tags,
                category=form.category.data,
                description=form.details.data,
                slug=generate_slug(form.question_title.data),
                user=current_user
            )
            notified_me=form.notified_me.data
            you_agree=form.you_agree.data

            # Save the image if provided
            if form.image.data:
                # Create the directory structure if it doesn't exist
                upload_folder = os.path.join(disc.config['UPLOAD_FOLDER'], 'question', 'image', str(question.id))
                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(form.image.data.filename)
                image_path = os.path.join(upload_folder, filename)
                form.image.data.save(image_path)

                # Assuming you have an Image model with an id field
                image = Image(filename=filename)
                question.images.append(image)


            # Add the question to the database
            db.session.add(question)
            db.session.commit()

            flash('Question uploaded successfully', category='success')
            return redirect(url_for('discussion.question', slug=question.slug))
        else:
            flash('Error submitting the question. Please check your inputs.', 'error')

    return render_template("discussion/ask-question.html", title="Ask Question", form=form)


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
@disc.route("/")
@disc.route("/dashboard")
def dashboard():
    # # Sample data, replace it with your actual data retrieval logic
    # discussions = get_discussions()
    # categories = get_categories()
    # tags = get_tags()

    # # Retrieve filters from query parameters
    # selected_category = request.args.get('category', 'All')
    # selected_tag = request.args.get('tag', 'All')

    # # Apply filters
    # filtered_discussions = filter_discussions(discussions, selected_category, selected_tag)

    return render_template("discussion/dashboard.html", title="Dashboard")
    #                         discussions=filtered_discussions, categories=categories, tags=tags, 
    #                         selected_category=selected_category, selected_tag=selected_tag)

# Add helper functions to retrieve data and filter discussions
def get_questions():
    # Implement your logic to retrieve discussions from the database or any other source
    pass

#========================================================================================================