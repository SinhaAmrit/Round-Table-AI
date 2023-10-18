# Import necessary modules and create a Blueprint for the Flask application
from flask import Blueprint, render_template, request, redirect, session
from flask import current_app as app
import pyotp

# Create a Blueprint named 'pages_bp' with specific configurations for templates and static files.
pages_bp = Blueprint('pages_bp', __name__, template_folder='templates',
                     static_folder='assets', static_url_path='assets')

# Define a dictionary to map messages to corresponding messages for user feedback.
msg_map = {
    '1': 'Account Creation successful',
    '2': 'Logout successful',
    '3': 'Please login',
    '4': 'User Already exists'
}

@pages_bp.route('/',  methods=('GET', 'POST',))
def landing_page():
    """
    Landing page for user login. Handles both GET and POST requests.
    
    GET: Displays the login page with an optional message.
    
    POST: Processes user login attempts, checking for username and password.
    Redirects to the home page if successful. If 2FA is enabled, it redirects to 2FA authentication.
    """
    print(app.config['db_store']['users'])
    if request.method == 'POST':
        users = app.config['db_store']['users']
        if users.get(request.form.get('username')) and users.get(request.form.get('username')).get('password') == request.form.get('password'):
            is_2fa = users.get(request.form.get('username')).get('enable_2fa')
            print('is_2fa')
            print(is_2fa)
            if is_2fa:
                session['2fa_user'] = request.form.get('username')
                return redirect('/2fa_auth')
            else:
                session['username'] = request.form['username']
                return redirect('/home')
        else:
            return redirect('/')
    else:
        message = ''
        if request.args.get('msg')!=None:
            message = msg_map[request.args.get('msg')]
        return render_template('index.html', message=message)

@pages_bp.route('/create_account', methods=('GET', 'POST',))
def create_account_page():
    """
    User account creation page. Handles both GET and POST requests.
    
    GET: Displays the account creation page.
    
    POST: Processes user account creation, storing user data.
    Redirects to the login page with a success or error message.
    """
    if request.method == 'POST':
        users = app.config['db_store']['users']
        if request.form.get('username') in users:
            return redirect('/?msg=4')
        else:
            users[request.form.get('username')] = { 
                    'password': request.form.get('password'),
                    'secret': pyotp.random_base32(),
                    'enable_2fa': False
            }
            return redirect('/?msg=1')
    else:
        return render_template('create_account.html')
    

@pages_bp.route('/home')
def home():
    """
    User home page after successful login. Requires authentication.
    Displays user information and provides an option to enable/disable 2FA.
    """
    if session.get('username'):
        username = session.get('username')
        secret  = app.config['db_store']['users'][username].get('secret')
        is_mfa = app.config['db_store']['users'][username].get('enable_2fa')
        provision_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name='Sample Flask 2FA App')
        mfa_text = 'Disable 2FA' if is_mfa else 'Enable 2FA'
        return render_template('home.html', provision_uri= provision_uri,
             username = username, mfa=is_mfa, mfa_text=mfa_text)
    else:
        return redirect('/?msg=3')

@pages_bp.route('/2fa_auth', methods=("GET", "POST",))
def mfa_auth_page():
    """
    Two-Factor Authentication (2FA) page for authentication with TOTP.
    
    GET: Displays the 2FA authentication page.
    
    POST: Processes 2FA authentication attempts, verifying the TOTP code.
    Redirects to the home page on success or back to the home page on failure.
    """
    if session.get('2fa_user') and request.method== 'POST':
        username = request.form.get('username')
        secret = app.config['db_store']['users'][username].get('secret')
        totp = pyotp.TOTP(secret)
        if request.form.get('mfacode') == totp.now():
            session['username'] = username
            session.pop('2fa_user', None)
            return redirect('/home')
        else:
            return redirect('/home')
    elif session.get('2fa_user'):
        user = session.get('2fa_user')
        return render_template('/2fa_auth.html', user=user)
    else:
        return redirect('/home')

@pages_bp.route('/save_2fa', methods=("GET", "POST",))
def save_2fa():
    """
    Route for enabling or disabling 2FA for a user.
    
    GET: Displays the 2FA settings page.
    
    POST: Processes the user's choice to enable or disable 2FA.
    Updates the user's 2FA setting and redirects to the home page.
    """
    if session.get('username') and request.method== 'POST':
        username = session.get('username')
        print(request.form.get('2fa', False))
        print(type(request.form.get('2fa', False)))
        enable_2fa = False
        if request.form.get('2fa') == 'True':
            enable_2fa = False
        else:
            enable_2fa = True
        app.config['db_store']['users'][username]['enable_2fa'] = enable_2fa
    print(app.config['db_store']['users'])
    return redirect('/home')

@pages_bp.route('/logout')
def logout():
    """
    User logout page. Handles logging out of the user session.
    Redirects to the login page with a logout message.
    """
    session.pop('username', None)
    return redirect('/?msg=2')