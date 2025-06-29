# ingestion/run_scraper.py

import logging
import time
import requests
from io import BytesIO

RETRY_LIMIT = 3
RETRY_DELAY = 2  # seconds


class FileDownloader:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def download_file(self):
        """
        Attempts to download a file from the given URL with retry logic.
        Returns a BytesIO stream of the file content on success.
        Raises an Exception after RETRY_LIMIT failures.
        """
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                logging.info(f"Attempt {attempt}: Downloading file from {self.url}...")
                response = self.session.get(self.url, timeout=10)
                response.raise_for_status()

                if not response.content:
                    raise ValueError("Empty file received.")

                logging.info("File downloaded successfully.")
                return BytesIO(response.content)

            except (requests.RequestException, ValueError) as e:
                logging.error(f"Download attempt {attempt} failed: {e}")
                if attempt < RETRY_LIMIT:
                    logging.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

        logging.critical("File download failed after multiple attempts.")
        raise Exception("File download failed after multiple retries. Please check the URL or your internet connection.")
