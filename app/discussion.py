from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from sqlalchemy import func
from . import db
from .models import User, UserDetail, Question, Answer, Image, Tag, QuestionTagAssociation
from .forms import AskQuestionForm, AnswerForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import random
import humanize

disc = Blueprint('discussion', __name__)

#========================================================================================================
def get_questions(queried_questions):
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
            'is_answered': question.is_solved,
            'created_ago': humanize.naturaltime(datetime.utcnow() - question.created_at),
            'username': username,
            'tags': question.tags,
            'summary': question.summary,
            'slug': question.slug
            })
    return questions
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
                

                return render_template("discussion/question.html", 
                                    question=question, 
                                    answers=answers,
                                    answer_form=answer_form, 
                                    title="Questions", 
                                    achievements=get_achievement(),
                                    trending_questions=trending_questions(),
                                    tag_count=tag_count())
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
#========================================================================================================
def generate_slug(title):
    # Convert to lowercase, replace spaces with hyphens, and take the first 50 characters
    slug = secure_filename(title.lower().replace(' ', '-'))[:50]
    return slug
#========================================================================================================
                                # CATEGORY
#========================================================================================================
@disc.route('/category/<category>/all', methods=['GET', 'POST'])
@disc.route('/category/<category>/all-page<int:page>', methods=['GET', 'POST'])
def all_category(category, page=1):
    per_page = 15
    all, total_all = all_catogery_question(page, category, per_page)
    unanswered, total_unanswered = unanswered_category_question(1, category, per_page)
    unsolved, total_unsolved = unsolved_catogery_questions(1, category, per_page)
    # Calculate total pages for pagination
    total_pages = {'all': (max(1, total_all) + per_page-1) // per_page,
                   'unanswered': (max(1, total_unanswered) + per_page-1) // per_page,
                   'unsolved': (max(1, total_unsolved) + per_page-1) // per_page}
    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.all_category', category=category))
    elif page > total_pages['all']:
        return redirect(url_for('discussion.all_category', category=category, page=total_pages['all']))
    
    questions = {'all': get_questions(all),
                'unanswered': get_questions(unanswered),
                'unsolved': get_questions(unsolved)}

    return render_template("discussion/category.html", 
                            title="Category",
                            questions=questions,
                            category=category,
                            active={'all': 'show active', 'unanswered': '', 'unsolved': ''},
                            page={'all': page, 'unanswered': 1, 'unsolved': 1},
                            total_pages=total_pages,
                            total_questions={'all': total_all, 'unanswered': total_unanswered, 'unsolved': total_unsolved},
                            achievements=get_achievement(),
                            trending_questions= trending_questions(),
                            tag_count=tag_count())
#========================================================================================================
                                # CATEGORY
#========================================================================================================
@disc.route('/category/<category>/unanswered', methods=['GET', 'POST'])
@disc.route('/category/<category>/unanswered-page<int:page>', methods=['GET', 'POST'])
def unanswered_category(category, page=1):
    per_page = 15
    all, total_all = all_catogery_question(1, category, per_page)
    unanswered, total_unanswered = unanswered_category_question(page, category, per_page)
    unsolved, total_unsolved = unsolved_catogery_questions(1, category, per_page)
    # Calculate total pages for pagination
    total_pages = {'all': (max(1, total_all) + per_page-1) // per_page,
                   'unanswered': (max(1, total_unanswered) + per_page-1) // per_page,
                   'unsolved': (max(1, total_unsolved) + per_page-1) // per_page}

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.unanswered_category', category=category))
    elif page > total_pages['unanswered']:
        return redirect(url_for('discussion.unanswered_category', category=category, page=total_pages['unanswered']))

    questions = {'all': get_questions(all),
                'unanswered': get_questions(unanswered),
                'unsolved': get_questions(unsolved)}

    return render_template("discussion/category.html", 
                            title="Category",
                            questions=questions,
                            category=category,
                            active={'all': '', 'unanswered': 'show active', 'unsolved': ''},
                            page={'all': 1, 'unanswered': page, 'unsolved': 1},
                            total_pages=total_pages,
                            total_questions={'all': total_all, 'unanswered': total_unanswered, 'unsolved': total_unsolved},
                            achievements=get_achievement(),
                            trending_questions= trending_questions(),
                            tag_count=tag_count())
#========================================================================================================
                                # CATEGORY
#========================================================================================================
@disc.route('/category/<category>/unsolved', methods=['GET', 'POST'])
@disc.route('/category/<category>/unsolved-page<int:page>', methods=['GET', 'POST'])
def unsolved_category(category, page=1):
    per_page = 15
    all, total_all = all_catogery_question(1, category, per_page)
    unanswered, total_unanswered = unanswered_category_question(1, category, per_page)
    unsolved, total_unsolved = unsolved_catogery_questions(page, category, per_page)
    # Calculate total pages for pagination
    total_pages = {'all': (max(1, total_all) + per_page-1) // per_page,
                   'unanswered': (max(1, total_unanswered) + per_page-1) // per_page,
                   'unsolved': (max(1, total_unsolved) + per_page-1) // per_page}

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.unsolved_category', category=category))
    elif page > total_pages['unsolved']:
        return redirect(url_for('discussion.unsolved_category', category=category, page=total_pages['unsolved']))

    questions = {'all': get_questions(all),
                'unanswered': get_questions(unanswered),
                'unsolved': get_questions(unsolved)}

    return render_template("discussion/category.html", 
                            title="Category",
                            questions=questions,
                            category=category,
                            active={'all': '', 'unanswered': '', 'unsolved': 'show active'},
                            page={'all': 1, 'unanswered': 1, 'unsolved': page},
                            total_pages=total_pages,
                            total_questions={'all': total_all, 'unanswered': total_unanswered, 'unsolved': total_unsolved},
                            achievements=get_achievement(),
                            trending_questions= trending_questions(),
                            tag_count=tag_count())
#========================================================================================================
def all_catogery_question(page, category, per_page):
    if category.lower() == 'random':
        if 'random_question_list' not in session:
            questions = Question.query.filter(Question.deleted_at == None).all()
            random.shuffle(questions)
            session['random_question_list'] = questions
        total_questions = Question.query.filter(Question.deleted_at == None).count()
        questions = session.get('random_question_list', [])
        questions = questions[(page - 1) * per_page: page * per_page]
        
    elif category.lower() == 'unanswered':
        questions = Question.query.filter(Question.deleted_at == None, Question.answers == None).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_questions = Question.query.filter(Question.deleted_at == None, Question.answers == None).count()
    
    elif category in ['algorithm', 'artificial-intelligence', 'cloud-computing', 'coding', 'data-analysis', 'data-science',  'devops', 'internet-of-things', 'robotics', 'ui-ux']:
        questions = Question.query.filter(Question.deleted_at == None, Question.category == category).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_questions = Question.query.filter(Question.deleted_at == None, Question.category == category).count()
        
    else:
        flash(f'The Category \'{category}\' not found!', category='error')
        return redirect(url_for('discussion.dashboard'))

    return questions, total_questions
#========================================================================================================
def unanswered_category_question(page, category, per_page):
    if category.lower() == 'random':
        if 'random_question_list' not in session:
            unanswered = Question.query.filter(Question.deleted_at == None, Question.answers == None).all()
            random.shuffle(unanswered)
            session['random_unanswered_list'] = unanswered
        total_unanswered = Question.query.filter(Question.deleted_at == None, Question.answers == None).count()
        unanswered = session.get('random_unanswered_list', [])
        unanswered = unanswered[(page - 1) * per_page: page * per_page]
        
    elif category.lower() == 'unanswered':
        unanswered = Question.query.filter(Question.deleted_at == None, Question.answers == None).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_unanswered = Question.query.filter(Question.deleted_at == None, Question.answers == None).count()
    elif category in ['algorithm', 'artificial-intelligence', 'cloud-computing', 'coding', 'data-analysis', 'data-science',  'devops', 'internet-of-things', 'robotics', 'ui-ux']:
        unanswered = Question.query.filter(Question.deleted_at == None, Question.category == category, Question.answers == None).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_unanswered = Question.query.filter(Question.deleted_at == None, Question.category == category, Question.answers == None).count()
    else:
        flash(f'The Category \'{category}\' not found!', category='error')
        return redirect(url_for('discussion.dashboard'))

    return unanswered, total_unanswered
#========================================================================================================
def unsolved_catogery_questions(page, category, per_page):
    if category.lower() == 'random':
        if 'random_question_list' not in session:
            unsolved = Question.query.filter(Question.deleted_at == None, Question.is_solved == False).all()
            random.shuffle(unsolved)
            session['random_unsolved_list'] = unsolved
        total_unsolved = Question.query.filter(Question.deleted_at == None, Question.is_solved == False).count()
        unsolved = session.get('random_unsolved_list', [])
        unsolved = unsolved[(page - 1) * per_page: page * per_page]
    
    elif category.lower() == 'unanswered':
        unsolved = Question.query.filter(Question.deleted_at == None, Question.answers == None, Question.is_solved == False).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_unsolved = Question.query.filter(Question.deleted_at == None, Question.answers == None, Question.is_solved == False).count()
    
    elif category in ['algorithm', 'artificial-intelligence', 'cloud-computing', 'coding', 'data-analysis', 'data-science',  'devops', 'internet-of-things', 'robotics', 'ui-ux']:
        unsolved = Question.query.filter(Question.deleted_at == None, Question.category == category, Question.is_solved == False).order_by(Question.created_at.desc()).slice((page - 1) * 15, page * 15).all()
        total_unsolved = Question.query.filter(Question.deleted_at == None, Question.category == category, Question.is_solved == False).count()
    
    else:
        flash(f'The Category \'{category}\' not found!', category='error')
        return redirect(url_for('discussion.dashboard'))

    return unsolved, total_unsolved
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
    sort_by = 'newest'
    queried_questions, total_questions = question_sort_by(page, sort_by, per_page)
    users, total_users = get_users(1, 20)
    
    # Calculate total pages for pagination
    total_pages = (max(1, total_questions) + per_page-1) // per_page

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.dashboard'))
    elif page > total_pages:
        return redirect(url_for('discussion.dashboard', page=total_pages))

    return render_template("discussion/dashboard.html",
                            title="Dashboard",
                            questions=get_questions(queried_questions),
                            active={'questions': 'show active', 'jobs': '', 'tags': '', 'users': '', 'badges': ''},
                            page={'question': page, 'user': 1},
                            total_pages={'question': 1, 'user': total_pages},
                            total_questions=total_questions,
                            users=users,
                            total_users=total_users,
                            achievements=get_achievement(),
                            trending_questions=trending_questions(),
                            tag_count=tag_count())
#========================================================================================================
                                # USER DASHBOARD
#========================================================================================================
@disc.route("/dashboard/users", methods=['GET', 'POST'])
@disc.route("/dashboard/users/page<int:page>", methods=['GET', 'POST'])
def user_dashboard(page=1):
    per_page = 20
    sort_by = 'newest'
    queried_questions, total_questions = question_sort_by(1, sort_by, 15)
    users, total_users = get_users(page, per_page)
    
    # Calculate total pages for pagination
    total_pages = (max(1, total_users) + per_page-1) // per_page

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('discussion.user_dashboard'))
    elif page > total_pages:
        return redirect(url_for('discussion.user_dashboard', page=total_pages))

    return render_template("discussion/dashboard.html",
                            title="Dashboard",
                            questions=get_questions(queried_questions),
                            active={'questions': '', 'jobs': '', 'tags': '', 'users': 'show active', 'badges': ''},
                            page={'question': 1, 'user': page},
                            total_pages={'question': 1, 'user': total_pages},
                            total_questions=total_questions,
                            users=users,
                            total_users=total_users,
                            achievements=get_achievement(),
                            trending_questions=trending_questions(),
                            tag_count=tag_count())
#========================================================================================================
def question_sort_by(page, sort_by='newest', per_page=15):
    if sort_by == 'newest':
        questions = Question.query.filter(Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.deleted_at == None).count()
    elif sort_by == 'featured':
        questions = Question.query.filter(Question.bountied != None, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.bountied != None, Question.deleted_at == None).count()
    elif sort_by == 'frequent':
        questions = Question.query.filter(Question.deleted_at == None).order_by(Question.views.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.deleted_at == None).count()
    elif sort_by == 'active':
        questions = Question.query.filter(Question.active == True, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.active == True, Question.deleted_at == None).count()
    elif sort_by == 'unanswered':
        questions = Question.query.filter(Question.answers == None, Question.deleted_at == None).order_by(Question.created_at.desc()).slice((page - 1) * per_page, page * per_page).all()
        total_questions = Question.query.filter(Question.answers == None, Question.deleted_at == None).count()
    else:
        flash(f'The Category \'{sort_by}\' not found!', category='error')
        return redirect(url_for('discussion.dashboard'))
    
    return questions, total_questions
#========================================================================================================
def get_users(page, per_page):
    users = db.session.query(User.name,
                            User.username,
                            UserDetail.reputation,
                            UserDetail.country
                            ).join(UserDetail).filter(User.deleted_at == None
                            ).order_by(UserDetail.reputation.desc()
                            ).slice((page - 1) * per_page, page * per_page).all()
    total_users = User.query.filter(User.deleted_at == None).count()
    return users, total_users
#========================================================================================================
@disc.route('/answer', methods=['GET', 'POST'])
@login_required
def answer():
    pass
#========================================================================================================
def get_achievement():
    questions = Question.query.filter(Question.deleted_at == None).count()
    answers = db.session.query(func.count(Answer.id)
                ).join(Question).filter(Question.deleted_at == None, Answer.deleted_at == None).scalar()
    accepted_answers = db.session.query(func.count(Answer.id)
                            ).join(Question).filter(Question.deleted_at == None, 
                                Answer.deleted_at == None, Answer.is_accepted == True).scalar()
    users = User.query.filter(User.deleted_at == None).count()
    
    return {'questions': format_number(questions),
        'answers': format_number(answers),
        'accepted_answers': format_number(accepted_answers),
        'users': format_number(users)}
#========================================================================================================
def format_number(num):
    suffixes = ['', 'K', 'M', 'B', 'T']
    magnitude = 0
    n = num
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    num_str = '{:.1f}'.format(num)
    integer_part = int(num)
    if integer_part >= 100 or n < 1000:
        return f'{integer_part}{suffixes[magnitude]}'
    return f'{num_str}{suffixes[magnitude]}'
#========================================================================================================
def trending_questions():
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    time_difference = func.extract('epoch', datetime.now() - Question.created_at)

# Query for trending questions
    trending = Question.query.filter(
        Question.deleted_at == None, Question.created_at >= two_weeks_ago
        ).order_by(func.coalesce(Question.views / time_difference, 0).desc()
        ).limit(5).all()
    return get_questions(trending)
#========================================================================================================
def tag_count():
    return db.session.query(Tag.title, func.count(QuestionTagAssociation.question_id)
                    ).join(QuestionTagAssociation).join(Question
                        ).filter(Question.deleted_at == None).group_by(Tag.title
                            ).order_by(func.count(QuestionTagAssociation.question_id).desc()).all()
#========================================================================================================