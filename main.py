from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/signin")
def signin_page():
    return render_template("auth/signin.html")

@app.route("/signup")
def signup_page():
    return render_template("auth/signup.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("/dashboard.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.run(debug=True)
