# Employee Data Scraper & Preprocessor

This project is designed to scrape and preprocess employee data from files hosted on Google Drive. It supports various file formats and prepares the data for ingestion into a data warehouse.

## User Story

**Title:** Scraping Employee Data from Google Drive File

As a developer,  
I want to scrape employee data from a Google Drive file URL,  
so that I can ingest the data into our data warehouse for further analysis.

## Features

- Download file from a Google Drive URL with retry logic
- Detect and parse multiple file formats:
  - CSV
  - Excel
  - JSON
  - XML
- Normalize and map fields to a standard structure
- Validate required employee fields
- Error logging and failure handling

## Required Employee Fields

- Employee ID  
- First Name  
- Last Name  
- Email  
- Job Title  
- Phone Number  
- Hire Date

## File Structure

employee_2000/
├── ingestion/
│ └── run_scraper.py
├── preprocessing/
│ └── preprocessing.py
└── tests/
├── test_run_scraper.py
└── test_preprocessing.py

shell
Copy
Edit

## Usage

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
Dependencies include: pandas, openpyxl, requests

Step 2: Run the Scraper
python
Copy
Edit
from ingestion.run_scraper import FileDownloader
from preprocessing.preprocessing import Preprocessor

url = "https://drive.google.com/uc?id=FILE_ID&export=download"
downloader = FileDownloader(url)
file_bytes = downloader.download_file()

preprocessor = Preprocessor(file_bytes)
df = preprocessor.parse_file()

print(df.head())
Running Tests
Make sure you're in the project root directory (where ingestion/, preprocessing/, and tests/ exist):

bash
Copy
Edit
# On PowerShell
$env:PYTHONPATH="."
python -m unittest discover tests
Or with pytest:

bash
Copy
Edit
pytest tests/ -v
Test Coverage
File download retry and failure

File type detection (CSV, Excel, JSON, XML)

Field normalization and alias mapping

Required field validation

XML parsing logic

Future Enhancements
Add support for compressed files (ZIP, GZ)

Field inference using ML for unknown formats

CLI wrapper or web dashboard