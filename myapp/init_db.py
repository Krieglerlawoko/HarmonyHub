from app import db, User, Song
from models import User, Song

def init_database():
    with app.app_context():
        # Create the database tables
        db.create_all()

        # Add sample data
        user1 = User(username='user1', password='password1')
        user2 = User(username='user2', password='password2')

        song1 = Song(title='Song Title 1', artist='Artist 1', genre='Genre 1', file_path='/path/to/song1.mp3')
        song2 = Song(title='Song Title 2', artist='Artist 2', genre='Genre 2', file_path='/path/to/song2.mp3')

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(song1)
        db.session.add(song2)

        db.session.commit()

if __name__ == '__main__':
    # Run the initialization script
    init_database()
