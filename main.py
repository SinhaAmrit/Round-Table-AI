from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index_page():
    return render_template("index.html")


@app.route("/signin")
def signin_page():
    return render_template("auth/signin.html", title="Sign In")


@app.route("/signup")
def signup_page():
    return render_template("auth/signup.html", title="Sign Up")


@app.route("/recover-password")
def recover_password():
    return render_template("auth/recover-password.html", title="Recover Password")


@app.route("/dashboard")
def dashboard_page():
    return render_template("/dashboard.html", title="Dashboard")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", title="Page Not Found"), 404


app.run(debug=True)
