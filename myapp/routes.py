from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db  # Import the app and db instances
from models import User
from flask import send_from_directory

# Import models to access database tables
from models import User, Song

# Routes
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    user = User.query.all()
    songs = Song.query.all()
    genre = 'rock'
    recommendations = get_recommendations(genre)
    return render_template('index.html', users=users, recommendations=recommendations)

# New API endpoint for music recommendations
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    # Get query parameters (e.g., genre) from the request
    genre = request.args.get('genre')

    # Perform logic to generate music recommendations based on the genre
    # Replace this with your recommendation algorithm or logic
    recommendations = generate_recommendations(genre)
    others = content_based_recommendations(songs, user_preferences, k=5)
    # Return JSON response with recommendations
    return jsonify(recommendations + "\n " + others)

def generate_recommendations(genre):
    # Get the genre from the request
    genre = request.json['genre']

    # Get recommended songs based on the specified genre
    recommended_songs = Song.query.filter_by(genre=genre).limit(5).all()

    # Format the recommendations as JSON
    recommendations = [{'title': song.title, 'artist': song.artist} for song in recommended_songs]

    return jsonify(recommendations)
    return [{'title': 'Song 1', 'artist': 'Artist 1'}, {'title': 'Song 2', 'artist': 'Artist 2'}]

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            # Implement login logic (e.g., session management)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/download', methods=['GET'])
def download():
    filenames = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', filenames=filenames)
