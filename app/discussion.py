from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
from .auth import unauthorized_callback
from .models import Question, Answer, Image
from .forms import AskQuestionForm, AnswerForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import humanize

disc = Blueprint('discussion', __name__)


#========================================================================================================
                                # QUESTION
#========================================================================================================
@disc.route('/question/<slug>', methods=['GET', 'POST'])
def question(slug):
        if slug:
            que = Question.query.filter_by(slug=slug).first()
            
            if que and not que.deleted_at:
                if not que.user.deleted_at:
                    username = que.user.username
                else:
                    username = "user15319675"
                que.views += 1
                db.session.commit()
                question = {'title' : que.title,
                        'body': que.body,
                        'category': que.category,
                        'slug': que.slug,
                        'views': que.views,
                        'vote': que.vote,
                        'archived': que.archived,
                        'asked_ago': humanize.naturaltime(datetime.utcnow() - que.created_at),
                        'edited' : que.updated_at,
                        'archived': que.archived,
                        'tags':que.tags,
                        'username': username,
                        'name': que.user.name,
                        'reputation': que.user.details.reputation,
                        'gold':que.user.details.gold,
                        'silver':que.user.details.silver,
                        'bronze':que.user.details.bronze
                    }
                
                answer_form = AnswerForm()
                if request.method == 'POST' and answer_form.validate_on_submit():
                    if current_user.is_authenticated:
                        ans = Answer(
                            body = answer_form.details.data,
                            user = current_user,
                            question = que
                        )
                        db.session.add(ans)
                        db.session.commit()
                        answer_form.details.data = ''
                        flash('Answer uploaded successfully!', category='success')
                
                    else:
                        session['slug'] = slug
                        return redirect(url_for('auth.sign_in', next=request.endpoint))
                
                answers = []
                for ans in que.answers:
                    if ans.user.deleted_at:
                        username = ans.user.username
                    else:
                        username = "user15319675"

                    answers.append({
                        'username': username,
                        'name': ans.user.name,
                        'reputation': ans.user.details.reputation,
                        'gold': ans.user.details.gold,
                        'silver': ans.user.details.silver,
                        'bronze': ans.user.details.bronze,
                        'body': ans.body,
                        'ans_ago': humanize.naturaltime(datetime.utcnow() - ans.created_at),
                        'edited': ans.updated_at,
                        'vote': ans.vote
                    })
                
                answers = sorted(answers, key=lambda x: x['vote'], reverse=True)
                

                return render_template("discussion/question.html", question=question, answers=answers,answer_form=answer_form, title="Questions")
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
                body=form.details.data,
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

            flash('Question uploaded successfully!', category='success')
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
def dash():
    return redirect(url_for('discussion.dashboard'))
@disc.route("/dashboard", methods=['GET', 'POST'])
@disc.route("/dashboard/page<int:page>", methods=['GET', 'POST'])
def dashboard(page=1):
    per_page = 15
    category = 'newest'
    queried_questions, total_questions = question_per_catogery(page, category, per_page)
    
    # Calculate total pages for pagination
    total_pages = (max(1, total_questions) + per_page-1) // per_page

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.dashboard'))
    elif page > total_pages:
        return redirect(url_for('discussion.dashboard', page=total_pages))
    
    questions = []
    # Prepare questions data for rendering
    for question in queried_questions:
        if not question.user.deleted_at:
            username = question.user.username
        else:
            username = "user15319675"
        
        questions.append({
            'title': question.title,
            'vote': question.vote,
            'answers': len(question.answers),
            'is_answered': question.is_answered,
            'created_ago': humanize.naturaltime(datetime.utcnow() - question.created_at),
            'username': username,
            'tags': question.tags,
            'summary': question.summary,
            'slug': question.slug
            })

    return render_template("discussion/dashboard.html",
                            title="Dashboard",
                            questions=questions,
                            page=page,
                            total_pages=total_pages,
                            total_questions=total_questions)
#========================================================================================================
def question_per_catogery(page, category='newest', per_page=15):
    if category == 'newest':
        questions = Question.query.filter(Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.deleted_at == None).count()
    elif category == 'featured':
        questions = Question.query.filter(Question.bountied != None, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.bountied != None, Question.deleted_at == None).count()
    elif category == 'frequent':
        questions = Question.query.filter(Question.deleted_at == None).order_by(Question.views.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.deleted_at == None).count()
    elif category == 'active':
        questions = Question.query.filter(Question.active == True, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.active == True, Question.deleted_at == None).count()
    elif category == 'unanswered':
        questions = Question.query.filter(Question.answers == None, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.answers == None, Question.deleted_at == None).count()
    
    return questions, total_questions
#========================================================================================================
@disc.route('/answer', methods=['GET', 'POST'])
@login_required
def answer():
    pass