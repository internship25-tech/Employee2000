# preprocessing/preprocessing.py

import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
import logging
import re

REQUIRED_FIELDS = [
    'Employee ID', 'First Name', 'Last Name',
    'Email', 'Job Title', 'Phone Number', 'Hire Date'
]

class Preprocessor:
    def __init__(self, file_bytes: BytesIO):
        self.file_bytes = file_bytes

    def detect_file_type(self):
        try:
            pd.read_csv(self.file_bytes)
            self.file_bytes.seek(0)
            return 'csv'
        except Exception:
            self.file_bytes.seek(0)

        try:
            pd.read_excel(self.file_bytes)
            self.file_bytes.seek(0)
            return 'excel'
        except Exception:
            self.file_bytes.seek(0)

        try:
            pd.read_json(self.file_bytes)
            self.file_bytes.seek(0)
            return 'json'
        except Exception:
            self.file_bytes.seek(0)

        try:
            ET.parse(self.file_bytes)
            self.file_bytes.seek(0)
            return 'xml'
        except Exception:
            self.file_bytes.seek(0)

        return 'unknown'

    def parse_file(self):
        file_type = self.detect_file_type()
        logging.info(f"Detected file type: {file_type.upper()}")

        if file_type == 'csv':
            df = pd.read_csv(self.file_bytes)
        elif file_type == 'excel':
            df = pd.read_excel(self.file_bytes)
        elif file_type == 'json':
            df = pd.read_json(self.file_bytes)
        elif file_type == 'xml':
            return self._parse_xml()
        else:
            raise ValueError("Unsupported or unknown file format.")

        return self._map_and_validate_fields(df)

    def _parse_xml(self):
        try:
            tree = ET.parse(self.file_bytes)
            root = tree.getroot()
            records = []
            for emp in root.findall('.//employee'):
                record = {}
                for field in REQUIRED_FIELDS:
                    tag = field.replace(" ", "").lower()
                    el = emp.find(tag)
                    record[field] = el.text if el is not None else None
                records.append(record)
            df = pd.DataFrame(records)
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse XML: {e}")

    def _normalize_column(self, name: str):
        name = name.lower()
        name = re.sub(r'[^a-z0-9]', '', name)  # remove spaces and punctuation
        return name

    def _map_and_validate_fields(self, df: pd.DataFrame):
        logging.info("Mapping fields to standard format...")
        normalized_df = {self._normalize_column(col): col for col in df.columns}

        aliases = {
            'employeeid': ['employeeid', 'empid', 'userid', 'user_id'],
            'firstname': ['firstname', 'fname', 'first'],
            'lastname': ['lastname', 'lname', 'last'],
            'email': ['email', 'emailaddress'],
            'jobtitle': ['jobtitle', 'position', 'role'],
            'phonenumber': ['phonenumber', 'phone', 'mobile'],
            'hiredate': ['hiredate', 'startdate', 'doj', 'dateofbirth', 'dob']
        }

        mapped_columns = {}
        for field in REQUIRED_FIELDS:
            normalized_field = self._normalize_column(field)
            found = False
            for alias in aliases.get(normalized_field, []):
                if alias in normalized_df:
                    mapped_columns[field] = normalized_df[alias]
                    found = True
                    break
            if not found:
                logging.warning(f"Could not find a match for: {field}")

        missing = [field for field in REQUIRED_FIELDS if field not in mapped_columns]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        df_renamed = df.rename(columns={v: k for k, v in mapped_columns.items()})
        return df_renamed[REQUIRED_FIELDS]
