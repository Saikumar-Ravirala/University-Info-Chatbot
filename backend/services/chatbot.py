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
# ###############################################################################
# ##this function as qdrant and metadata
# #split the function into two parts: one for creating the collection and uploading data, and another for querying

# def index_pdfs_to_qdrant(pdf_paths: List[str], file_names: List[str], collection_name="pdf-rag-chatbot"):
#     all_chunks = []
#     for path, name in zip(pdf_paths, file_names):
#         # pages = extract_text_and_images_by_page_with_easyOCR(path)
#         # pages = extract_text_with_hybrid_approach(path)
#         pages = extract_pdf_with_region_ocr(path)
#         #blocks = extract_pdf_with_region_paddleocr(path, source=name)
#         #chunks = blocks  # blocks already contain metadata
#         #pages = extract_pdf_with_region_paddleocr(path, source=name)
#         chunks = chunk_text_with_metadata(pages, name)
#         all_chunks.extend(chunks)

#     embeddings = get_embeddings_for_metadata(all_chunks)
#     create_qdrant_collection(collection_name, embeddings.shape[1])
#     upload_to_qdrant(collection_name, embeddings, all_chunks)
#     print("now ask the questions")

# # def index_pdfs_to_qdrant(pdf_paths: List[str], file_names: List[str], collection_name="pdf-rag-chatbot"):
# #     try:
# #         all_chunks = []

# #         for path, name in zip(pdf_paths, file_names):
# #             print(f"🔍 Processing PDF: {name}")
# #             blocks = extract_pdf_with_region_paddleocr(path, source=name)
            
# #             if not blocks:
# #                 print(f"⚠️ No text extracted from: {name}, skipping...")
# #                 continue

# #             # Ensure all blocks contain 'text'
# #             valid_blocks = [blk for blk in blocks if isinstance(blk, dict) and blk.get("text")]
# #             if not valid_blocks:
# #                 print(f"⚠️ No valid text chunks in: {name}, skipping...")
# #                 continue

# #             all_chunks.extend(valid_blocks)

# #         if not all_chunks:
# #             print("🚫 No valid chunks extracted from any PDF. Aborting indexing.")
# #             return

# #         # Generate embeddings
# #         embeddings = get_embeddings_for_metadata(all_chunks)
# #         if embeddings.size == 0:
# #             print("🚫 Embedding array is empty. Aborting.")
# #             return

# #         # Create collection and upload
# #         create_qdrant_collection(collection_name, embeddings.shape[1])
# #         upload_to_qdrant(collection_name, embeddings, all_chunks)

# #         print("✅ PDF chunks successfully indexed to Qdrant. You can now ask questions.")

# #     except Exception as e:
# #         import traceback
# #         print("❌ Error during PDF indexing:")
# #         print(traceback.format_exc())




# def query_rag(user_query: str, top_k=3, collection_name="pdf-rag-chatbot"):
#     query_embedding = model.encode(user_query)
#     retrieved_chunks = search_qdrant(collection_name, query_embedding, top_k)
#     context_texts = [chunk["text"] for chunk in retrieved_chunks]
#     metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]
#     return context_texts, metadata


# ###############################################################################
