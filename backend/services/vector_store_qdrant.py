# vector_store_qdrant.py
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import numpy as np
import uuid
from typing import List, Dict

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# # Initialize Qdrant client (use env vars for safety)
# client = QdrantClient(
#     url="https://your-cluster-name.qdrant.tech",
#     api_key="your-api-key"
# )

def create_qdrant_collection(collection_name: str, dim: int):
    """
    Creates or resets a Qdrant collection.
    """
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
    )

# def upload_to_qdrant(collection_name: str, embeddings: np.ndarray, metadata: List[Dict]):
#     """
#     Uploads embeddings and metadata to Qdrant.
#     """
#     points = [
#         PointStruct(
#             id=str(uuid.uuid4()),
#             vector=embedding.tolist(),
#             payload=meta
#         )
#         for embedding, meta in zip(embeddings, metadata)
#     ]
#     client.upsert(collection_name=collection_name, points=points)

# Function to upload data in batches to avoid timeout issues
def upload_to_qdrant(collection_name: str, embeddings, metadata, batch_size: int = 50):
    """
    Uploads points to Qdrant in batches to avoid timeout issues.

    Args:
        collection_name (str): Name of the Qdrant collection.
        embeddings (List[np.ndarray]): List of embedding vectors.
        metadata (List[Dict]): List of metadata dictionaries for each chunk.
        batch_size (int): Number of points per batch.
    """
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload=meta
        )
        for embedding, meta in zip(embeddings, metadata)
    ]

    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        try:
            client.upsert(collection_name=collection_name, points=batch)
        except Exception as e:
            print(f"❌ Failed to upload batch {i // batch_size + 1}: {e}")



def search_qdrant(collection_name: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
    """
    Searches Qdrant and returns top_k matching metadata entries.
    """
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k
    )
    return [r.payload for r in results]
