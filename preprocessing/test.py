import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import pandas as pd

from preprocessing import Preprocessor, REQUIRED_FIELDS


class TestPreprocessor(unittest.TestCase):

    def setUp(self):
        self.valid_csv_data = """Employee ID,First Name,Last Name,Email,Job Title,Phone Number,Hire Date
        101,John,Doe,john@example.com,Engineer,1234567890,2021-01-01
        102,Jane,Smith,jane@example.com,Manager,9876543210,2022-02-02"""

        self.invalid_csv_data = """ID,Name,Contact
        1,Alice,1111"""

    # Test Case 2: Verify CSV File Extraction
    def test_csv_file_extraction(self):
        file_bytes = BytesIO(self.valid_csv_data.encode('utf-8'))
        preprocessor = Preprocessor(file_bytes)
        df = preprocessor.parse_file()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertListEqual(df.columns.tolist(), REQUIRED_FIELDS)
        self.assertEqual(len(df), 2)

    # Test Case 3: Validate File Type and Format
    def test_file_type_detection_csv(self):
        file_bytes = BytesIO(self.valid_csv_data.encode('utf-8'))
        preprocessor = Preprocessor(file_bytes)
        file_type = preprocessor.detect_file_type()
        self.assertEqual(file_type, 'csv')

    # Test Case 4: Validate Data Structure
    def test_data_structure_validation(self):
        file_bytes = BytesIO(self.valid_csv_data.encode('utf-8'))
        preprocessor = Preprocessor(file_bytes)
        df = preprocessor.parse_file()

        self.assertFalse(df.isnull().any().any(), "DataFrame contains nulls in required fields")
        self.assertSetEqual(set(df.columns.tolist()), set(REQUIRED_FIELDS))

    # Test Case 5: Handle Missing or Invalid Fields
    def test_missing_fields_raises_error(self):
        file_bytes = BytesIO(self.invalid_csv_data.encode('utf-8'))
        preprocessor = Preprocessor(file_bytes)

        with self.assertRaises(ValueError) as context:
            preprocessor.parse_file()

        self.assertIn("Missing required fields", str(context.exception))


unittest.main()
