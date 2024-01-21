from flask import Blueprint, render_template, request, flash, redirect, url_for
from .auth import is_strong_password
from .forms import ChangePasswordForm, UserProfileForm, EmailSettingsForm
from . import db
from flask_login import login_required, current_user

# Create a Blueprint named 'acc'
acc = Blueprint('account', __name__)
acc.config = {'UPLOAD_FOLDER': './uploads'}

@acc.route('/notifications', methods=['GET', 'POST'])
@login_required
def all_notification():
    if request.method == 'POST':
        pass
    else:
        return render_template("account/notifications.html", 
                                title="Notifications", 
                                notifications=current_user.notifications)

@acc.route('/user-profile', methods=['GET', 'POST'])
@login_required
def user_profile():

    # if User.query.filter_by(username=username).first():
    #     user = User.query.filter_by(username=username).first()

    #     created_at = datetime.utcfromtimestamp(user.created_at.timestamp())
    #     # Calculate the time difference
    #     time_difference = datetime.utcnow() - created_at

    #     # Get the formatted time difference
    #     time_ago = format_time_difference(time_difference)

    #     print('This line 37')

    #     return render_template("account/user-profile.html", title=user.name, user=user, time_ago=time_ago)

    # else:
    #     return redirect(url_for('views.home'))
    
    return render_template("account/user-profile.html", title=current_user.name, user=current_user)

# Define a function to format the time difference
def format_time_difference(time_difference):

    # Calculate years, months, and days
    years = time_difference.days // 365
    months = (time_difference.days % 365) // 30
    days = (time_difference.days % 365) % 30

    if years > 0:
        return f"{years} {'year' if years == 1 else 'years'} ago"
    elif months > 0:
        return f"{months} {'month' if months == 1 else 'months'} ago"
    else:
        return f"{days} {'day' if days == 1 else 'days'} ago"

@acc.route('/referrals', methods=['GET', 'POST'])
@login_required
def referrals():
    return render_template("account/referrals.html", title="Referrals")


@acc.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_profile_form = get_user_profile_form()
    change_password_form = ChangePasswordForm()
    email_settings_form = get_email_settings_form()

    if request.method == 'POST':
        print('inside POST')
        if user_profile_form.is_submitted(): # validate
            update_user_profile(user_profile_form)

        if change_password_form.validate_on_submit():
            change_password(change_password_form)

        if email_settings_form.validate_on_submit():
            email_settings(email_settings_form)

    return render_template("account/settings.html", title="Settings", 
                        user_profile_form = user_profile_form, 
                        change_password_form=change_password_form,
                        email_settings_form=email_settings_form)

def get_user_profile_form():
    form = UserProfileForm(
        full_name = current_user.name,
        location = current_user.details.country,
        about_me = current_user.details.about,
        website_link = current_user.conn_accounts.website,
        twitter_link = current_user.conn_accounts.twitter,
        facebook_link = current_user.conn_accounts.facebook,
        instagram_link = current_user.conn_accounts.instagram,
        youtube_link = current_user.conn_accounts.youtube,
        vimeo_link = current_user.conn_accounts.vimeo,
        github_link = current_user.conn_accounts.github,
        profile_photo = current_user.details.profile_photo,
    )
    return form

def get_email_settings_form():
    form = EmailSettingsForm(
        email = current_user.email,
        feature_announcements = current_user.email_settings.feature_announcements,
        round_table = current_user.email_settings.round_table,
        tips_reminders = current_user.email_settings.tips_reminders,
        inbox = current_user.email_settings.inbox,
        community_milestones = current_user.email_settings.community_milestones,
        research = current_user.email_settings.research,
        recommended_jobs = current_user.email_settings.recommended_jobs,
        company_alerts = current_user.email_settings.company_alerts
        )
    return form

def email_settings(form):
    pass

def change_password(form):
    current_password = form.current_password.data
    new_password = form.new_password.data

    if current_user.check_password(current_password):
        if not is_strong_password(form.new_password.data)[0]:
            flash(is_strong_password(form.new_password.data)[1], category='error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
    else:
        flash('Password does not match', category='error')

    return redirect(url_for('account.settings'))

def update_user_profile(form):

    current_user.name = form.full_name.data
    current_user.location = form.location.data
    current_user.about_me = form.about_me.data

    current_user.conn_accounts.website = form.website_link.data
    current_user.conn_accounts.twitter = form.twitter_link.data
    current_user.conn_accounts.facebook = form.facebook_link.data
    current_user.conn_accounts.instagram = form.instagram_link.data
    current_user.conn_accounts.youtube = form.youtube_link.data
    current_user.conn_accounts.vimeo = form.vimeo_link.data
    current_user.conn_accounts.github = form.github_link.data

    # print('Outside Image ')
    # if form.profile_photo.data:
    #     upload_folder = os.path.join(acc.config['UPLOAD_FOLDER'], 'user', str(current_user.username), 'profile-photo')
    #     os.makedirs(upload_folder, exist_ok=True)

    #     # Use user_name as the filename for uniqueness
    #     _, file_extension = os.path.splitext(form.profile_photo.data.filename)
    #     filename = secure_filename(f'{current_user.name}{file_extension}')
    #     profile_photo_path = os.path.join(upload_folder, filename).replace('\\', '/')
    #     form.profile_photo.data.save(profile_photo_path)

    #     current_user.details.profile_photo = profile_photo_path.strip('.')

    #     print(f'{form.profile_photo.data}')

    db.session.commit()
    print("update database")

    flash('Profile information updated successfully!', 'success')
    return redirect(url_for('account.settings'))