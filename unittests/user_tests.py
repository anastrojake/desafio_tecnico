import unittest
from unittest.mock import patch, MagicMock
from client.view import app


class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('client.view.db')
    @patch('client.model.User')
    def test_register(self, mock_user, db):
        mock_user.query.filter_by.return_value.first.return_value = None
        response = self.app.post('/register', json={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 201)

    @patch('client.view.create_access_token')
    @patch('client.view.User')
    def test_login(self, mock_user, mock_access_token):
        user = MagicMock(username='testuser', password_hash='testpassword')
        mock_access_token.return_value = 'token'
        mock_user.query.filter_by.return_value.first.return_value = user
        user.check_password.return_value = True
        response = self.app.post('/login', json={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)

    @patch('client.model.User')
    def test_login_invalid_credentials(self, mock_user):
        mock_user.query.filter_by.return_value.first.return_value = None
        response = self.app.post('/login', json={'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)

    def test_login_missing_credentials(self):
        response = self.app.post('/login', json={})
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
