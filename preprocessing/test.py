import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from io import BytesIO
from preprocessing import Preprocessor, REQUIRED_FIELDS


class TestPreprocessor(unittest.TestCase):
    def create_csv_bytes(self, content: str):
        return BytesIO(content.encode('utf-8'))

    def test_detect_csv_type(self):
        file_content = "Employee ID,First Name,Last Name,Email,Job Title,Phone Number,Hire Date\n1,John,Doe,john@example.com,Dev,1234567890,2023-01-01"
        processor = Preprocessor(self.create_csv_bytes(file_content))
        self.assertEqual(processor.detect_file_type(), "csv")

    def test_parse_valid_csv(self):
        csv_data = """Employee ID,First Name,Last Name,Email,Job Title,Phone Number,Hire Date
1,John,Doe,john@example.com,Developer,1234567890,2023-01-01"""
        processor = Preprocessor(self.create_csv_bytes(csv_data))
        df = processor.parse_file()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertListEqual(list(df.columns), REQUIRED_FIELDS)
        self.assertEqual(df.iloc[0]["First Name"], "John")

    def test_parse_with_aliases(self):
        csv_data = """emp_id,fname,lname,emailaddress,role,mobile,startdate
1,Jane,Smith,jane@example.com,Manager,9876543210,2022-01-15"""
        processor = Preprocessor(self.create_csv_bytes(csv_data))
        df = processor.parse_file()

        self.assertListEqual(list(df.columns), REQUIRED_FIELDS)
        self.assertEqual(df.iloc[0]["Job Title"], "Manager")
        self.assertEqual(df.iloc[0]["Hire Date"], "2022-01-15")

    def test_missing_required_fields(self):
        bad_csv = """ID,Name\n1,Test"""
        processor = Preprocessor(self.create_csv_bytes(bad_csv))

        with self.assertRaises(ValueError) as context:
            processor.parse_file()

        self.assertIn("Missing required fields", str(context.exception))

    def test_detect_unknown_format(self):
        unknown_data = b"This is not a valid format"
        processor = Preprocessor(BytesIO(unknown_data))
        self.assertEqual(processor.detect_file_type(), "unknown")

    def test_parse_xml_valid(self):
        xml_data = """
        <root>
          <employee>
            <employeeid>1</employeeid>
            <firstname>Sam</firstname>
            <lastname>Roy</lastname>
            <email>sam@abc.com</email>
            <jobtitle>Engineer</jobtitle>
            <phonenumber>1231231234</phonenumber>
            <hiredate>2023-05-01</hiredate>
          </employee>
        </root>
        """
        processor = Preprocessor(BytesIO(xml_data.encode('utf-8')))
        df = processor.parse_file()

        self.assertListEqual(list(df.columns), REQUIRED_FIELDS)
        self.assertEqual(df.iloc[0]['First Name'], 'Sam')

    def test_parse_xml_with_missing_fields(self):
        xml_data = """
        <root>
          <employee>
            <employeeid>1</employeeid>
            <firstname>Ana</firstname>
          </employee>
        </root>
        """
        processor = Preprocessor(BytesIO(xml_data.encode('utf-8')))
        df = processor.parse_file()

        self.assertIn("First Name", df.columns)
        self.assertIsNone(df.iloc[0]['Last Name'])  # missing mapped field

    @patch('pandas.read_excel')
    def test_detect_excel_type(self, mock_read_excel):
        mock_read_excel.return_value = pd.DataFrame({'A': [1]})
        dummy_bytes = BytesIO(b"dummy")
        processor = Preprocessor(dummy_bytes)
        self.assertEqual(processor.detect_file_type(), "excel")


if __name__ == "__main__":
    unittest.main()
