from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router
from langsmith.middleware import TracingMiddleware
from config.app_config import AppConfig
from config.logging_config import setup_logging
from utils.logger import get_logger

# Setup logging first
setup_logging()
logger = get_logger("main")

try:
    config = AppConfig.from_env()
    logger.info("✅ Configuration loaded successfully")
    
    # Log configuration details
    logger.info(f"LANGCHAIN_TRACING_V2: {config.langsmith_tracing}")
    logger.info(f"LANGCHAIN_API_KEY: {'✅ Set' if config.langsmith_api_key else '❌ Missing'}")
    logger.info(f"LANGCHAIN_PROJECT: {config.langsmith_project or 'default'}")
    
except Exception as e:
    logger.critical(f"❌ Failed to load configuration: {e}")
    raise

app = FastAPI()

# Add middleware if LangSmith tracing is enabled
if config.langsmith_tracing:
    app.add_middleware(TracingMiddleware)
    logger.info("✅ LangSmith tracing enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    logger.info("Health check endpoint called")
    return {"status": "running", "tracing": config.langsmith_tracing}

app.include_router(router)
logger.info("✅ FastAPI application started successfully")

