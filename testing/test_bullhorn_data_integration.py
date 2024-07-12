"""
Bullhorn Data Integration Unit Tests

Pre-reqs:
    1. Ensure the BullhornDataIntegration class is correctly implemented.
    2. The following environment variables should be set:
        a. rest_url
        b. client_id
        c. client_secret
        d. bhusername
        e. bhpassword

    Tip: Make sure to mock external dependencies for isolated testing.
"""

import unittest
from unittest.mock import patch, Mock
import requests
from main import BullhornDataIntegration

class TestBullhornDataIntegration(unittest.TestCase):
    """
    Testing suite for BullhornDataIntegration class.
    
    This suite covers all critical functionalities to ensure Bullhorn data integration
    is handled correctly. Mocking is used extensively to simulate real-world scenarios
    without making actual API calls.
    """

    def setUp(self):
        self.candidate_modification_data = [
            {
                'Basic Information': ['123', 'John Doe', '10', 'Developer', 'OEM', 'Project Role', 'OEM Experience', 'Industry Experience', 'Domains', 'Standards', 'Skills', 'Languages', 'Tools']
            }
        ]
        self.bullhorn_authentication_credentials = {
            'rest_url': 'https://rest.bullhornstaffing.com/',
            'BhRestToken': 'fake_token'
        }
        self.integration = BullhornDataIntegration(self.candidate_modification_data, self.bullhorn_authentication_credentials)

    @patch('bullhorn_data_integration.requests.Session.post')
    def test_bullhornCandidateModifications_success(self, mock_post):
        """
        Test successful modification of candidates on Bullhorn.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.integration.bullhornCandidateModifications()

        self.assertTrue(mock_post.called)
        mock_post.assert_called_with(
            'https://rest.bullhornstaffing.com/entity/Candidate/123',
            params={'BhRestToken': 'fake_token'},
            headers={'Content-Type': 'application/json'},
            json={
                'customText3': 'Project Role',
                'customText31': 'OEM Experience',
                'customText21': 'Industry Experience',
                'customTextBlock5': 'Domains',
                'customTextBlock10': 'Standards',
                'customTextBlock2': 'Skills',
                'customTextBlock6': 'Languages',
                'customTextBlock7': 'Tools',
                'customFloat3': 10
            }
        )

    @patch('bullhorn_data_integration.requests.Session.post')
    def test_bullhornCandidateModifications_http_error(self, mock_post):
        """
        Test handling of HTTP errors during candidate modification.
        """
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=Mock(status_code=400))
        mock_post.return_value = mock_response

        with self.assertLogs(level='ERROR'):
            self.integration.bullhornCandidateModifications()

    @patch('bullhorn_data_integration.requests.Session.post')
    def test_bullhornCandidateModifications_request_exception(self, mock_post):
        """
        Test handling of request exceptions during candidate modification.
        """
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        with self.assertLogs(level='ERROR'):
            self.integration.bullhornCandidateModifications()

    @patch('bullhorn_data_integration.requests.Session.post')
    def test_bullhornCandidateModifications_general_exception(self, mock_post):
        """
        Test handling of general exceptions during candidate modification.
        """
        mock_post.side_effect = Exception("Unexpected error")

        with self.assertLogs(level='ERROR'):
            self.integration.bullhornCandidateModifications()

if __name__ == '__main__':
    
    unittest.main()