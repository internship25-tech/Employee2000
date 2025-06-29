
import logging
from link import GOOGLE_DRIVE_FILE_LINK
from run_scraper import FileDownloader

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        downloader = FileDownloader(GOOGLE_DRIVE_FILE_LINK)
        file_content = downloader.download_file()

        # Save file as binary (you can rename or process based on actual file type)
        with open("downloaded_file", "wb") as f:
            f.write(file_content.read())
            logging.info("Downloaded file saved as 'downloaded_file'.")

    except Exception as e:
        logging.error(f"Failed to complete download process: {e}")
