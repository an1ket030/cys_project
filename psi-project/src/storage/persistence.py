"""
Result persistence utilities.
"""
import json
import os
from typing import Dict, Any, List

class Persistence:
    @staticmethod
    def save_results(data: Dict[str, Any], filepath: str):
        """Save results dict to JSON mapping."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def save_intersection(intersection: List[str], filepath: str):
        """Save intersection list to a text file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in intersection:
                f.write(f"{item}\n")
