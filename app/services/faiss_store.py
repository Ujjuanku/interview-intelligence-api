import faiss
import numpy as np
import json
import os
import logging
from typing import List, Tuple, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class FaissStore:
    def __init__(self):
        self.index_path = settings.faiss_index_path
        self.metadata_path = self.index_path.replace(".bin", "_meta.json")
        self.dimension = 1536  # Dimension for text-embedding-3-small
        self.index = None
        self.metadata = {}  # Map int ID to dict with 'text' and other metadata
        self._next_id = 0
        self.load_index()

    def load_index(self):
        """Loads the FAISS index and metadata from disk if they exist."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = {int(k): v for k, v in data.get("metadata", {}).items()}
                    self._next_id = data.get("next_id", 0)
                logger.info("Loaded FAISS index from disk.")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._initialize_empty_index()
        else:
            self._initialize_empty_index()

    def _initialize_empty_index(self):
        """Initializes a new empty FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine similarity (assuming normalized vectors)
        # Create an IDMap to store custom integer IDs
        self.index = faiss.IndexIDMap(self.index)
        self.metadata = {}
        self._next_id = 0
        logger.info("Initialized new empty FAISS index.")

    def save_index(self):
        """Saves the FAISS index and metadata to disk."""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "next_id": self._next_id,
                    "metadata": self.metadata
                }, f)
            logger.info("Saved FAISS index to disk.")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise

    def add_vectors(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Adds vectors and their corresponding metadata to the index."""
        if not embeddings:
            return

        assert len(embeddings) == len(metadatas), "Embeddings and metadata must have same length."

        # Normalize vectors for cosine similarity
        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)

        # Generate IDs
        ids = np.arange(self._next_id, self._next_id + len(vectors), dtype=np.int64)
        
        # Add to FAISS
        self.index.add_with_ids(vectors, ids)

        # Update metadata Map
        for i, idx_val in enumerate(ids):
            self.metadata[int(idx_val)] = metadatas[i]

        self._next_id += len(vectors)
        self.save_index()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Searches the index for the top_k most similar vectors."""
        if self.index.ntotal == 0:
            return []

        # Prepare query vector
        query_vector = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)

        # Perform search
        scores, ids = self.index.search(query_vector, top_k)
        
        results = []
        for j, idx in enumerate(ids[0]):
            if idx != -1:  # -1 means no result found
                item_metadata = self.metadata.get(int(idx), {})
                score = float(scores[0][j])
                results.append((item_metadata, score))
                
        return results

# Singleton instance
faiss_store = FaissStore()
