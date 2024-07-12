"""
Bullhorn Auth Unit Tests

Pre-reqs:
    1. Ensure the BullhornAuth class is correctly implemented.
    2. The following environment variables should be set:
        a. auth_url
        b. rest_url
        c. client_id
        d. client_secret
        e. bhusername
        f. bhpassword

    Tip: Make sure to mock external dependencies for isolated testing.
"""

import unittest
from unittest.mock import patch, Mock
import requests

from helper_classes.bullhorn_authentication import BullhornAuth


class TestBullhornAuth(unittest.TestCase):
    """
    Testing suite for BullhornAuth class.
    
    This suite covers all critical functionalities to ensure Bullhorn authentication
    is handled correctly. Mocking is used extensively to simulate real-world scenarios
    without making actual API calls.
    """

    def setUp(self):
        self.auth = BullhornAuth()
        self.auth.client_id = "test_client_id"
        self.auth.client_secret = "test_client_secret"
        self.auth.username = "test_username"
        self.auth.password = "test_password"
        self.auth.auth_url = "https://auth.bullhornstaffing.com/oauth"
        self.auth.rest_url = "https://rest.bullhornstaffing.com"


    @patch('bullhorn_auth.requests.get')
    def test_attain_auth_code_success(self, mock_get):
        """
        Test successful retrieval of the authorization code from Bullhorn.
        """
        mock_response = Mock()
        mock_response.url = 'https://auth.bullhornstaffing.com/oauth/authorize?code=auth_code'
        mock_get.return_value = mock_response

        auth_code = self.auth.attain_auth_code()
        self.assertEqual(auth_code, 'auth_code')
        mock_get.assert_called_once()
        self.assertIn('Successfully retrieved authorization code.', self._caplog.text)


    @patch('bullhorn_auth.requests.get')
    def test_attain_auth_code_failure(self, mock_get):
        """
        Test failure in retrieving the authorization code from Bullhorn.
        """
        mock_response = Mock()
        mock_response.url = 'https://auth.bullhornstaffing.com/oauth/authorize'
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            self.auth.attain_auth_code()
        mock_get.assert_called_once()
        self.assertIn('AuthCodeError: The code was not found in query_dictionary', self._caplog.text)


    @patch('bullhorn_auth.requests.post')
    def test_get_access_token_with_auth_code(self, mock_post):
        """
        Test retrieving access token using an authorization code.
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'access_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        access_token = self.auth.get_access_token(auth_code='auth_code')
        self.assertEqual(access_token, 'access_token')
        self.assertEqual(self.auth.refresh_token, 'refresh_token')
        mock_post.assert_called_once()
        self.assertIn('Successfully retrieved the access token.', self._caplog.text)


    @patch('bullhorn_auth.requests.post')
    def test_get_access_token_with_refresh_token(self, mock_post):
        """
        Test retrieving access token using a refresh token.
        """
        self.auth.refresh_token = 'existing_refresh_token'
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        access_token = self.auth.get_access_token()
        self.assertEqual(access_token, 'access_token')
        self.assertEqual(self.auth.refresh_token, 'new_refresh_token')
        mock_post.assert_called_once()
        self.assertIn('Successfully retrieved the access token.', self._caplog.text)


    @patch('bullhorn_auth.requests.post')
    def test_api_login_success(self, mock_post):
        """
        Test successful login to the Bullhorn REST API.
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'BhRestToken': 'rest_token',
            'restUrl': 'https://rest.bullhornstaffing.com'
        }
        mock_post.return_value = mock_response

        login_data = self.auth.api_login(access_token='access_token')
        self.assertIn('BhRestToken', login_data)
        self.assertIn('restUrl', login_data)
        mock_post.assert_called_once()
        self.assertIn('Successfully logged into REST API.', self._caplog.text)


    @patch('bullhorn_auth.requests.post')
    def test_api_login_failure(self, mock_post):
        """
        Test failed login to the Bullhorn REST API.
        """
        mock_post.side_effect = requests.exceptions.HTTPError("HTTP error occurred")

        with self.assertRaises(requests.exceptions.HTTPError):
            self.auth.api_login(access_token='access_token')
        self.assertIn('HTTP error occurred', self._caplog.text)



if __name__ == '__main__':
    
    unittest.main()