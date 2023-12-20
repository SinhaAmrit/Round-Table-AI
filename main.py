from flask import Flask, render_template

app = Flask(__name__, static_url_path="/static")

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300


@app.route("/")
def index_page():
    return render_template("index.html")


# =======================================Auth Route Start=======================================
@app.route("/signin")
def signin_page():
    return render_template("auth/signin.html", title="Sign In")


@app.route("/signup")
def signup_page():
    return render_template("auth/signup.html", title="Sign Up")


@app.route("/recover-password")
def recover_password():
    return render_template("auth/recover-password.html", title="Recover Password")


@app.route("/user-profile")
def user_profile():
    return render_template("auth/user-profile.html", title="Profile")


# =======================================Auth Route End=======================================

# ===================================Discussion Route Start===================================


@app.route("/dashboard")
def dashboard_page():
    return render_template("discussion/dashboard.html", title="Dashboard")


@app.route("/question")
def full_question():
    return render_template("/discussion/question.html", title="Discussion")


@app.route("/ask-question")
def ask_question():
    return render_template("/discussion/ask-question.html", title="Ask Question")


# ====================================Discussion Route End====================================

# =====================================Error Route Start=====================================


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page Not Found"), 404


# ======================================Error Route End======================================

app.run(debug=True)
