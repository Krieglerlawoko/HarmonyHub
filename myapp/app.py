from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from recommendations import get_recommendations, content_based_recommendations
#from app.db import init_db, db
from __init__ import create_app


app = app = create_app() 

from models import User, Song

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Routes
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
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

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
def logout():
    # Implement logout logic (e.g., session management)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    # Implement song upload logic
    file = request.files['file']
    # Save the file and update the database
    flash('Song uploaded successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Get song details from the request
        title = request.form['title']
        artist = request.form['artist']
        genre = request.form['genre']
        file_path = request.form['file_path']

        # Create a new song object and add it to the database
        new_song = Song(title=title, artist=artist, genre=genre, file_path=file_path)
        db.session.add(new_song)
        db.session.commit()

        flash('Song uploaded successfully!', 'success')
        return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
