import unittest
from unittest.mock import patch, MagicMock
from run_scraper import FileDownloader, RETRY_LIMIT
from io import BytesIO
import requests


class TestFileDownloader(unittest.TestCase):
    def setUp(self):
        self.url = "https://drive.google.com/uc?id=demo-id&export=download"
        self.downloader = FileDownloader(self.url)

    @patch('run_scraper.requests.Session.get')
    def test_successful_csv_download(self, mock_get):
        """Test Case 1: Verify CSV File Download"""

        # Mock response with content
        mock_response = MagicMock()
        mock_response.content = b"Employee ID,First Name,Last Name\n123,John,Doe"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.downloader.download_file()

        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.getvalue(), b"Employee ID,First Name,Last Name\n123,John,Doe")
        self.assertEqual(mock_get.call_count, 1)

    @patch('run_scraper.requests.Session.get')
    def test_retry_then_success(self, mock_get):
        """Test Case 2: Retry logic succeeds after failure"""

        # Simulate failure on first call, success on second
        mock_response_fail = MagicMock()
        mock_response_fail.raise_for_status.side_effect = requests.HTTPError("503 Service Unavailable")

        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.content = b"valid,data"

        mock_get.side_effect = [mock_response_fail, mock_response_success]

        result = self.downloader.download_file()
        self.assertEqual(result.getvalue(), b"valid,data")
        self.assertEqual(mock_get.call_count, 2)

    @patch('run_scraper.requests.Session.get')
    def test_invalid_url_download_failure(self, mock_get):
        """Test Case 5: Handle unreachable URL or connection errors"""

        mock_get.side_effect = requests.ConnectionError("Failed to connect")

        with self.assertRaises(Exception) as context:
            self.downloader.download_file()

        self.assertIn("File download failed after multiple retries", str(context.exception))
        self.assertEqual(mock_get.call_count, RETRY_LIMIT)

    @patch('run_scraper.requests.Session.get')
    def test_empty_file_download_error(self, mock_get):
        """Test Case 5: Handle empty file download"""

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b""
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            self.downloader.download_file()

        self.assertIn("Empty file received", str(context.exception))
        self.assertEqual(mock_get.call_count, 1)

    @patch('run_scraper.requests.Session.get')
    def test_http_error_raises_exception(self, mock_get):
        """Test Case 5: Handle HTTP 4xx/5xx errors"""

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with self.assertRaises(Exception):
            self.downloader.download_file()

        self.assertEqual(mock_get.call_count, RETRY_LIMIT)


if __name__ == "__main__":
    unittest.main()
