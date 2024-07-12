"""
Skills Data Operations Unit Tests

Pre-reqs:
    1. Ensure the SkillsDataOperations class is correctly implemented.
    2. The following environment variables should be set:
        a. azure_blob_connection_string
        b. azure_blob_container_name

    Tip: Make sure to mock external dependencies for isolated testing.
"""

import unittest
from unittest.mock import patch, Mock
import datetime

from helper_classes.attain_and_stage_skillsdata import SkillsDataOperations

class TestSkillsDataOperations(unittest.TestCase):
    """
    Testing suite for SkillsDataOperations class.
    
    This suite covers all critical functionalities to ensure skills data operations
    are handled correctly. Mocking is used extensively to simulate real-world scenarios
    without making actual API calls or file reads.
    """

    def setUp(self):
        self.skills_operations = SkillsDataOperations()


    @patch('skills_data_operations.load_workbook')
    def test_get_column_headers(self, mock_load_workbook):
        """
        Test the retrieval and processing of column headers from the worksheet.
        """
        mock_worksheet = Mock()
        mock_worksheet[1] = [Mock(value='Header1'), Mock(value='Header2')]

        headers = self.skills_operations.get_column_headers(mock_worksheet)
        self.assertEqual(headers, ['Header1', 'Header2'])


    @patch('skills_data_operations.load_workbook')
    def test_get_row_values(self, mock_load_workbook):
        """
        Test the retrieval and processing of row values from the worksheet.
        """
        mock_worksheet = Mock()
        mock_worksheet.iter_rows.return_value = [
            [Mock(value='value1'), Mock(value=datetime.datetime(2023, 1, 1))]
        ]

        row_values = self.skills_operations.get_row_values(mock_worksheet)
        self.assertEqual(row_values, [['value1', '2023-01-01']])


    @patch('skills_data_operations.load_workbook')
    def test_survey_data_preparation(self, mock_load_workbook):
        """
        Test the preparation of survey data from an Excel file.
        """
        mock_worksheet = Mock()
        mock_load_workbook.return_value.active = mock_worksheet
        mock_worksheet[1] = [Mock(value='Header1'), Mock(value='Header2')]
        mock_worksheet.iter_rows.return_value = [
            [Mock(value='value1'), Mock(value=datetime.datetime(2023, 1, 1))]
        ]

        blob_obj = b'some bytes representing an excel file'
        col_headers, row_values = self.skills_operations.survey_data_preparation(blob_obj)
        self.assertEqual(col_headers, ['Header1', 'Header2'])
        self.assertEqual(row_values, [['value1', '2023-01-01']])


    def test_get_language_value(self):
        """
        Test the conversion of a language value to a customized string.
        """
        result = self.skills_operations.get_language_value('Python', '3', ['N', 'None'])
        self.assertEqual(result, 'Python (Level 3)')

        result = self.skills_operations.get_language_value('Python', 'None', ['N', 'None'])
        self.assertEqual(result, '')


    def test_stage_row_values(self):
        """
        Test the staging of row values for insertion into a Tableau data source.
        """
        header_vals = ['ID', 'Name', 'Experience', 'Project Role', 'OEM Experience', 'Industry Experience', 'Domains', 'Standards', 'Skills', 'Languages', 'Tools']
        row_vals = [['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', '3', 'Yes']]
        staged_data = self.skills_operations.stage_row_values(header_vals, row_vals)
        
        expected_output = [{
            'Basic Information': ['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes'],
            'Industry Experience': ['Industry Experience'],
            'Domains': ['Domains'],
            'Standards': ['Standards'],
            'Skills': ['Skills'],
            'Languages': ['Python (Level 3)'],
            'Tools': ['Tools']
        }]
        self.assertEqual(staged_data, expected_output)


    def test_nested_lists_to_csv_strings(self):
        """
        Test the conversion of nested lists into comma-separated strings.
        """
        data = [
            {
                'Basic Information': ['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes'],
                'Industry Experience': ['Industry Experience'],
                'Domains': ['Domains'],
                'Standards': ['Standards'],
                'Skills': ['Skills'],
                'Languages': ['Python (Level 3)'],
                'Tools': ['Tools']
            }
        ]
        result = self.skills_operations.nested_lists_to_csv_strings(data)
        expected_output = [
            {
                'Basic Information': ['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes'],
                'Industry Experience': 'Industry Experience',
                'Domains': 'Domains',
                'Standards': 'Standards',
                'Skills': 'Skills',
                'Languages': 'Python (Level 3)',
                'Tools': 'Tools'
            }
        ]
        self.assertEqual(result, expected_output)


    def test_map_work_experience_values(self):
        """
        Test the mapping of work experience descriptors to integer values.
        """
        data = [{'Basic Information': ['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes', '5 to 9']}]
        result = self.skills_operations.map_work_experience_values(data)
        expected_output = [{'Basic Information': ['1', 'John Doe', '10', 'Developer', 'Yes', 'Yes', 2]}]
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    
    unittest.main()