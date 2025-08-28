# backend/services/chatbot.py
from typing import List, Dict, Tuple, Optional
# import numpy as np
import logging
from langsmith import traceable

from .parser.dispatcher import ParserDispatcher
from .chunker import TextChunker
from .embedder import Embedder
from .vector_store_qdrant import QdrantVectorStore
from .gemini_client import GeminiClient
from .scraper import WebScraper
from config.app_config import AppConfig

class RAGService:
    """
    A class that orchestrates the RAG pipeline including document indexing,
    query processing, and response generation.
    """
    def __init__(self, config: AppConfig, embedder: Embedder, vector_store: QdrantVectorStore, gemini_client: GeminiClient):
        self.logger = logging.getLogger(__name__)
        self.parser_dispatcher = ParserDispatcher()
        self.text_chunker = TextChunker(chunk_size=config.chunk_size, overlap=config.chunk_overlap)
        self.embedding_generator = embedder
        self.vector_store = vector_store
        self.gemini_client = gemini_client
        self.scraper = WebScraper()
        self.logger.info("✅ Chatbot initialized with AppConfig + injected services")
    # def __init__(
    #     self,
    #     embedding_model_name: str = "all-MiniLM-L6-v2",
    #     gemini_model_name: str = "gemini-2.5-flash",
    #     qdrant_url: Optional[str] = None,
    #     qdrant_api_key: Optional[str] = None,
    #     gemini_api_key: Optional[str] = None,
    #     chunk_size: int = 500,
    #     chunk_overlap: int = 50
    # ):
    #     """
    #     Initialize the Chatbot with all necessary components.
        
    #     Args:
    #         embedding_model_name: Name of the embedding model
    #         gemini_model_name: Name of the Gemini model
    #         qdrant_url: Qdrant server URL
    #         qdrant_api_key: Qdrant API key
    #         gemini_api_key: Gemini API key
    #         chunk_size: Size of text chunks
    #         chunk_overlap: Overlap between chunks
    #     """
    #     self.logger = logging.getLogger(__name__)
        
    #     # Initialize components
    #     self.parser_dispatcher = ParserDispatcher()
    #     self.text_chunker = TextChunker(chunk_size=chunk_size, overlap=chunk_overlap)
    #     self.embedding_generator = Embedder(model_name=embedding_model_name)
    #     self.vector_store = QdrantVectorStore(url=qdrant_url, api_key=qdrant_api_key)
    #     self.gemini_client = GeminiClient(model_name=gemini_model_name, api_key=gemini_api_key)
    #     self.scraper = WebScraper()

    #     self.logger.info("✅ Chatbot initialized with all components")
    
    @traceable
    async def index_scraped_url_to_qdrant(self, url: str, selectors: List[str], collection_name: str) -> bool:
        """
        Scrape a URL and index the content into Qdrant.
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for scraping
            collection_name: Name of the Qdrant collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            scraped_data = await self.scraper.scrape_page(url, selectors)
            chunks = self.scraper.flatten_scraped_data(scraped_data, url)
            
            if not chunks:
                self.logger.warning(f"⚠️ No content scraped from URL: {url}")
                return False
            
            embeddings = self.embedding_generator.get_embeddings_for_metadata(chunks)
            
            if embeddings.size == 0:
                self.logger.error("❌ Failed to generate embeddings for scraped content")
                return False
            
            # Create collection and upload data
            self.vector_store.create_collection_if_not_exists(collection_name, embeddings.shape[1])
            uploaded_count = self.vector_store.upload_points(collection_name, embeddings, chunks)
            
            self.logger.info(f"🌐 Scraped content from '{url}' indexed into '{collection_name}'. Uploaded {uploaded_count} points.")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to index scraped URL {url}: {e}")
            return False
    
    @traceable
    def index_documents_to_qdrant(self, file_paths: List[str], file_names: List[str], collection_name: str) -> int:
        """
        Index multiple documents into Qdrant.
        
        Args:
            file_paths: List of file paths
            file_names: List of file names for metadata
            collection_name: Name of the Qdrant collection
            
        Returns:
            Number of chunks successfully indexed
        """
        if len(file_paths) != len(file_names):
            raise ValueError("Number of file paths must match number of file names")
        
        all_chunks = []
        
        for path, name in zip(file_paths, file_names):
            try:
                # Parse document
                parsed_content = self.parser_dispatcher.dispatch_parser(path)
                
                # Chunk text with metadata
                if isinstance(parsed_content, list) and all(isinstance(item, tuple) and len(item) == 2 for item in parsed_content):
                    # Handle (page_num, text) format
                    chunks = self.text_chunker.chunk_text_with_metadata(parsed_content, name)
                elif isinstance(parsed_content, str):
                    # Handle plain text format - convert to list of (1, text)
                    chunks = self.text_chunker.chunk_text_with_metadata([(1, parsed_content)], name)
                else:
                    self.logger.warning(f"⚠️ Unsupported parsed content format for {name}")
                    continue
                
                all_chunks.extend(chunks)
                self.logger.info(f"✅ Processed {name}: {len(chunks)} chunks")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to parse {name}: {str(e)}")
                continue
        
        if not all_chunks:
            self.logger.error("❌ No chunks were created from the documents")
            return 0
        
        # Generate embeddings and upload to Qdrant
        embeddings = self.embedding_generator.get_embeddings_for_metadata(all_chunks)
        
        if embeddings.size == 0:
            self.logger.error("❌ Failed to generate embeddings")
            return 0
        
        # Create collection and upload data
        self.vector_store.create_collection_if_not_exists(collection_name, embeddings.shape[1])
        uploaded_count = self.vector_store.upload_points(collection_name, embeddings, all_chunks)
        
        self.logger.info(f"✅ Collection '{collection_name}' indexed with {uploaded_count} points. Ready for questions.")
        return uploaded_count
    
    @traceable
    def query_rag(self, user_query: str, collection_name: str, top_k: int = 3) -> Tuple[List[str], List[Dict]]:
        """
        Query the RAG system and retrieve relevant context.
        
        Args:
            user_query: User's query string
            collection_name: Name of the Qdrant collection to search
            top_k: Number of results to return
            
        Returns:
            Tuple of (context_texts, metadata_list)
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.get_embeddings([user_query])
            
            if query_embedding.size == 0:
                self.logger.error("❌ Failed to generate query embedding")
                return [], []
            
            # Search Qdrant
            retrieved_chunks = self.vector_store.search(collection_name, query_embedding[0], top_k)
            
            if not retrieved_chunks:
                self.logger.warning(f"⚠️ No results found for query in collection '{collection_name}'")
                return [], []
            
            # Extract context and metadata
            context_texts = [chunk.get("text", "") for chunk in retrieved_chunks]
            metadata = [
                {"source": chunk.get("source", "Unknown"), "page": chunk.get("page", "Unknown")}
                for chunk in retrieved_chunks
            ]
            
            return context_texts, metadata
            
        except Exception as e:
            self.logger.error(f"❌ RAG query failed: {e}")
            return [], []
    
    @traceable
    def generate_response(
        self,
        user_query: str,
        collection_name: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 3
    ) -> str:
        """
        Generate a response using RAG and Gemini.
        
        Args:
            user_query: User's query string
            collection_name: Name of the Qdrant collection to search
            history: Conversation history
            top_k: Number of context chunks to retrieve
            
        Returns:
            Generated response text
        """
        context_texts, metadata = self.query_rag(user_query, collection_name, top_k)
        
        if not context_texts:
            return "I couldn't find relevant information to answer your question. Please try asking something else."
        
        return self.gemini_client.generate_answer(context_texts, user_query, metadata, history)
    
    @traceable
    def stream_response(
        self,
        user_query: str,
        collection_name: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 3
    ):
        """
        Stream a response using RAG and Gemini.
        
        Args:
            user_query: User's query string
            collection_name: Name of the Qdrant collection to search
            history: Conversation history
            top_k: Number of context chunks to retrieve
            
        Yields:
            Response text chunks
        """
        context_texts, metadata = self.query_rag(user_query, collection_name, top_k)
        
        if not context_texts:
            yield "I couldn't find relevant information to answer your question. Please try asking something else."
            return
        
        for chunk in self.gemini_client.stream_answer(context_texts, user_query, metadata, history):
            yield chunk
    
    def cleanup_collection(self, collection_name: str) -> bool:
        """
        Clean up a Qdrant collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            return self.vector_store.delete_collection(collection_name)
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
        return self.vector_store.collection_exists(collection_name)
    
    def update_parameters(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        embedding_model: Optional[str] = None,
        gemini_model: Optional[str] = None
    ) -> None:
        """
        Update chatbot parameters.
        
        Args:
            chunk_size: New chunk size
            chunk_overlap: New chunk overlap
            embedding_model: New embedding model name
            gemini_model: New Gemini model name
        """
        if chunk_size is not None or chunk_overlap is not None:
            self.text_chunker.update_chunking_parameters(chunk_size, chunk_overlap)
            self.logger.info(f"🔄 Updated chunking parameters: size={chunk_size}, overlap={chunk_overlap}")
        
        if embedding_model is not None:
            self.embedding_generator.update_model(embedding_model)
            self.logger.info(f"🔄 Updated embedding model: {embedding_model}")
        
        if gemini_model is not None:
            self.gemini_client.update_model(gemini_model)
            self.logger.info(f"🔄 Updated Gemini model: {gemini_model}")

# # chatbot.py
# #from .pdf_parser import extract_text_by_page, extract_text_and_images_by_page_with_easyOCR, extract_text_with_hybrid_approach, extract_pdf_with_region_ocr, extract_pdf_with_region_paddleocr
# from .parser.pdf_parser import extract_pdf_with_region_ocr
# from .parser.dispatcher import dispatch_parser
# from .chunker import chunk_text_with_metadata
# # from .embedder import get_embeddings_for_metadata, model
# from .embedder import get_embeddings_for_metadata, get_model
# # from .vector_store import build_faiss_index, search_faiss_index
# from .vector_store_qdrant import  upload_to_qdrant, search_qdrant,create_qdrant_collection_if_not_exists,delete_qdrant_collection

# # from .gemini_client import generate_answer
# import numpy as np
# from typing import List, Dict,Tuple

# from .scraper import scrape_page, flatten_scraped_data
# from langsmith import traceable

# @traceable
# async def index_scraped_url_to_qdrant(url: str, selectors: List[str], collection_name: str):
#     scraped_data = await scrape_page(url, selectors)
#     chunks = flatten_scraped_data(scraped_data, url)

#     embeddings = get_embeddings_for_metadata(chunks)
#     create_qdrant_collection_if_not_exists(collection_name, embeddings.shape[1])
#     upload_to_qdrant(collection_name, embeddings, chunks)
#     print(f"🌐 Scraped content from '{url}' indexed into '{collection_name}'.")

# @traceable
# def index_docs_to_qdrant(file_paths: List[str], file_names: List[str], collection_name: str):
#     all_chunks = []
#     for path, name in zip(file_paths, file_names):
#         try:
#             raw_text_or_pages = dispatch_parser(path)
#             chunks = chunk_text_with_metadata(raw_text_or_pages, name)
#             all_chunks.extend(chunks)
#         except Exception as e:
#             logger.warning(f"Failed to parse {name}: {str(e)}")

#     embeddings = get_embeddings_for_metadata(all_chunks)
#     create_qdrant_collection_if_not_exists(collection_name, embeddings.shape[1])
#     upload_to_qdrant(collection_name, embeddings, all_chunks)
#     print(f"✅ Collection '{collection_name}' indexed. Ready for questions.")

# @traceable(name="index_pdfs_to_qdrant")
# def index_pdfs_to_qdrant(pdf_paths: List[str], file_names: List[str], collection_name: str):
#     print("Indexing PDFs to Qdrant...")
#     all_chunks = []
#     for path, name in zip(pdf_paths, file_names):
#         pages = extract_pdf_with_region_ocr(path)
#         chunks = chunk_text_with_metadata(pages, name)
#         all_chunks.extend(chunks)

#     print(f"Total chunks created: {len(all_chunks)}")
#     embeddings = get_embeddings_for_metadata(all_chunks)
#     create_qdrant_collection_if_not_exists(collection_name, embeddings.shape[1])
#     upload_to_qdrant(collection_name, embeddings, all_chunks)
#     print(f"✅ Collection '{collection_name}' indexed. Ready for questions.")

# @traceable
# def query_rag(user_query: str, collection_name: str, top_k=3):
#     model = get_model()
#     query_embedding = model.encode(user_query)
#     retrieved_chunks = search_qdrant(collection_name, query_embedding, top_k)
#     context_texts = [chunk["text"] for chunk in retrieved_chunks]
#     metadata = [{"source": chunk["source"], "page": chunk["page"]} for chunk in retrieved_chunks]
#     return context_texts, metadata

# @traceable
# def cleanup_user_collection(collection_name: str):
#     delete_qdrant_collection(collection_name)