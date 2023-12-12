from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/signin")
def signin_page():
    return render_template("auth/signin.html", title="Sign In")

@app.route("/signup")
def signup_page():
    return render_template("auth/signup.html", title="Sign Up")

@app.route("/dashboard")
def dashboard_page():
    return render_template("/dashboard.html", title = "Dashboard", greeting = greeting())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = "404"), 404



def greeting():
    current_time = datetime.now().time()
    if current_time.hour < 12:
        return "Good Morning"
    elif current_time.hour < 16:
        return "Good Afternoon"
    else:
        return "Good Evening"

if __name__ == '__main__':
    app.run(debug=True)
