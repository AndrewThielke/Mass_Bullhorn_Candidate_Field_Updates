# Skills Matrix

## Overview

The **Skills Matrix** is a Python-based solution designed to streamline the process of managing and integrating skills data for large teams or organizations. This script reads data from a source file (e.g., a CSV) stored in an Azure Blob, processes it column by column, and then pushes the data to Bullhorn using Bullhorn's REST API.

## Features

- **Data Integration**: Seamlessly integrates skills data from a CSV file stored in Azure Blob storage.
- **Automated Processing**: Automates the extraction, transformation, and loading (ETL) process for skills data.
- **Bullhorn API Integration**: Utilizes Bullhorn's REST API to ensure data is accurately and efficiently pushed to the Bullhorn platform.
- **Scalability**: Designed to handle large datasets, making it suitable for organizations with extensive skills data.
- **Error Handling**: Incorporates robust error handling to ensure data integrity and reliability throughout the process.

## Prerequisites

- Python 3.x
- Azure Blob Storage account and access credentials
- Bullhorn API access credentials
- Required Python libraries: `pandas`, `azure-storage-blob`, `requests`

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/AndrewThielke/Mass_Bullhorn_Candidate_Field_Updates.git
    cd full_path/Mass_Bullhorn_Candidate_Field_Updates
    ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure your environment variables:**
    - Create a `.env` file in the root directory.
    - Add your Azure Blob Storage and Bullhorn API credentials:
      ```bash
      AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
      BULHORN_CLIENT_ID="your_client_id"
      BULHORN_CLIENT_SECRET="your_client_secret"
      BULHORN_USERNAME="your_username"
      BULHORN_PASSWORD="your_password"
      ```

## Usage

1. **Prepare your CSV data:**
    - Ensure your CSV file is correctly formatted and uploaded to your Azure Blob Storage container.

2. **Run the script:**
    ```bash
    python candidate_update.py
    ```

3. **Monitor the process:**
    - The script will log its progress, including any errors encountered during the ETL process, to the console. 

## Example CSV Format

Your CSV file should be structured with columns representing different skills data fields. Here is an example format:

| Employee ID | Domains | Skills | Tools | ... |
|-------------|---------|---------|---------|-----|
| 001         | X, Y, Z  | No     | X, Z, W, Q   | ... |
| 002         | X    | X, Y, Z     | A     | ... |

*Note: 1's are "Yes" & 0's are "No".*

## Contributing

Contributions are welcome!

## Acknowledgments

- Special thanks to the open-source community for the libraries and tools used in this project.

## Contact

For any questions or issues, please open an issue in the [GitHub repository](https://github.com/AndrewThielke/Mass_Bullhorn_Candidate_Field_Updates/issues).
