# Import the Flask class from the Flask framework and a blueprint named pages_bp.
from flask import Flask
from pages.pages import pages_bp

# Create a Flask application instance.
app = Flask(__name__)

# Set a secret key for the application. The secret key is a critical security measure.
app.secret_key = 'any random string'

# Configure a database store within the application's configuration.
# This dictionary stores user-related data, such as user profiles and authentication information.
app.config['db_store'] = {'users': {}}

# Register a blueprint with the Flask application.
# Blueprints are a way to organize routes, templates, and static files in a Flask application.
# The 'url_prefix' argument specifies the base URL for the routes defined within the blueprint.
app.register_blueprint(pages_bp, url_prefix='/')

# Entry point for running the Flask application.
if __name__ == '__main__':
    # Start the Flask development server.
    # The application will listen on all available network interfaces (0.0.0.0) and on port 5000.
    app.run(host='0.0.0.0', port=5000)