# vector_store_qdrant.py
import os
import uuid
import numpy as np
import time
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from langsmith import traceable

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def generate_collection_name() -> str:
    """Generates a unique collection name for each user session."""
    return f"user-session-{uuid.uuid4().hex}"

def create_qdrant_collection_if_not_exists(collection_name: str, dim: int):
    """Creates a Qdrant collection only if it doesn't already exist."""
    existing = client.get_collections().collections
    if not any(c.name == collection_name for c in existing):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
        )

@traceable
def upload_to_qdrant(
    collection_name: str,
    embeddings,
    metadata,
    batch_size: int = 10,
    max_retries: int = 3,
    log_collection_size: bool = True
):
    """
    Uploads points to Qdrant with retries and logging.

    Args:
        collection_name (str): Qdrant collection name.
        embeddings (np.ndarray): Embedding vectors.
        metadata (List[Dict]): Metadata for each chunk.
        batch_size (int): Number of points per batch.
        max_retries (int): Retry attempts per batch.
        log_collection_size (bool): Whether to log final collection size.
    """
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
        for attempt in range(max_retries):
            try:
                client.upsert(collection_name=collection_name, points=batch)
                print(f"✅ Uploaded batch {i // batch_size + 1} ({len(batch)} points)")
                total_uploaded += len(batch)
                break
            except Exception as e:
                print(f"❌ Batch {i // batch_size + 1} failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)  # exponential backoff
        else:
            print(f"🚫 Giving up on batch {i // batch_size + 1} after {max_retries} attempts")

    if log_collection_size:
        try:
            count = client.count(collection_name=collection_name, exact=True).count
            print(f"📦 Total points in collection '{collection_name}': {count}")
        except Exception as e:
            print(f"⚠️ Failed to fetch collection size: {e}")

@traceable
def search_qdrant(collection_name: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
    """Searches Qdrant and returns top_k matching metadata entries."""
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k,
        with_payload=True
    )
    return [r.payload for r in results]

def delete_qdrant_collection(collection_name: str):
    """Deletes a Qdrant collection (for session cleanup)."""
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"✅ Deleted collection: {collection_name}")
    except Exception as e:
        print(f"❌ Failed to delete collection {collection_name}: {e}")
