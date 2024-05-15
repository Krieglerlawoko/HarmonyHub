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
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized', 'error')
    return redirect(url_for('login'))

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

from flask import jsonify, request
# Initialize the Spotipy client with your Spotify credentials
client_credentials_manager = SpotifyClientCredentials(client_id='3e315e99365a46118e423cf641bfc4c3', client_secret='44ad8667502b4adeb460d55e2107781e')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def fetch_recommendations(genre):
    results = sp.search(q='genre:' + genre, type='track', limit=9)
    recommendations = []
    for track in results['tracks']['items']:
        recommendations.append({
            'song_name': track['name'],
            'artist_title': track['artists'][0]['name'],
            'cover_art_url': track['album']['images'][0]['url']
        })
    return recommendations

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    genre = request.args.get('genre')
    if genre:
        try:
            recommendations = fetch_recommendations(genre)
            return render_template('recommendations.html', recommended_songs=recommendations)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Genre parameter is missing'}), 400


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


from flask import send_file, abort

@app.route('/download', methods=['GET', 'POST'])
@login_required
def download_song():
    if request.method == 'POST':
        file_id = request.form['file_id']
        # Retrieve the song from the database based on the file_id
        song = Song.query.get(file_id)
        if song:
            # Send the song file as an attachment for download
            return send_file(song.file_data, as_attachment=True, download_name=song.title + '.mp3')
        else:
            # Song not found, return a 404 error
            abort(404)
    else:
        # For GET requests, fetch all songs for display on the download page
        songs = Song.query.all()
        return render_template('download.html', songs=songs)


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('limited_dashboard'))

    # Fetch all songs from the database
    songs = Song.query.all()
    # Pass the fetched data to the template for rendering
    return render_template('dashboard.html', username=current_user.username, songs=songs)


@app.route('/limited_dashboard')
def limited_dashboard():
    # Assume you have a function or method to fetch song titles and artist names from your database
    songs =  Song.query.all()


    return render_template('limited_dashboard.html', songs=songs,)



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
    if current_user.is_authenticated:
        logout_user()
        flash('Logged out successfully!', 'success')
    else:
        flash('You are not logged in.', 'error')
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
