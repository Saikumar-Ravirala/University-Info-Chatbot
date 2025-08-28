import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    # API Keys
    gemini_api_key: str
    qdrant_url: str
    qdrant_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    
    # Application Settings
    langsmith_project: Optional[str] = None
    langsmith_tracing: bool = False
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    log_level: str = "INFO"

    @classmethod
    def from_env(cls):
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
            langsmith_project=os.getenv("LANGSMITH_PROJECT"),
            langsmith_tracing=os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
            chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
            top_k=int(os.getenv("TOP_K", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )