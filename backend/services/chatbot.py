# chatbot.py
#from .pdf_parser import extract_text_by_page, extract_text_and_images_by_page_with_easyOCR, extract_text_with_hybrid_approach, extract_pdf_with_region_ocr, extract_pdf_with_region_paddleocr
from .pdf_parser import extract_pdf_with_region_ocr
from .chunker import chunk_text_with_metadata
# from .embedder import get_embeddings_for_metadata, model
from .embedder import get_embeddings_for_metadata, get_model
# from .vector_store import build_faiss_index, search_faiss_index
from .vector_store_qdrant import  upload_to_qdrant, search_qdrant,create_qdrant_collection_if_not_exists,delete_qdrant_collection

# from .gemini_client import generate_answer
import numpy as np
from typing import List, Dict,Tuple

from .scraper import scrape_page, flatten_scraped_data

async def index_scraped_url_to_qdrant(url: str, selectors: List[str], collection_name: str):
    scraped_data = await scrape_page(url, selectors)
    chunks = flatten_scraped_data(scraped_data, url)

    embeddings = get_embeddings_for_metadata(chunks)
    create_qdrant_collection_if_not_exists(collection_name, embeddings.shape[1])
    upload_to_qdrant(collection_name, embeddings, chunks)
    print(f"🌐 Scraped content from '{url}' indexed into '{collection_name}'.")


def index_pdfs_to_qdrant(pdf_paths: List[str], file_names: List[str], collection_name: str):
    all_chunks = []
    for path, name in zip(pdf_paths, file_names):
        pages = extract_pdf_with_region_ocr(path)
        chunks = chunk_text_with_metadata(pages, name)
        all_chunks.extend(chunks)

    embeddings = get_embeddings_for_metadata(all_chunks)
    create_qdrant_collection_if_not_exists(collection_name, embeddings.shape[1])
    upload_to_qdrant(collection_name, embeddings, all_chunks)
    print(f"✅ Collection '{collection_name}' indexed. Ready for questions.")

def query_rag(user_query: str, collection_name: str, top_k=3):
    model = get_model()
    query_embedding = model.encode(user_query)
    retrieved_chunks = search_qdrant(collection_name, query_embedding, top_k)
    context_texts = [chunk["text"] for chunk in retrieved_chunks]
    metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]
    return context_texts, metadata

def cleanup_user_collection(collection_name: str):
    delete_qdrant_collection(collection_name)