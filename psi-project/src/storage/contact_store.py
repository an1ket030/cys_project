"""
Contact list management.
"""
from typing import List
import csv
import logging

logger = logging.getLogger(__name__)

class ContactStore:
    def __init__(self, identifier: str = "default"):
        self.identifier = identifier
        self.contacts: List[str] = []

    def load_from_list(self, contacts: List[str]):
        """Load contacts from a memory list."""
        self.contacts = contacts.copy()
        logger.info(f"Loaded {len(self.contacts)} contacts via list for {self.identifier}")

    def load_from_csv(self, filepath: str, column: str = 'identifier'):
        """Load contacts from a CSV file."""
        loaded = []
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if column not in reader.fieldnames and reader.fieldnames:
                    # fallback to first column if 'identifier' is missing
                    column = reader.fieldnames[0]
                
                for row in reader:
                    if row.get(column):
                        loaded.append(row[column].strip())
                        
            self.contacts = loaded
            logger.info(f"Loaded {len(self.contacts)} contacts from {filepath} for {self.identifier}")
        except Exception as e:
            logger.error(f"Failed to load specific CSV {filepath}: {e}")
            raise
