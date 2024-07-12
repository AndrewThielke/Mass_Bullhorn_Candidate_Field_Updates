'''
Skills Data Integration
'''
import logging
import os
import urllib.parse
import urllib.request
from typing import Dict, List, Union

import azure.functions as func
import requests
from azure.storage.blob import BlobServiceClient
from helper_classes.attain_and_stage_skillsdata import SkillsDataOperations
from helper_classes.bullhorn_authentication import BullhornAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BullhornDataIntegration(object):
	'''
	Takes Login Credentials & Skills Data | Inserts Data Into Bullhorn

	Methods:
	__init__(self, candidate_modification_data: List[List[Union[str, int]]], bullhorn_authentication_credentials: dict): Initializes the class with candidate data and Bullhorn credentials.
	bullhornCandidateModifications(self) -> None: Modifies candidates on Bullhorn in specified UI entry fields.
	'''

	def __init__(self, candidate_modification_data: List[Dict[str, Union[str, int]]], bullhorn_authentication_credentials: dict):
		logging.info("Initializing BullhornDataIntegration class.")
		self.candidate_modification_data = candidate_modification_data
		self.bullhorn_authentication_credentials = bullhorn_authentication_credentials

	def bullhornCandidateModifications(self) -> None:
		"""
		Modifies Candidates on Bullhorn in specified UI entry fields.
		This method iterates through the candidate modification data and updates the corresponding
		fields in Bullhorn using the provided authentication credentials. It logs any errors
		encountered during the process and informs management if a Bullhorn ID is missing.
		"""
		logging.info("Starting candidate modifications on Bullhorn.")
		
		with requests.Session() as session:
			for engineerdata in [data for data in self.candidate_modification_data if data['Basic Information'][3] != "None" or data['Basic Information'][4] != "None"]:
				if engineerdata['Basic Information'][0] == "None" and engineerdata['Basic Information'][3] != "None":
					logging.warning(f"Employee: {engineerdata['Basic Information'][3]} (NEEDS BULLHORN ID ENTERED)")
					continue
				
				rest_url = self.bullhorn_authentication_credentials['rest_url'] + 'entity/Candidate/' + str(engineerdata['Basic Information'][0])
				data = {
					'customText3': engineerdata['Basic Information'][5],  # Project Role
					'customText31': engineerdata['Basic Information'][7],  # OEM Experience
					'customText21': engineerdata['Industry Experience'],
					'customTextBlock5': engineerdata['Domains'],
					'customTextBlock10': engineerdata['Standards'],
					'customTextBlock2': engineerdata['Skills'],
					'customTextBlock6': engineerdata['Languages'],
					'customTextBlock7': engineerdata['Tools'],
				}
				
				if isinstance(engineerdata['Basic Information'][8], int):
					data['customFloat3'] = engineerdata['Basic Information'][8]  # Work Experience

				try:
					response = session.post(
						rest_url,
						params={'BhRestToken': self.bullhorn_authentication_credentials['BhRestToken']},
						headers={'Content-Type': 'application/json'},
						json=data,
					)
					response.raise_for_status()
					logging.info(f"Successfully accessed & modified {engineerdata['Basic Information'][3]}'s profile.")
				
				except requests.exceptions.HTTPError as e:
					logging.error(f"HTTPError: {e.response.status_code} - {e.response.text}")
					logging.error(f"Failed URL: {e.request.url}")
				
				except requests.exceptions.RequestException as e:
					logging.error(f"RequestException: {e}")
			   
				except Exception as e:
					logging.error(f"An unexpected error occurred: {e}")

		logging.info("Candidate modifications on Bullhorn completed.")





app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="BullhornMassCandidateUpdate")
def BullhornMassCandidateUpdate(req: func.HttpRequest) -> func.HttpResponse:
    '''
    Summary Description: This Python function is an Azure Function that retrieves an Excel file 
            from Azure Blob Storage, manipulates and stages the data, 
            authenticates to Bullhorn REST API and integrates the data to Bullhorn.

    -- CONTROL FLOW
        -- The function starts by attaining the Excel file from Azure Blob Storage.
        -- The data from the Excel file is manipulated and staged using SkillsDataOperations class.
        -- The function then authenticates the connection to Bullhorn REST API using BullhornAuth class.
        -- The data is integrated into Bullhorn using BullhornDataIntegration class.
        -- The function returns a success message indicating the data has been integrated into Bullhorn.
    '''
    
    logging.info('MASS BULLHORN CANDIDATE UPDATE FUNCTION RECEIVED REQUEST.')
    
    # Step 1: Retrieve the Excel file from Azure Blob Storage
    try:
        logging.info('Attaining Blob...')
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=os.getenv('AZURE_BLOB_CONNECTION_STRING'))
        skillsblob_client = blob_service_client.get_blob_client(container='engineerskills-file', blob='skillsSurveyData.xlsx')         
        skills_blob_data = skillsblob_client.download_blob().readall()
        logging.info('Attained Blob successfully.')
    
    except Exception as e:
        logging.error(f"Failed to attain blob: {e}")
        return func.HttpResponse(f"Failed to attain blob: {e}", status_code=500)
    
    # Step 2: Manipulate and stage the data
    try:
        logging.info('Data Operations Starting...')
        skills_operations = SkillsDataOperations()
        headers, row_vals = skills_operations.survey_data_preparation(skills_blob_data)
        staged_row_values = skills_operations.stage_row_values(headers, row_vals)
        transformed_staged_data = skills_operations.map_work_experience_values(staged_row_values)
        production_data = skills_operations.nested_lists_to_csv_strings(transformed_staged_data)
        logging.info('Data Operations Complete.')
    
    except Exception as e:
        logging.error(f'Failed to prepare or stage skills data: {e}')
        return func.HttpResponse(f'Failed Data Operations: {e}', status_code=500)        
    
    # Step 3: Authenticate to Bullhorn REST API
    try:
        logging.info('Bullhorn Authentication Started.')
        bullhorn_auth_instance = BullhornAuth()
        auth_code = bullhorn_auth_instance.attain_auth_code()
        access_token = bullhorn_auth_instance.get_access_token(auth_code)
        creds = bullhorn_auth_instance.api_login(access_token)
        
        if not creds:
            logging.error('Bullhorn Authentication Process Failed: creds variable is NONE - Should Be a Dictionary containing BhRestToken and restUrl.')
            return func.HttpResponse('Failed Bullhorn Authentication: Missing credentials.', status_code=500)
        
        logging.info('Bullhorn Authentication Complete.')
    
    except Exception as e:
        logging.error(f'Failed to Authenticate Bullhorn Access: {e}')
        return func.HttpResponse(f'Failed to Authenticate Bullhorn Access: {e}', status_code=500)
    
    # Step 4: Integrate data into Bullhorn
    try:
        logging.info('Bullhorn Data Integration Started.')
        data_integration_instance = BullhornDataIntegration(candidate_modification_data=production_data, bullhorn_authentication_credentials=creds)
        data_integration_instance.bullhornCandidateModifications()
        logging.info('Bullhorn Data Integration Complete.')
   
    except Exception as e:
        logging.error(f'Failed to Integrate Data To Bullhorn: {e}')
        return func.HttpResponse(f'Failed to Integrate Data To Bullhorn: {e}', status_code=500)
    
    return func.HttpResponse('Successful Skills Matrix Function Execution. Check Bullhorn & Compare Excel File To Validate Submitted Data.', status_code=200)