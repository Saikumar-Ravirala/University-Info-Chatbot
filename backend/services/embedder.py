# embedder.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Converts list of text chunks into embeddings.
    Returns a NumPy array of shape (num_chunks, embedding_dim).
    """
    embeddings = model.encode(chunks, show_progress_bar=True)
    return np.array(embeddings)

def get_embeddings_for_metadata(chunks: List[Dict]) -> np.ndarray:
    """
    Converts list of chunk dicts into embeddings using 'text' field.
    Returns NumPy array of shape (num_chunks, embedding_dim).
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings)