# config.py
import google.generativeai as genai

def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)
