"""
In-Memory Vector Store for Prompt Shield threat matching.

Supports fast numpy cosine matrix multiplication / FAISS fallback for sub-millisecond similarity queries.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional


class VectorStore:
    """Ultra-fast In-Memory Vector Store for real-time vector similarity search."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors: Optional[np.ndarray] = None  # Shape: (N, dimension)
        self.metadata: List[Dict[str, Any]] = []

    def clear(self) -> None:
        """Clears all vectors and metadata."""
        self.vectors = None
        self.metadata = []

    def add_vector(self, vector: np.ndarray, meta: Dict[str, Any]) -> None:
        """Adds a single normalized vector and its metadata."""
        vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        if self.vectors is None:
            self.vectors = np.array([vec], dtype=np.float32)
        else:
            self.vectors = np.vstack([self.vectors, vec])
        self.metadata.append(meta)

    def search(self, query_vector: np.ndarray, top_k: int = 1) -> List[Tuple[float, Dict[str, Any]]]:
        """Performs cosine similarity search against indexed threat vectors. Returns [(similarity_score, metadata)]."""
        if self.vectors is None or len(self.metadata) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Cosine similarity via matrix-vector dot product
        similarities = np.dot(self.vectors, q_vec)
        
        # Get top-k indices sorted descending
        top_k = min(top_k, len(similarities))
        idx_sorted = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in idx_sorted:
            score = float(similarities[idx])
            results.append((score, self.metadata[idx]))

        return results

    def count(self) -> int:
        """Returns the total number of indexed vectors."""
        return len(self.metadata)
