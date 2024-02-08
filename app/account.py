from flask import Blueprint, render_template, request, flash, redirect, url_for
from .auth import is_strong_password
from .models import User, Notification
from .forms import ChangePasswordForm, UserProfileForm, EmailSettingsForm, PrivacyForm, DeleteAccountForm
from . import db
from datetime import datetime
from flask_login import login_required, current_user
import humanize

# Create a Blueprint named 'acc'
acc = Blueprint('account', __name__)
acc.config = {'UPLOAD_FOLDER': './uploads'}
#========================================================================================================
                                # NOTIFICATIONS
#========================================================================================================
@acc.route('/notifications', methods=['GET'])
@acc.route('/notifications/page<int:page>', methods=['GET'])
@login_required
def all_notification(page=1):
    # Total number of notifications for the current user
    total_notifications = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.deleted_at == None
    ).count()

    # Calculate total pages for pagination
    total_pages = (max(1, total_notifications) + 14) // 15

    # Redirect to the first or last page if the requested page is out of bounds
    if page < 1:
        return redirect(url_for('account.all_notification'))
    elif page > total_pages:
        return redirect(url_for('account.all_notification', page=total_pages))

    # Fetch notifications for the requested page
    queried_notifications = Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.deleted_at == None
    ).order_by(Notification.created_at.desc()).slice((page - 1) * 15, page * 15).all()

    notifications = []
    # Prepare notification data for rendering
    for notification in queried_notifications:
        notifications.append({
            'data': notification.data,
            'type': notification.type,
            'event_url': notification.event_url,
            'created_ago': humanize.naturaltime(datetime.utcnow() - notification.created_at),
            'read': notification.read_at
        })

    return render_template("account/notifications.html",
                            title="Notifications",
                            notifications=notifications,
                            page=page,
                            total_pages=total_pages,
                            total_notifications=total_notifications)
#========================================================================================================
                                # USER PROFILE
#========================================================================================================
@acc.route('/user-profile', methods=['GET', 'POST'])
@acc.route('/user/<username>', methods=['GET', 'POST'])
def user_profile(username=None):
    if not username:
        username=current_user.username
    user = User.query.filter_by(username=username).first()
    if user and not user.deleted_at:
        user = {
            'name' : user.name,
            'username' : user.username,
            'created_ago' : humanize.naturaltime(datetime.utcnow() - user.created_at),
            'about' : user.details.about,
            'country' : user.details.country,
            'status' : user.details.status,
            'active' : user.details.active,
            'reputation' : user.details.reputation,
            'gold' : user.details.gold,
            'silver' : user.details.silver,
            'bronze' : user.details.bronze,
            'last_seen' : user.details.last_seen,
            'website' : user.conn_accounts.website,
            'twitter' : user.conn_accounts.twitter,
            'facebook' : user.conn_accounts.facebook,
            'instagram' : user.conn_accounts.instagram,
            'linkedIn' : user.conn_accounts.linkedIn,
            'youtube' : user.conn_accounts.youtube,
            'vimeo' : user.conn_accounts.vimeo,
            'github' : user.conn_accounts.github,
            }

    else:
        flash('User not found!', 'error')
        return redirect(url_for('discussion.dashboard'))
    
    return render_template("account/user-profile.html", title=user['name'], user=user)
#========================================================================================================
                                # REFERRALS
#========================================================================================================
@acc.route('/referrals', methods=['GET', 'POST'])
@login_required
def referrals():
    return render_template("account/referrals.html", title="Referrals")
#========================================================================================================
                                # SETTINGS
#========================================================================================================
@acc.route('/settings', methods=['GET'])
@login_required
def settings():
    print('in settings')
    user_profile_form = get_user_profile_form(request.form)
    change_password_form = get_change_password_form(request.form)
    email_settings_form = get_email_settings_form(request.form)
    privacy_form = get_privacy_settings_form(request.form)
    delete_account_form = get_delete_account_form(request.form)

    return render_template("account/settings.html", title="Settings",
                        user_profile_form = user_profile_form, 
                        change_password_form=change_password_form,
                        email_settings_form=email_settings_form,
                        privacy_form=privacy_form,
                        delete_account_form=delete_account_form)
#========================================================================================================
                                # PROFILE SETTINGS
