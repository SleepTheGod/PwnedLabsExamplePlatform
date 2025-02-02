import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Example of connecting to PostgreSQL (RDS)
def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conn.cursor()
        # Add any necessary initialization here, like creating tables
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
    except Exception as e:
        print("Error initializing database:", e)

def get_challenges():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM challenges')
    challenges = cursor.fetchall()
    return challenges

def add_user(username, password):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
    conn.commit()

def get_leaderboard():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
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
    return leaderboard

# Initialize the database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Assume you have a function to verify user credentials
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
        add_user(username, password)
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

if __name__ == '__main__':
    # Production server (use Gunicorn or similar for deployment)
    app.run(debug=True, host='0.0.0.0', port=5000)
