from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router
from langsmith.middleware import TracingMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ Verify LangSmith configuration
print("🔍 LangSmith Configuration:")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_API_KEY: {'✅ Set' if os.getenv('LANGSMITH_API_KEY') else '❌ Missing'}")
print(f"LANGCHAIN_PROJECT: {os.getenv('LANGSMITH_PROJECT', 'default')}")

app = FastAPI()

app.add_middleware(TracingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ FastAPI starting...")

@app.get("/")
def health():
    return {"status": "running"}



app.include_router(router)
