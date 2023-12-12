from src import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

'''
Run this in Terminal=>
$env:FLASK_APP="src"; $env:FLASK_DEBUG="development"; flask run
'''