#========================================================================================================
@acc.route('/settings/profile-settings', methods=['POST'])
@login_required
def profile_settings():
    form = get_user_profile_form(request.form)
    if form.validate_on_submit():
        current_user.name = form.full_name.data
        current_user.details.country = form.location.data
        current_user.details.about = form.about_me.data
        current_user.conn_accounts.website = form.website_link.data
        current_user.conn_accounts.linkedIn = form.linkedin_link.data
        current_user.conn_accounts.twitter = form.twitter_link.data
        current_user.conn_accounts.facebook = form.facebook_link.data
        current_user.conn_accounts.instagram = form.instagram_link.data
        current_user.conn_accounts.youtube = form.youtube_link.data
        current_user.conn_accounts.vimeo = form.vimeo_link.data
        current_user.conn_accounts.github = form.github_link.data
        
        db.session.commit()
        flash('Profile information updated successfully!', 'success')
    else:
        flash('Invalid data submitted!', 'error')

    return redirect(url_for('account.settings'))

    #    print('Outside Image ')
    #    if form.profile_photo.data:
    #        upload_folder = os.path.join(acc.config['UPLOAD_FOLDER'], 'user', str(current_user.username), 'profile-photo')
    #        os.makedirs(upload_folder, exist_ok=True)

    #        # Use user_name as the filename for uniqueness
    #        _, file_extension = os.path.splitext(form.profile_photo.data.filename)
    #        filename = secure_filename(f'{current_user.name}{file_extension}')
    #        profile_photo_path = os.path.join(upload_folder, filename).replace('\\', '/')
    #        form.profile_photo.data.save(profile_photo_path)

    #        current_user.details.profile_photo = profile_photo_path.strip('.')

    #        print(f'{form.profile_photo.data}')
#========================================================================================================
def get_user_profile_form(data=None):
    form = UserProfileForm(data = data,
        full_name =  current_user.name,
        location = current_user.details.country,
        about_me = current_user.details.about,
        website_link = current_user.conn_accounts.website,
        linkedin_link = current_user.conn_accounts.linkedIn,
        twitter_link = current_user.conn_accounts.twitter,
        facebook_link = current_user.conn_accounts.facebook,
        instagram_link = current_user.conn_accounts.instagram,
        youtube_link = current_user.conn_accounts.youtube,
        vimeo_link = current_user.conn_accounts.vimeo,
        github_link = current_user.conn_accounts.github,
        profile_photo = current_user.details.profile_photo,
    )
    return form
#========================================================================================================
                                # CHANGE PASSWORD
#========================================================================================================
@acc.route('/settings/password-settings', methods=['POST'])
@login_required
def change_password():
    form = get_change_password_form(request.form)
    if form.validate_on_submit():
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
#========================================================================================================
def get_change_password_form(data=None):
    return ChangePasswordForm(data=data)
#========================================================================================================
                                # EMAIL SETTINGS
#========================================================================================================
@acc.route('/settings/email-settings', methods=['POST'])
@login_required
def email_settings():
    form = get_email_settings_form(request.form)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.email_settings.feature_announcements = form.feature_announcements.data
        current_user.email_settings.round_table = form.round_table.data
        current_user.email_settings.tips_reminders = form.tips_reminders.data
        current_user.email_settings.inbox = form.inbox.data
        current_user.email_settings.community_milestones = form.community_milestones.data
        current_user.email_settings.research = form.research.data
        current_user.email_settings.recommended_jobs = form.recommended_jobs.data
        current_user.email_settings.company_alerts = form.company_alerts.data

        db.session.commit()
        flash('Email Settings updated successfully!', 'success')
    else:
        flash('Invalid data submitted', 'error')

    return redirect(url_for('account.settings'))
#========================================================================================================
def get_email_settings_form(data=None):
    form = EmailSettingsForm(data=data,
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
#========================================================================================================
                                # PRIVACY SETTINGS
#========================================================================================================
@acc.route('/settings/privacy-settings', methods=['POST'])
@login_required
def privacy_settings():
    form = get_privacy_settings_form(request.form)
    if form.validate_on_submit():
        current_user.privacy_settings.profile_photo = form.profile_photo.data
        current_user.privacy_settings.email = form.email_privacy.data
        current_user.privacy_settings.biography = form.biography.data
        current_user.privacy_settings.country = form.country.data
        current_user.privacy_settings.social_links = form.social_links.data
        db.session.commit()
        print("update database")
        flash('Privacy Settings updated successfully!', 'success')
    else:
        flash('Invalid data submitted!', 'error')

    return redirect(url_for('account.settings'))
#========================================================================================================
def get_privacy_settings_form(data=None):
    form = PrivacyForm(data=data,
        profile_photo = current_user.privacy_settings.profile_photo,
        email_privacy = current_user.privacy_settings.email,
        biography = current_user.privacy_settings.biography,
        country = current_user.privacy_settings.country,
        social_links = current_user.privacy_settings.social_links
        )
    return form
#========================================================================================================
                                # DELETE ACCOUNT
#========================================================================================================
@acc.route('/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    form = get_delete_account_form(request.form)
    if form.validate_on_submit():
        if form.delete_terms.data:
            current_user.deleted_at = datetime.utcnow()
            db.session.commit()
            flash('Account Deleted Successfully!', 'success')
            return redirect(url_for('auth.sign_out'))
    else:
        flash('Invaliid response!', 'error')
        return redirect(url_for('account.settings'))
#========================================================================================================
def get_delete_account_form(data=None):
    return DeleteAccountForm(data=data)
#========================================================================================================