"""
Dataset management module for Prompt Shield attack vectors.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AttackVector(BaseModel):
    id: str
    category: str  # jailbreak | prompt_injection | data_exfiltration
    sub_category: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    pattern: str
    keywords: List[str] = []


class AttackVectorDataset:
    """Manages loading, filtering, and dynamic updating of attack vector datasets."""

    def __init__(self, file_path: str = "data/attack_vectors.json"):
        self.file_path = file_path
        self.vectors: List[AttackVector] = []
        self.load_dataset()

    def load_dataset(self) -> List[AttackVector]:
        """Loads attack vectors from JSON file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.vectors = [AttackVector(**item) for item in data]
        else:
            self.vectors = []
        return self.vectors

    def save_dataset(self) -> None:
        """Persists current attack vectors to JSON file."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            data = [v.model_dump() for v in self.vectors]
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_vector(self, vector: AttackVector) -> None:
        """Adds a new attack vector dynamically."""
        self.vectors.append(vector)
        self.save_dataset()

    def get_by_category(self, category: str) -> List[AttackVector]:
        """Filters vectors by category."""
        return [v for v in self.vectors if v.category.lower() == category.lower()]

    def get_all_patterns(self) -> List[str]:
        """Returns all text patterns for vector store indexing."""
        return [v.pattern for v in self.vectors]
