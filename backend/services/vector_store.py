# vector_store.py
import faiss
import numpy as np
from typing import List, Tuple, Dict

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Builds a FAISS index from embeddings.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_faiss_index(index: faiss.IndexFlatL2, query_embedding: np.ndarray, metadata: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Searches FAISS index and returns top_k matching metadata entries.
    """
    query_embedding = np.array([query_embedding])  # FAISS expects 2D
    distances, indices = index.search(query_embedding, top_k)
    results = [metadata[i] for i in indices[0]]
    return results