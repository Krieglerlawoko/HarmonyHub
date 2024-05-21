import unittest
from app import db, create_app
from models import User, Song

class TestModels(unittest.TestCase):
    def setUp(self):
        """Set up test database and app context."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Clean up test database and app context."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user creation."""
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test@example.com')

    def test_song_creation(self):
        """Test song creation."""
        song = Song(title='Test Song', artist='Test Artist', genre='Test Genre')
        db.session.add(song)
        db.session.commit()
        self.assertIsNotNone(song.id)
        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(song.artist, 'Test Artist')
        self.assertEqual(song.genre, 'Test Genre')

if __name__ == '__main__':
    unittest.main()
