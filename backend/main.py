from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router

app = FastAPI()

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
