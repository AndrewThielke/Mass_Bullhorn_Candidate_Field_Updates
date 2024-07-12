import os
import logging
import requests
import urllib.parse
from datetime import datetime, timedelta

from helper_classes.bullhorn_authentication import BullhornAuth

"""
Bullhorn Authentication Class

Pre-reqs:
	1. Install the following environment variables prior to execution:
		a. auth_url
		b. rest_url
		c. client_id
		d. client_secret
		e. bhusername
		f. bhpassword
		
		Tip: Include these environment variables in the environment setup to automate this during execution.
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BullhornAuth:
	'''
	Authenticates/Logins To The Bullhorn Access Point For API Queries

	Methods:
		__init__(self): Constructor method that initializes the BullhornAuth class with environment variables and sets instance variables to None.
		attain_auth_code(self) -> str: Method that attains the Bullhorn authentication code and returns it as a string.
		get_access_token(self, auth_code: str = None) -> str: Method that attains the Bullhorn access token using either the authorization code or the refresh token.
		api_login(self, access_token: str) -> dict: Method that logs into the Bullhorn Rest API and returns content for further Bullhorn Rest API calls as a dictionary.
	'''

	def __init__(self):
		# If you are returning None - Make sure these are set OR Keys/Passwords are correct
		self.auth_url = os.environ.get("auth_url", "https://auth.bullhornstaffing.com/oauth")
		self.rest_url = os.environ.get("rest_url")
		self.client_id = os.environ.get("client_id")
		self.client_secret = os.environ.get("client_secret")
		self.username = os.environ.get("bhusername")
		self.password = os.environ.get("bhpassword")
		self.refresh_token = None
		self.refresh_token_expiry = None
		logging.info("Initialized BullhornAuth class.")

	def attain_auth_code(self) -> str:
		'''
		Attains Bullhorn Authentication Code
		Returns: 
			auth_code (str): Authentication Code Used To Get Access Token Info
		'''
		auth_code_params = dict(
			client_id=self.client_id,
			response_type='code',
			username=self.username,
			password=self.password,
			action='Login'
		)

		url = self.auth_url + '/authorize'
		try:
			req = requests.get(url, params=auth_code_params)
			req.raise_for_status()
			query_response = urllib.parse.urlparse(req.url).query
			query_dictionary = urllib.parse.parse_qs(query_response)
		
			if 'code' in query_dictionary:
				auth_code = query_dictionary['code'][0]
				logging.info('Successfully retrieved authorization code.')
				return auth_code
		
			else:
				logging.error('AuthCodeError: The code was not found in query_dictionary')
				raise ValueError('AuthCodeError: The code was not found in query_dictionary')
		
		except requests.exceptions.RequestException as e:
			logging.error(f'An error occurred while trying to get the authorization code: {e}')
			raise

	def get_access_token(self, auth_code: str = None) -> str:
		'''
		Attains Bullhorn Access Token using either authorization code or refresh token
		
		Args: 
			auth_code: str - The authorization code, optional
		
		Return: 
			str - The access token
		'''
		params = {
			"client_id": self.client_id,
			"client_secret": self.client_secret,
		}

		if auth_code:
			params.update({
				"code": auth_code,
				"grant_type": "authorization_code",
			})
		elif self.refresh_token:
			params.update({
				"refresh_token": self.refresh_token,
				"grant_type": "refresh_token",
			})
		else:
			raise ValueError("Either auth_code or refresh_token must be provided")

		url = self.auth_url + "/token"
		
		try:
			req = requests.post(url, params=params)
			req.raise_for_status()
			response_data = req.json()
			self.refresh_token = response_data.get('refresh_token')
			
			if response_data.get('expires_in'):
				self.refresh_token_expiry = datetime.utcnow() + timedelta(seconds=response_data['expires_in'])
			logging.info('Successfully retrieved the access token.')
			return response_data.get('access_token')
		
		except requests.exceptions.RequestException as e:
			logging.error(f'Error getting access token: {e}')
			raise

	def api_login(self, access_token: str) -> dict:
		'''
		Logs into Bullhorn Rest API
		
		Args: 
			access_token (str): Contains either new or refresh access token. 
		
		Returns: 
			dict: Content for further Bullhorn Rest API calls
		'''
		url = self.rest_url + '/login'
		api_login_params = {
			'version': '*',
			'access_token': access_token
		}
	   
		try:
			req = requests.post(url, params=api_login_params)
			req.raise_for_status()
			logging.info('Successfully logged into REST API.')
			return req.json()
		
		except requests.exceptions.HTTPError as err:
			logging.error(f'HTTP error: {err}')
			raise
		
		except requests.exceptions.RequestException as e:
			logging.error(f'Request error: {e}')
			raise
		
		except Exception as e:
			logging.error(f'Unexpected error: {e}')
			raise