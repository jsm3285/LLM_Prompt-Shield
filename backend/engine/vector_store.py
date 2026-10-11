"""
In-Memory Vector Store for Prompt Shield threat matching.

Supports hybrid FAISS (IndexFlatIP) and high-speed Numpy cosine matrix operations
for sub-millisecond similarity queries (<2ms SLA).
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False


class VectorStore:
    """Ultra-fast In-Memory Vector Store with FAISS & Numpy hybrid backend."""

    def __init__(self, dimension: int = 384, prefer_faiss: bool = True):
        self.dimension = dimension
        self.use_faiss = prefer_faiss and FAISS_AVAILABLE
        self.faiss_index = None
        if self.use_faiss:
            self.faiss_index = faiss.IndexFlatIP(dimension)

        self.vectors: Optional[np.ndarray] = None  # Shape: (N, dimension)
        self.metadata: List[Dict[str, Any]] = []

    def clear(self) -> None:
        """Clears all vectors and metadata."""
        if self.use_faiss and faiss is not None:
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
        self.vectors = None
        self.metadata = []

    def add_vector(self, vector: np.ndarray, meta: Dict[str, Any]) -> None:
        """Adds a single normalized vector and its metadata."""
        vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        # FAISS index addition
        if self.use_faiss and self.faiss_index is not None:
            self.faiss_index.add(np.expand_dims(vec, axis=0))

        # Numpy matrix backup
        if self.vectors is None:
            self.vectors = np.array([vec], dtype=np.float32)
        else:
            self.vectors = np.vstack([self.vectors, vec])

        self.metadata.append(meta)

    def search(self, query_vector: np.ndarray, top_k: int = 1) -> List[Tuple[float, Dict[str, Any]]]:
        """Performs cosine similarity search against indexed threat vectors. Returns [(similarity_score, metadata)]."""
        if len(self.metadata) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        top_k = min(top_k, len(self.metadata))

        # FAISS search branch
        if self.use_faiss and self.faiss_index is not None and self.faiss_index.ntotal > 0:
            q_expanded = np.expand_dims(q_vec, axis=0)
            distances, indices = self.faiss_index.search(q_expanded, top_k)
            results = []
            for score, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(self.metadata):
                    results.append((float(score), self.metadata[idx]))
            return results

        # Numpy matrix search branch
        if self.vectors is None:
            return []

        similarities = np.dot(self.vectors, q_vec)
        idx_sorted = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in idx_sorted:
            score = float(similarities[idx])
            results.append((score, self.metadata[idx]))

        return results

    def count(self) -> int:
        """Returns the total number of indexed vectors."""
        return len(self.metadata)

    def get_backend_info(self) -> Dict[str, Any]:
        """Returns the active backend and index statistics."""
        return {
            "backend": "FAISS (IndexFlatIP)" if self.use_faiss else "Numpy (Matrix Dot Product)",
            "dimension": self.dimension,
            "vector_count": len(self.metadata),
            "faiss_installed": FAISS_AVAILABLE
        }

