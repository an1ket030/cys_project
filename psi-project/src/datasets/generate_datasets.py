"""
Generate realistic synthetic contact datasets for PSI experiments.
"""
import csv
import random
import os
import logging
from typing import Tuple, List

from ..storage.dataset import Dataset

logger = logging.getLogger(__name__)

class ContactGenerator:
    """Generate realistic contact identifiers."""
    EMAIL_PROVIDERS = ['gmail.com', 'yahoo.com', 'outlook.com', 'example.com', 'company.com']
    FIRST_NAMES = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'hank']
    LAST_NAMES = ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia']

    @staticmethod
    def generate_email(unique_suffix: str = "") -> str:
        first = random.choice(ContactGenerator.FIRST_NAMES)
        last = random.choice(ContactGenerator.LAST_NAMES)
        provider = random.choice(ContactGenerator.EMAIL_PROVIDERS)
        return f"{first}.{last}{unique_suffix}@{provider}"

class DatasetGenerator:
    """Generate contact datasets with specified overlap."""
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        
    @staticmethod
    def generate_pair(size_a: int, size_b: int, overlap: int) -> Tuple[List[str], List[str]]:
        if overlap > min(size_a, size_b):
            raise ValueError(f"Overlap ({overlap}) cannot exceed min(size_a, size_b)")

        shared_contacts = set()
        for i in range(overlap):
            shared_contacts.add(ContactGenerator.generate_email(unique_suffix=f"_shared_{i}"))

        contacts_a = list(shared_contacts)
        while len(contacts_a) < size_a:
            contact = ContactGenerator.generate_email(unique_suffix=f"_a_{len(contacts_a)}")
            if contact not in contacts_a:
                contacts_a.append(contact)

        contacts_b = list(shared_contacts)
        while len(contacts_b) < size_b:
            contact = ContactGenerator.generate_email(unique_suffix=f"_b_{len(contacts_b)}")
            if contact not in contacts_b:
                contacts_b.append(contact)

        random.shuffle(contacts_a)
        random.shuffle(contacts_b)

        return contacts_a, contacts_b

    @staticmethod
    def save_to_csv(contacts: List[str], filename: str):
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['identifier', 'type', 'source'])
            for contact in contacts:
                contact_type = 'email' if '@' in contact else 'username'
                writer.writerow([contact, contact_type, 'generated'])
        logger.info(f"Saved {len(contacts)} contacts to {filename}")
