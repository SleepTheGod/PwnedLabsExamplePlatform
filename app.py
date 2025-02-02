import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the database connection
def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'your-rds-hostname'),
            database=os.getenv('DB_NAME', 'pwnedlabs'),
            user=os.getenv('DB_USER', 'your-db-user'),
            password=os.getenv('DB_PASSWORD', 'your-db-password')
        )
        cursor = conn.cursor()
        # Create tables if they don't exist
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE,
                password VARCHAR(100)
            );
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS challenges (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                description TEXT,
                points INT
            );
        ''')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS leaderboard (
                user_id INT,
                challenge_id INT,
                score INT,
                PRIMARY KEY (user_id, challenge_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (challenge_id) REFERENCES challenges(id)
            );
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error initializing database", e)

# Fetch challenges from the database
def get_challenges():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'your-rds-hostname'),
        database=os.getenv('DB_NAME', 'pwnedlabs'),
        user=os.getenv('DB_USER', 'your-db-user'),
        password=os.getenv('DB_PASSWORD', 'your-db-password')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM challenges')
    challenges = cursor.fetchall()
    cursor.close()
    conn.close()
    return challenges

# Add a user to the database
def add_user(username, password):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'your-rds-hostname'),
        database=os.getenv('DB_NAME', 'pwnedlabs'),
        user=os.getenv('DB_USER', 'your-db-user'),
        password=os.getenv('DB_PASSWORD', 'your-db-password')
    )
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
    conn.commit()
    cursor.close()
    conn.close()

# Verify user credentials
def verify_user_credentials(username, password):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'your-rds-hostname'),
        database=os.getenv('DB_NAME', 'pwnedlabs'),
        user=os.getenv('DB_USER', 'your-db-user'),
        password=os.getenv('DB_PASSWORD', 'your-db-password')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
    stored_password_hash = cursor.fetchone()
    cursor.close()
    conn.close()
    if stored_password_hash:
        return check_password_hash(stored_password_hash[0], password)
    return False

# Get leaderboard from the database
def get_leaderboard():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'your-rds-hostname'),
        database=os.getenv('DB_NAME', 'pwnedlabs'),
        user=os.getenv('DB_USER', 'your-db-user'),
        password=os.getenv('DB_PASSWORD', 'your-db-password')
    )
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, SUM(c.points) AS total_score
        FROM leaderboard l
        JOIN users u ON u.id = l.user_id
        JOIN challenges c ON c.id = l.challenge_id
        GROUP BY u.username
        ORDER BY total_score DESC
    ''')
    leaderboard = cursor.fetchall()
    cursor.close()
    conn.close()
    return leaderboard

# Flask routes
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

# Error handler for 404 (Page not found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Initialize the database before starting the app
    init_db()
    
    if app.config['ENV'] == 'development':
        app.run(debug=True)
    else:
        # Use Gunicorn for production
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
