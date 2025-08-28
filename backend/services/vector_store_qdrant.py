# backend/services/vector_store_qdrant.py
# import os
import uuid
import numpy as np
import time
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from langsmith import traceable
import logging
from config.app_config import AppConfig

# Load environment variables
load_dotenv()

class QdrantVectorStore:
    """
    A class for managing Qdrant vector store operations including
    collection management, data upload, and search functionality.
    """
    
    #def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
    def __init__(self, config: AppConfig):
        """
        Initialize the Qdrant vector store client.
        
        Args:
            url: Qdrant server URL (defaults to QDRANT_URL env var)
            api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
        """
        self.url = config.qdrant_url
        self.api_key = config.qdrant_api_key
        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        # self.url = url or os.getenv("QDRANT_URL")
        # self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        
        if not self.url:
            raise ValueError("Qdrant URL must be provided or set in QDRANT_URL environment variable")
        
        # self.client = QdrantClient(url=self.url, api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def generate_collection_name(self, prefix: str = "user-session") -> str:
        """
        Generates a unique collection name.
        
        Args:
            prefix: Prefix for the collection name
            
        Returns:
            Unique collection name string
        """
        return f"{prefix}-{uuid.uuid4().hex}"
    
    def create_collection_if_not_exists(self, collection_name: str, dim: int) -> bool:
        """
        Creates a Qdrant collection only if it doesn't already exist.
        
        Args:
            collection_name: Name of the collection to create
            dim: Dimension of the vectors
            
        Returns:
            True if collection was created, False if it already exists
        """
        try:
            existing = self.client.get_collections().collections
            if not any(c.name == collection_name for c in existing):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
                self.logger.info(f"✅ Created collection: {collection_name}")
                return True
            else:
                self.logger.info(f"ℹ️ Collection already exists: {collection_name}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to create collection {collection_name}: {e}")
            raise
    
    @traceable
    def upload_points(
        self,
        collection_name: str,
        embeddings: np.ndarray,
        metadata: List[Dict],
        batch_size: int = 10,
        max_retries: int = 3,
        log_collection_size: bool = True
    ) -> int:
        """
        Uploads points to Qdrant with retries and logging.
        
        Args:
            collection_name: Qdrant collection name
            embeddings: Embedding vectors as numpy array
            metadata: Metadata for each chunk
            batch_size: Number of points per batch
            max_retries: Retry attempts per batch
            log_collection_size: Whether to log final collection size
            
        Returns:
            Total number of points successfully uploaded
        """
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        timestamp = datetime.utcnow().isoformat()
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={**meta, "timestamp": timestamp}
            )
            for embedding, meta in zip(embeddings, metadata)
        ]

        total_uploaded = 0

        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            for attempt in range(max_retries):
                try:
                    self.client.upsert(collection_name=collection_name, points=batch)
                    self.logger.info(f"✅ Uploaded batch {batch_num} ({len(batch)} points)")
                    total_uploaded += len(batch)
                    break
                except Exception as e:
                    self.logger.warning(f"❌ Batch {batch_num} failed (attempt {attempt + 1}): {e}")
                    time.sleep(2 ** attempt)  # exponential backoff
            else:
                self.logger.error(f"🚫 Giving up on batch {batch_num} after {max_retries} attempts")

        if log_collection_size:
            try:
                count = self.client.count(collection_name=collection_name, exact=True).count
                self.logger.info(f"📦 Total points in collection '{collection_name}': {count}")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to fetch collection size: {e}")
        
        return total_uploaded
    
    @traceable
    def search(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Searches Qdrant and returns top_k matching metadata entries.
        
        Args:
            collection_name: Name of the collection to search
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of matching metadata entries
        """
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                with_payload=True,
                score_threshold=score_threshold
            )
            return [r.payload for r in results]
        except Exception as e:
            self.logger.error(f"❌ Search failed for collection {collection_name}: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Deletes a Qdrant collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            self.logger.info(f"✅ Deleted collection: {collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to delete collection {collection_name}: {e}")
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if collection exists, False otherwise
        """
        try:
            existing = self.client.get_collections().collections
            return any(c.name == collection_name for c in existing)
        except Exception as e:
            self.logger.error(f"❌ Failed to check collection existence {collection_name}: {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information dictionary or None if not found
        """
        try:
            return self.client.get_collection(collection_name=collection_name).dict()
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get collection info {collection_name}: {e}")
            return None
        
# # vector_store_qdrant.py
# import os
# import uuid
# import numpy as np
# import time
# from typing import List, Dict
# from datetime import datetime
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.models import PointStruct, Distance, VectorParams
# from langsmith import traceable

# # Load environment variables
# load_dotenv()

# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# def generate_collection_name() -> str:
#     """Generates a unique collection name for each user session."""
#     return f"user-session-{uuid.uuid4().hex}"

# def create_qdrant_collection_if_not_exists(collection_name: str, dim: int):
#     """Creates a Qdrant collection only if it doesn't already exist."""
#     existing = client.get_collections().collections
#     if not any(c.name == collection_name for c in existing):
#         client.create_collection(
#             collection_name=collection_name,
#             vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
#         )

# @traceable
# def upload_to_qdrant(
#     collection_name: str,
#     embeddings,
#     metadata,
#     batch_size: int = 10,
#     max_retries: int = 3,
#     log_collection_size: bool = True
# ):
#     """
#     Uploads points to Qdrant with retries and logging.

#     Args:
#         collection_name (str): Qdrant collection name.
#         embeddings (np.ndarray): Embedding vectors.
#         metadata (List[Dict]): Metadata for each chunk.
#         batch_size (int): Number of points per batch.
#         max_retries (int): Retry attempts per batch.
#         log_collection_size (bool): Whether to log final collection size.
#     """
#     timestamp = datetime.utcnow().isoformat()
#     points = [
#         PointStruct(
#             id=str(uuid.uuid4()),
#             vector=embedding.tolist(),
#             payload={**meta, "timestamp": timestamp}
#         )
#         for embedding, meta in zip(embeddings, metadata)
#     ]

#     total_uploaded = 0

#     for i in range(0, len(points), batch_size):
#         batch = points[i:i + batch_size]
#         for attempt in range(max_retries):
#             try:
#                 client.upsert(collection_name=collection_name, points=batch)
#                 print(f"✅ Uploaded batch {i // batch_size + 1} ({len(batch)} points)")
#                 total_uploaded += len(batch)
#                 break
#             except Exception as e:
#                 print(f"❌ Batch {i // batch_size + 1} failed (attempt {attempt + 1}): {e}")
#                 time.sleep(2 ** attempt)  # exponential backoff
#         else:
#             print(f"🚫 Giving up on batch {i // batch_size + 1} after {max_retries} attempts")

#     if log_collection_size:
#         try:
#             count = client.count(collection_name=collection_name, exact=True).count
#             print(f"📦 Total points in collection '{collection_name}': {count}")
#         except Exception as e:
#             print(f"⚠️ Failed to fetch collection size: {e}")

# @traceable
# def search_qdrant(collection_name: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
#     """Searches Qdrant and returns top_k matching metadata entries."""
#     results = client.search(
#         collection_name=collection_name,
#         query_vector=query_embedding.tolist(),
#         limit=top_k,
#         with_payload=True
#     )
#     return [r.payload for r in results]

# def delete_qdrant_collection(collection_name: str):
#     """Deletes a Qdrant collection (for session cleanup)."""
#     try:
#         client.delete_collection(collection_name=collection_name)
#         print(f"✅ Deleted collection: {collection_name}")
#     except Exception as e:
#         print(f"❌ Failed to delete collection {collection_name}: {e}")
