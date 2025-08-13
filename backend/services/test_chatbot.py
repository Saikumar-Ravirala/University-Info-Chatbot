# test_chatbot.py
from chatbot import answer_query_from_pdf
from config import configure_gemini

key = "abcdefghijklmnopqrstuvwxyz1234567890"  # Replace with your actual API key

configure_gemini(key)

pdf_path = "pdf's\Attention_is_all_you_need.pdf"
query = "What is the main contribution of this paper?"

response = answer_query_from_pdf(pdf_path, query)
print("Gemini's Answer:\n", response)
