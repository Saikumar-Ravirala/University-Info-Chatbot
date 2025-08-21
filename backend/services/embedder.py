from typing import List, Dict, Optional
import numpy as np
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

# Optional: Lazy model loading
_model: Optional["SentenceTransformer"] = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Converts list of text chunks into embeddings.
    Returns a NumPy array of shape (num_chunks, embedding_dim).
    """
    if not chunks:
        logging.warning("⚠️ Empty chunk list passed to get_embeddings")
        return np.empty((0, 0), dtype=np.float32)

    model = get_model()
    try:
        embeddings = model.encode(chunks, show_progress_bar=True)
        return np.array(embeddings, dtype=np.float32)
    except Exception as e:
        logging.error(f"❌ Embedding error: {e}")
        return np.empty((0, 0), dtype=np.float32)

def get_embeddings_for_metadata(chunks: List[Dict]) -> np.ndarray:
    """
    Converts list of chunk dicts into embeddings using 'text' field.
    Returns NumPy array of shape (num_chunks, embedding_dim).
    Handles empty chunks or missing text safely.
    """
    try:
        texts = [chunk.get("text", "").strip() for chunk in chunks if chunk.get("text", "").strip()]
        if not texts:
            logging.warning("⚠️ No valid text found in metadata chunks")
            return np.empty((0, 0), dtype=np.float32)

        return get_embeddings(texts)

    except Exception as e:
        logging.error(f"❌ Error while generating metadata embeddings: {e}")
        return np.empty((0, 0), dtype=np.float32)

# # embedder.py
# from sentence_transformers import SentenceTransformer
# import numpy as np
# from typing import List, Dict

# # Load model once
# model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_embeddings(chunks: List[str]) -> np.ndarray:
#     """
#     Converts list of text chunks into embeddings.
#     Returns a NumPy array of shape (num_chunks, embedding_dim).
#     """
#     embeddings = model.encode(chunks, show_progress_bar=True)
#     return np.array(embeddings)

# # def get_embeddings_for_metadata(chunks: List[Dict]) -> np.ndarray:
# #     """
# #     Converts list of chunk dicts into embeddings using 'text' field.
# #     Returns NumPy array of shape (num_chunks, embedding_dim).
# #     """
# #     texts = [chunk["text"] for chunk in chunks]
# #     embeddings = model.encode(texts, show_progress_bar=True)
# #     return np.array(embeddings)

# def get_embeddings_for_metadata(chunks: List[Dict]) -> np.ndarray:
#     """
#     Converts list of chunk dicts into embeddings using 'text' field.
#     Returns NumPy array of shape (num_chunks, embedding_dim).
#     Handles empty chunks or missing text safely.
#     """
#     try:
#         # Extract only valid non-empty texts
#         texts = [chunk.get("text", "").strip() for chunk in chunks if chunk.get("text", "").strip()]

#         if not texts:
#             print("⚠️ No valid text found in chunks, returning empty embedding array")
#             return np.empty((0, 0), dtype=np.float32)

#         embeddings = model.encode(texts, show_progress_bar=True)

#         # Convert to numpy array
#         return np.array(embeddings, dtype=np.float32)

#     except Exception as e:
#         print(f"❌ Error while generating embeddings: {e}")
#         return np.empty((0, 0), dtype=np.float32)
