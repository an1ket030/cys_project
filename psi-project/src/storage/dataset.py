"""
Dataset generation and basic operations.
"""
import random
from typing import Tuple, List

class Dataset:
    @staticmethod
    def generate_contacts(size_a: int, size_b: int, overlap: int) -> Tuple[List[str], List[str]]:
        """Generate synthetic contacting lists."""
        if overlap > min(size_a, size_b):
            raise ValueError("Overlap cannot be larger than the smaller set size")
            
        shared = [f"shared_user{i}@example.com" for i in range(overlap)]
        unique_a = [f"alice_only_{i}@example.com" for i in range(size_a - overlap)]
        unique_b = [f"bob_only_{i}@example.com" for i in range(size_b - overlap)]
        
        contacts_a = shared + unique_a
        contacts_b = shared + unique_b
        
        random.shuffle(contacts_a)
        random.shuffle(contacts_b)
        
        return contacts_a, contacts_b
