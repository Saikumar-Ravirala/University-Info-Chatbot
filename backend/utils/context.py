# utils/context.py
from context_store import context_store
from typing import List, Dict

def get_history(session_id: str) -> List[Dict[str, str]]:
    return context_store.get(session_id, [])

def save_message(session_id: str, role: str, content: str):
    if session_id not in context_store:
        context_store[session_id] = []
    context_store[session_id].append({"role": role, "content": content})
