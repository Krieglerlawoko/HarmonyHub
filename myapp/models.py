from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # Define the is_active attribute
    def get_id(self):
        return self.id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    file_path = db.Column(db.String(200))
    file_data = db.Column(db.LargeBinary)
    #cover_art_data = db.Column(db.LargeBinary)  # Make sure this line is included

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'

class UserPreference(db.Model):
    __tablename__ = 'user_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Corrected here
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
