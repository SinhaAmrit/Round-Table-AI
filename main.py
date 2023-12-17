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


# =======================================Auth Route End=======================================

# ===================================Discussion Route Start===================================


@app.route("/questions")
def questions_page():
    return render_template("discussion/questions.html", title="Questions")


@app.route("/question")
def full_question():
    return render_template("/discussion/question.html", title="Discussion")


@app.route("/ask-question")
def ask_question():
    return render_template("/discussion/ask-question.html", title="Ask Question")


@app.route("/tags-list")
def tags_list():
    return render_template("/discussion/tags-list.html", title="Tags List")

@app.route("/category")
def category():
    return render_template("/discussion/category.html", title="Categories")


# ====================================Discussion Route End====================================

# =====================================Error Route Start=====================================


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page Not Found"), 404


# ======================================Error Route End======================================

# =====================================Extracts Route Start=====================================


@app.route("/user-list")
def user_list():
    return render_template("/extracts/user-list.html", title="User List")

@app.route("/badges-list")
def badges_list():
    return render_template("/extracts/badges-list.html", title="Badges List")


# =====================================Extracts Route End=====================================


app.run(debug=True)
