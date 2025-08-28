# backend/services/embedder.py
from typing import List, Dict, Optional, TYPE_CHECKING
import numpy as np
import logging
from langsmith import traceable
from config.app_config import AppConfig

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

class Embedder:
    """
    A class for generating text embeddings using SentenceTransformers.
    Handles lazy model loading and provides embedding generation methods.
    """
    def __init__(self, config: AppConfig):
        self.model_name = "all-MiniLM-L6-v2"  # default
        # Allow override from config if you want later
        self._model: Optional["SentenceTransformer"] = None
        self.logger = logging.getLogger(__name__)

    # def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
    #     """
    #     Initialize the EmbeddingGenerator.
        
    #     Args:
    #         model_name: Name of the SentenceTransformer model to use
    #     """
    #     self.model_name = model_name
    #     self._model: Optional["SentenceTransformer"] = None
    #     self.logger = logging.getLogger(__name__)
    
    def _get_model(self) -> "SentenceTransformer":
        """
        Get the model instance with lazy loading.
        
        Returns:
            Loaded SentenceTransformer model
        """
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self.logger.info(f"✅ Loaded embedding model: {self.model_name}")
            except ImportError:
                self.logger.error("❌ sentence-transformers package not installed")
                raise
            except Exception as e:
                self.logger.error(f"❌ Failed to load model {self.model_name}: {e}")
                raise
        
        return self._model
    
    def get_embeddings(self, chunks: List[str]) -> np.ndarray:
        """
        Converts list of text chunks into embeddings.
        
        Args:
            chunks: List of text strings to embed
            
        Returns:
            NumPy array of shape (num_chunks, embedding_dim)
        """
        if not chunks:
            self.logger.warning("⚠️ Empty chunk list passed to get_embeddings")
            return np.empty((0, 0), dtype=np.float32)

        model = self._get_model()
        try:
            embeddings = model.encode(chunks, show_progress_bar=True)
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            self.logger.error(f"❌ Embedding error: {e}")
            return np.empty((0, 0), dtype=np.float32)
    
    @traceable
    def get_embeddings_for_metadata(self, chunks: List[Dict]) -> np.ndarray:
        """
        Converts list of chunk dicts into embeddings using 'text' field.
        
        Args:
            chunks: List of dictionaries containing chunk data
            
        Returns:
            NumPy array of shape (num_chunks, embedding_dim)
        """
        try:
            texts = [chunk.get("text", "").strip() for chunk in chunks if chunk.get("text", "").strip()]
            if not texts:
                self.logger.warning("⚠️ No valid text found in metadata chunks")
                return np.empty((0, 0), dtype=np.float32)

            return self.get_embeddings(texts)

        except Exception as e:
            self.logger.error(f"❌ Error while generating metadata embeddings: {e}")
            return np.empty((0, 0), dtype=np.float32)
    
    def update_model(self, model_name: str) -> None:
        """
        Update the model to use for embeddings.
        
        Args:
            model_name: New model name to use
        """
        if model_name != self.model_name:
            self.model_name = model_name
            self._model = None  # Force reload on next use
            self.logger.info(f"🔄 Model updated to: {model_name}")
            