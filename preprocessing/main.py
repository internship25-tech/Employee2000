# preprocessing/main.py

import logging
from preprocessing import Preprocessor
from io import BytesIO
import os

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Use full path to downloaded_file in ingestion folder
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "ingestion", "downloaded_file")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        preprocessor = Preprocessor(BytesIO(file_bytes))
        employee_df = preprocessor.parse_file()

        logging.info("Employee data parsed and normalized successfully.")
        print(employee_df.head())

        output_path = os.path.join(base_dir, "preprocessing", "parsed_employees.csv")
        employee_df.to_csv(output_path, index=False)
        logging.info(f"Saved parsed employee data to '{output_path}'.")

    except Exception as e:
        logging.error(f"Preprocessing failed: {e}")
