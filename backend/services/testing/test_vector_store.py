# test_vector_store.py
from embedder import get_embeddings
from vector_store import build_faiss_index, search_faiss_index

chunks = ["AI is transforming education.", "FastAPI is great for backend development.", "Embeddings capture semantic meaning."]
embeddings = get_embeddings(chunks)

index = build_faiss_index(embeddings)

query = "What is FastAPI used for?"
query_embedding = get_embeddings([query])[0]

top_indices = search_faiss_index(index, query_embedding, top_k=2)
print("Top matching chunks:")
for i in top_indices:
    print(f"- {chunks[i]}")
