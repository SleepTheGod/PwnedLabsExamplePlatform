from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/challenges')
def challenges():
    return render_template('challenges.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')

if __name__ == '__main__':
    # Running on localhost (127.0.0.1) and port 5000
    app.run(debug=True, host='127.0.0.1', port=5000)
