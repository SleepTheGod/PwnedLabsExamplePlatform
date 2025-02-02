import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Simple route to render the index.html template
@app.route('/')
def home():
    return render_template('index.html')

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the Challenges page
@app.route('/challenges')
def challenges():
    return render_template('challenges.html')

# Route for the Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

# Route for the Sign In page (GET and POST to handle form submissions)
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add logic for verifying user credentials
        # For now, we'll just print the credentials to simulate a sign-in
        print(f"Username: {username}, Password: {password}")
        return redirect(url_for('challenges'))  # Redirect to challenges page after successful sign-in
    return render_template('signin.html')

# Route for the Sign Up page (GET and POST to handle form submissions)
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add logic to create a user (save to DB or memory)
        print(f"New user - Username: {username}, Password: {password}")
        return redirect(url_for('sign_in'))  # Redirect to the sign-in page
    return render_template('signup.html')

# Route for the Teams page
@app.route('/teams')
def teams():
    return render_template('teams.html')

# If you need to start your app in production mode
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
