import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Import the app and db instances
from models import User
from flask import send_from_directory
from flask import current_app
from flask import session
from flask import jsonify

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
    recommendations = get_recommendations()
    return render_template('index.html', users=user, recommendations=recommendations)

# New API endpoint for music recommendations
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    # Get the genre from the request query parameters
    genre = request.args.get('genre')

    # Check if the genre is provided
    if genre:
        # Generate recommendations based on the genre
        recommendations = generate_recommendations(genre)
        return jsonify({'recommendations': recommendations})
    else:
        return jsonify({'error': 'Genre parameter is missing'}), 400




def generate_recommendations(genre):
    # Get the genre from the request
    genre = request.json('genre')

    # Get recommended songs based on the specified genre
    recommended_songs = Song.query.filter_by(genre=genre).limit(5).all()

    # Format the recommendations as JSON
    recommendations = [{'title': song.title, 'artist': song.artist} for song in recommended_songs]

    return jsonify(recommendations)
    return [{'title': 'Song 1', 'artist': 'Artist 1'}, {'title': 'Song 2', 'artist': 'Artist 2'}]


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user input from the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists in the database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # Create a new user object with hashed password
        new_user = User(username=username, email=email, password=hashed_password)

        # Add the new user to the database session
        db.session.add(new_user)
        db.session.commit()

        # Redirect to a success page or login page
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('registration_success'))
    else:
        # Render the registration form template
        return render_template('register.html')


@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/download', methods=['GET'])
def download():
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if upload_folder is None:
        return 'UPLOAD_FOLDER is not configured.', 500

    download_folder = os.path.join(upload_folder, 'download')
    if not os.path.exists('download'):
        return 'Download folder does not exist.', 500

    filenames = os.listdir('download')
    return render_template('download.html', filenames='download')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:  # Check if user is logged in
        # Fetch all songs from the database
        songs = Song.query.all()
        # Pass the fetched data to the template for rendering
        return render_template('dashboard.html', username=session['username'], songs=songs)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user from the database based on the provided username
        user = User.query.filter_by(username=username).first()

        if user:
            # Check if the provided password matches the hashed password stored in the database
            if check_password_hash(user.password, password):
                # Password is correct, log in the user
                session['username'] = username  # Set session variable upon successful login
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password!', 'error')
        else:
            flash('Invalid username!', 'error')

    # Render the login form template for GET requests
    return render_template('login.html')
