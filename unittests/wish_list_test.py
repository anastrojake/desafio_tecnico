import unittest
from unittest.mock import patch, MagicMock
from client.view import app
from flask_jwt_extended import create_access_token


class TestGetWishList(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('client.view.WishList')
    @patch('client.view.get_product_details')
    def test_get_wish_list(self, mock_get_product_details, mock_query):
        mock_wish_list_items = [
            MagicMock(product_id=123),
            MagicMock(product_id=456)
        ]
        mock_query.filter_by.return_value.all.return_value = mock_wish_list_items
        mock_product_details_123 = {
            'id_product': 123,
            'title': 'Test Product 123',
            'price': 99.99,
            'image': 'http://example.com/image123.jpg',
            'reviewScore': 4.5
        }
        mock_product_details_456 = {
            'id_product': 456,
            'title': 'Test Product 456',
            'price': 129.99,
            'image': 'http://example.com/image456.jpg',
            'reviewScore': 3.8
        }
        mock_get_product_details.side_effect = [
            mock_product_details_123,
            mock_product_details_456
        ]
        with self.app.application.app_context():
            token = create_access_token(identity='user_id')
            response = self.app.get('/wish-list/1', headers={'Authorization': f'Bearer {token}'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['id_product'], 123)
        self.assertEqual(response.json[1]['id_product'], 456)


if __name__ == '__main__':
    unittest.main()
