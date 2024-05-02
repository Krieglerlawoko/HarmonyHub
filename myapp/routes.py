import os
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Song
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, LargeBinary
from sqlalchemy.orm import sessionmaker
from app import app, db  # Remove
from sqlalchemy.exc import IntegrityError


login_manager = LoginManager()
login_manager.init_app(app)


# Routes
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    users = User.query.all()
    songs = Song.query.all()
    genre = 'rock'
    recommendations = get_recommendations()
    return render_template('index.html', users=users, recommendations=recommendations)

# New API endpoint for music recommendations
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    genre = request.args.get('genre')
    if genre:
        recommendations = generate_recommendations(genre)
        return jsonify({'recommendations': recommendations})
    else:
        return jsonify({'error': 'Genre parameter is missing'}), 400

def generate_recommendations(genre):
    recommended_songs = Song.query.filter_by(genre=genre).limit(5).all()
    recommendations = [{'title': song.title, 'artist': song.artist} for song in recommended_songs]
    return recommendations

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('registration_success'))
    else:
        return render_template('register.html')

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

@app.route('/download', methods=['GET'])
def download():
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return 'UPLOAD_FOLDER is not configured.', 500

    download_folder = os.path.join(upload_folder, 'download')
    if not os.path.exists(download_folder):
        return 'Download folder does not exist.', 500

    filenames = os.listdir(download_folder)
    return render_template('download.html', filenames=filenames)

from flask_login import current_user

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch all songs from the database
    songs = Song.query.all()
    # Pass the fetched data to the template for rendering
    return render_template('dashboard.html', username=current_user.username, songs=songs)
    #return render_template('dashboard.html', username=current_user.username, songs=songs, playlist_title="Your Playlist Title", show_playlist=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve the user from the database based on the provided username
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()

        if user and check_password_hash(user.password, password):
            # Password is correct, log in the user
            login_user(user)  # Log in the user
            session['username'] = user.username  # Set session variable upon successful login
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')

    # Render the login form template for GET requests
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre = request.form['genre']
        file = request.files['file']
        cover_art = request.files['cover_art']

        if file:
            try:
                # Save song information to the database
                new_song = Song(title=title, artist=artist, genre=genre, file_data=file.read(), cover_art_data=cover_art.read())
                db.session.add(new_song)
                db.session.commit()
                flash('Song uploaded successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'error')

            return redirect(url_for('dashboard'))
        else:
            flash('No file selected!', 'error')
            return redirect(request.url) 

    return render_template('upload.html')
