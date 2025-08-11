# context_store.py
from typing import Dict, List

# Key: session_id, Value: list of message dicts
context_store: Dict[str, List[Dict[str, str]]] = {}
