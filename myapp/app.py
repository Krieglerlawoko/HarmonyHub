from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import secrets
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from flask_migrate import Migrate

# Initialize the app11
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database-file.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sievrjxxscwcvs:0c6714283c9073f74b792315a9418f939bfc16fa76d226d20898975ee6aa3d81@ec2-44-194-102-142.compute-1.amazonaws.com:5432/d9neel4gp1m6gq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Initialize extensionss2
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

client_credentials_manager = SpotifyClientCredentials(client_id='3e315e99365a46118e423cf641bfc4c3', client_secret='44ad8667502b4adeb460d55e2107781e')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized', 'error')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    def get_id(self):
        return self.id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    file_data = db.Column(db.LargeBinary)
#    cover_art_data = db.Column(db.LargeBinary)
    cover_art_data = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'

    @property
    def cover_art_url(self):
        if self.cover_art_data:
            return url_for('cover_art', song_id=self.id)
        else:
            return url_for('static', filename='default_cover_art.jpg')  # Use a default image if cover art is not available

class UserPreference(db.Model):
    __tablename__ = 'user_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    preference_name = db.Column(db.String(100))
    preference_value = db.Column(db.String(255))

    def __repr__(self):
        return f'<Post {self.user_id}>'

class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Post {self.user_id}>'

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.user_id}>'

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.song_id}>'

# Fetch Spotify recommendations
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

# Routes
@app.route('/')
def index():
    users = User.query.all()
    genre = 'rock'
    recommendations = fetch_recommendations(genre)
    return render_template('index.html', users=users, recommendations=recommendations)

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
        username, email, password = request.form['username'], request.form['email'], request.form['password']
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

@app.route('/download', methods=['GET', 'POST'])
@login_required
def download_song():
    if request.method == 'POST':
        song = Song.query.get(request.form.get('file_id'))
        if song:
            return send_file(song.file_data, as_attachment=True, download_name=song.title + '.mp3')
        abort(404)
    else:
        songs = Song.query.all()
        return render_template('download.html', songs=songs)

@app.route('/dashboard')
@login_required
def dashboard():
    songs = Song.query.all()
    return render_template('dashboard.html', username=current_user.username, songs=songs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form.get('username'), request.form.get('password')
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
# @login_required  # Uncomment this line if using Flask-Login for authentication
def upload_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre = request.form['genre']
        file = request.files['file']
        cover_art = request.files['cover_art']
        
        if file and cover_art:
            try:
                new_song = Song(
                    title=title,
                    artist=artist,
                    genre=genre,
                    file_data=file.read(),
                    cover_art_data=cover_art.read()
                )
                db.session.add(new_song)
                db.session.commit()
                flash('Song uploaded successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('dashboard'))
        else:
            flash('File and cover art are required!', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/cover_art/<int:song_id>')
def cover_art(song_id):
    song = Song.query.get_or_404(song_id)
    if song.cover_art_data:
        return send_file(BytesIO(song.cover_art_data), mimetype='image/jpeg')
    else:
        flash('No cover art available for this song', 'error')
        return redirect(url_for('dashboard'))

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

@app.route('/limited_dashboard')
def limited_dashboard():
    songs = Song.query.all()
    return render_template('limited_dashboard.html', songs=songs)

# Initialize the database and create tables
with app.app_context():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5001)

