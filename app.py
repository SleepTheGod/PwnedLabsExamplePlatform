import os
from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_challenges, add_user, get_leaderboard
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the database
init_db()

# Set the secret key for session handling
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret-key')

# Production configuration
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')

# Function to verify user credentials
def verify_user_credentials(username, password):
    # Replace this with your actual password verification logic, such as checking hashes in your DB
    stored_password_hash = get_user_password_hash(username)  # Implement this function
    return check_password_hash(stored_password_hash, password)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user_credentials(username, password):
            return redirect(url_for('challenges'))
        else:
            return "Invalid login"
    return render_template('signin.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add user to the database securely (ensure password is hashed)
        add_user(username, password)  # Implement secure password hashing
        return redirect(url_for('sign_in'))
    return render_template('signup.html')

@app.route('/challenges')
def challenges():
    challenges = get_challenges()
    return render_template('challenges.html', challenges=challenges)

@app.route('/leaderboard')
def leaderboard():
    leaderboard_data = get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

@app.route('/about')
def about():
    return render_template('about.html')

# Add error handler for 404 (Page not found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    if app.config['ENV'] == 'development':
        app.run(debug=True)
    else:
        # Use Gunicorn or another WSGI server for production
        from gunicorn.app.base import BaseApplication
        from gunicorn.six import iteritems

        class FlaskApplication(BaseApplication):
            def __init__(self, app):
                self.app = app
                super(FlaskApplication, self).__init__()

            def load(self):
                return self.app

            def load_config(self):
                for key, value in iteritems(self.app.config):
                    self.cfg.set(key, value)

        FlaskApplication(app).run()

