import unittest
from unittest.mock import patch, MagicMock
from client.view import app
from flask_jwt_extended import create_access_token


class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('client.view.Client')
    @patch('client.view.db')
    @patch('client.view.client_schema')
    def test_add_client_success(self, mock_client_schema, mock_db, mock_client):
        data = {'name': 'Test Client', 'email': 'test@example.com'}
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        with app.app_context():
            token = create_access_token(identity='user_id')
            response = self.app.post('/clients', json=data, headers={'Authorization': f'Bearer {token}'})
            mock_client.assert_called_once_with(name='Test Client', email='test@example.com')
            mock_db.session.add.assert_called_once_with(mock_client_instance)
            mock_db.session.commit.assert_called_once()
            self.assertEqual(response.status_code, 201)

    @patch('client.view.Client')
    @patch('client.view.clients_schema')
    def test_get_clients_success(self, mock_clients_schema, mock_client):
        mock_client_instance1 = MagicMock(name='Client 1', email='client1@example.com')
        mock_client_instance2 = MagicMock(name='Client 2', email='client2@example.com')
        mock_client.query.all.return_value = [mock_client_instance1, mock_client_instance2]
        mock_clients_schema.dump.return_value = {'teste': 'teste'}

        with app.app_context():
            token = create_access_token(identity='user_id')
            response = self.app.get('/clients', headers={'Authorization': f'Bearer {token}'})
            mock_client.query.all.assert_called_once()
            mock_clients_schema.dump.assert_called_once_with([mock_client_instance1, mock_client_instance2])
            self.assertEqual(response.status_code, 200)

    @patch('client.view.Client')
    def test_get_clients_empty(self, mock_client):
        mock_client.query.all.return_value = []
        with app.app_context():
            token = create_access_token(identity='user_id')
            response = self.app.get('/clients', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
