import unittest
from app import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client."""
        app.testing = True
        self.client = app.test_client()

    def test_home_route(self):
        """Test home route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to My App', response.data)

    def test_login_route(self):
        """Test login route."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_route(self):
        """Test register route."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_invalid_route(self):
        """Test invalid route."""
        response = self.client.get('/invalid')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
