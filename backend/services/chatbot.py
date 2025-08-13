# chatbot.py
from .pdf_parser import extract_text_by_page, extract_text_and_images_by_page
from .chunker import chunk_text_with_metadata
from .embedder import get_embeddings_for_metadata, model
from .vector_store import build_faiss_index, search_faiss_index
from .vector_store_qdrant import create_qdrant_collection, upload_to_qdrant, search_qdrant

# from .gemini_client import generate_answer
import numpy as np
from typing import List, Dict,Tuple


#this function as faiss and metadata 

# def get_rag_context_from_pdfs(
#     pdf_paths: List[str],
#     file_names: List[str],
#     user_query: str,
#     top_k: int = 3
# ) -> Tuple[List[str], List[Dict]]:
#     # Step 1: Parse and chunk all PDFs with metadata
#     all_chunks = []
#     for path, name in zip(pdf_paths, file_names):
#         pages = extract_text_by_page(path)
#         chunks = chunk_text_with_metadata(pages, name)
#         all_chunks.extend(chunks)

#     # Step 2: Embed chunks
#     embeddings = get_embeddings_for_metadata(all_chunks)

#     # Step 3: Build FAISS index
#     index = build_faiss_index(embeddings)

#     # Step 4: Embed user query
#     query_embedding = model.encode(user_query)

#     # Step 5: Search top-k relevant chunks
#     retrieved_chunks = search_faiss_index(index, query_embedding, all_chunks, top_k)

#     # Step 6: Extract text and metadata
#     context_texts = [chunk["text"] for chunk in retrieved_chunks]
#     metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]

#     return context_texts, metadata
###############################################################################


#this function as qdrant and metadata 
#it contains all the steps from pdf parsing to chunking, embedding, and searching

# def get_rag_context_from_pdfs(
#     pdf_paths: List[str],
#     file_names: List[str],
#     user_query: str,
#     top_k: int = 3
# ) -> Tuple[List[str], List[Dict]]:
#     # Step 1: Parse and chunk all PDFs with metadata
#     all_chunks = []
#     for path, name in zip(pdf_paths, file_names):
#         # pages = extract_text_by_page(path)  # If you want to extract only text
#         # Use extract_text_and_images_by_page if you want both text and images
#         pages = extract_text_and_images_by_page(path)
#         chunks = chunk_text_with_metadata(pages, name)
#         all_chunks.extend(chunks)

#     # Step 2: Embed chunks
#     embeddings = get_embeddings_for_metadata(all_chunks)

#     # Step 3: Create Qdrant collection
#     collection_name = "pdf-rag-chatbot"
#     create_qdrant_collection(collection_name, embeddings.shape[1])

#     # Step 4: Upload to Qdrant
#     upload_to_qdrant(collection_name, embeddings, all_chunks)

#     print("now ask the questions")

#     # Step 5: Embed user query
#     query_embedding = model.encode(user_query)

#     # Step 6: Search top-k relevant chunks
#     retrieved_chunks = search_qdrant(collection_name, query_embedding, top_k)

#     # Step 7: Extract text and metadata
#     context_texts = [chunk["text"] for chunk in retrieved_chunks]
#     metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]

#     return context_texts, metadata
###############################################################################
##this function as qdrant and metadata
#split the function into two parts: one for creating the collection and uploading data, and another for querying

def index_pdfs_to_qdrant(pdf_paths: List[str], file_names: List[str], collection_name="pdf-rag-chatbot"):
    all_chunks = []
    for path, name in zip(pdf_paths, file_names):
        pages = extract_text_and_images_by_page(path)
        chunks = chunk_text_with_metadata(pages, name)
        all_chunks.extend(chunks)

    embeddings = get_embeddings_for_metadata(all_chunks)
    create_qdrant_collection(collection_name, embeddings.shape[1])
    upload_to_qdrant(collection_name, embeddings, all_chunks)
    print("now ask the questions")


def query_rag(user_query: str, top_k=3, collection_name="pdf-rag-chatbot"):
    query_embedding = model.encode(user_query)
    retrieved_chunks = search_qdrant(collection_name, query_embedding, top_k)
    context_texts = [chunk["text"] for chunk in retrieved_chunks]
    metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]
    return context_texts, metadata


###############################################################################


# def answer_query_from_pdfs(
#     pdf_paths: List[str],
#     file_names: List[str],
#     user_query: str,
#     history: List[Dict[str, str]],
#     top_k: int = 3
# ) -> str:
    
    
#     #def answer_query_from_pdfs(pdf_paths: List[str], file_names: List[str], user_query: str, top_k: int = 3) -> str:
    
#     # Step 1: Parse and chunk all PDFs with metadata
#     all_chunks = []
#     for path, name in zip(pdf_paths, file_names):
#         pages = extract_text_by_page(path)
#         chunks = chunk_text_with_metadata(pages, name)
#         all_chunks.extend(chunks)

#     # Step 2: Embed chunks
#     embeddings = get_embeddings_for_metadata(all_chunks)

#     # Step 3: Build FAISS index
#     index = build_faiss_index(embeddings)

#     # Step 4: Embed query
#     # from embedder import model  # reuse loaded model
#     query_embedding = model.encode(user_query)
#     # query_embedding = get_embeddings([user_query])[0]

#     # Step 5: Search top-k chunks
#     retrieved_chunks = search_faiss_index(index, query_embedding, all_chunks, top_k)

#     # Step 6: Prepare context and metadata
#     context_texts = [chunk["text"] for chunk in retrieved_chunks]
#     metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]

#     # Step 7: Generate answer
#     #answer = generate_answer(context_texts, user_query, metadata)
#     #return answer

#     # Step 7: Generate answer with history
#     answer = generate_answer(context_texts, user_query, metadata, history)
#     return answer


# def answer_query_from_pdf(pdf_path: str, user_query: str, top_k: int = 3) -> str:
    # Step 1: Extract text
    # text = extract_text_from_pdf(pdf_path)

    # # Step 2: Chunk text
    # chunks = chunk_text(text)

    # # Step 3: Embed chunks
    # embeddings = get_embeddings(chunks)

    # # Step 4: Build FAISS index
    # index = build_faiss_index(embeddings)

    # # Step 5: Embed query
    # query_embedding = get_embeddings([user_query])[0]

    # # Step 6: Search top-k chunks
    # top_indices = search_faiss_index(index, query_embedding, top_k)
    # context_chunks = [chunks[i] for i in top_indices]

    # # Step 7: Generate answer
    # answer = generate_answer(context_chunks, user_query)
    # return answer



# from pdf_parser import extract_text_from_pdf
# from chunker import chunk_text
# from embedder import get_embeddings
# from vector_store import build_faiss_index, search_faiss_index
# from gemini_client import generate_answer
# import numpy as np

