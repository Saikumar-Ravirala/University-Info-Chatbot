from config.app_config import AppConfig
from utils.logger import get_logger
from services.embedder import Embedder
from services.vector_store_qdrant import QdrantVectorStore
from services.gemini_client import GeminiClient
from services.chatbot import RAGService  # Make sure this exists

class ServiceManager:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger("ServiceManager")
        
        # Initialize services
        self.embedder = Embedder(config)
        self.vector_store = QdrantVectorStore(config)
        self.gemini_client = GeminiClient(config)
        self.rag_service = RAGService(config, self.embedder, self.vector_store, self.gemini_client)
        
        self.logger.info("✅ All services initialized successfully")
    
    def get_services(self):
        return {
            "embedder": self.embedder,
            "vector_store": self.vector_store,
            "gemini_client": self.gemini_client,
            "rag_service": self.rag_service
        }