import google.generativeai as genai
from typing import List, Dict
import json
from dotenv import load_dotenv
import os
from langsmith import traceable

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def format_rag_prompt(context_chunks: List[str], user_query: str, metadata: List[Dict]) -> str:
    """
    Formats the RAG prompt with retrieved context, metadata, and user query.
    """
    # Combine context with metadata
    formatted_context = ""
    for i, chunk in enumerate(context_chunks):
        source = metadata[i].get("source", "Unknown Source")
        page = metadata[i].get("page", "Unknown Page")
        formatted_context += f"[Source: {source}, Page: {page}]\n{chunk}\n\n"

    # Query object for Gemini
    query_object = {
        "task": user_query,
        "audience": "university students and prospective applicants",
        "length": "100 words",
        "tone": "friendly and informative",
        "constraint": "If the user query is unrelated to university information (such as admissions, courses, departments, campus life, facilities, etc.), politely decline to answer.",
        "role": "You are a university information chatbot. Answer queries as a representative of the university, providing helpful, accurate, and student-focused information."
    }

    formatted_query = json.dumps(query_object, indent=2)

    # Final prompt
    prompt = f"""Use the following context to answer the question. Cite sources where relevant.

                {formatted_context}

                Question: {formatted_query}
              """
    return prompt

@traceable(name="generate_suggested_questions_gemini", run_type="llm")
def generate_suggested_questions_gemini(prompt: str) -> List[str]:
    """
    Generates suggested questions based on the provided prompt.
    """
    response = model.generate_content(prompt)
    return response.text.splitlines()

# def generate_answer(context_chunks: List[str], user_query: str, metadata: List[Dict]) -> str:
#     """
#     Sends RAG prompt to Gemini and returns the response.
#     """
#     prompt = format_rag_prompt(context_chunks, user_query, metadata)
#     response = model.generate_content(prompt)
#     return response.text

# def generate_answer(context_chunks: List[str], user_query: str, metadata: List[Dict], history: List[Dict[str, str]]) -> str:
    # prompt = format_rag_prompt(context_chunks, user_query, metadata)

    # # Optionally append history to prompt
    # if history:
    #     history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
    #     prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

    # response = model.generate_content(prompt, stream=True)
    # return response.text
from google.generativeai.types import content_types

@traceable(name="stream_gemini_answer", run_type="llm")
def stream_gemini_answer(context_chunks: List[str], user_query: str, metadata: List[Dict], history: List[Dict[str, str]]):
    prompt = format_rag_prompt(context_chunks, user_query, metadata)

    if history:
        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
        prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

    response = model.generate_content(prompt, stream = True)

    for chunk in response:
        if chunk.parts:
            yield chunk.text


# # gemini_client.py
# import google.generativeai as genai
# from typing import List
# import json
# # from config import configure_gemini


# # configure_gemini(key)
# model = genai.GenerativeModel("gemini-2.5-flash")

# def format_rag_prompt(context_chunks: List[str], user_query: str) -> str:
#     """
#     Formats the RAG prompt with retrieved context and user query.
#     """
#     context = "\n\n".join(context_chunks)

#     # query_object = {
#     #     "task": user_query,
#     #     "audience": "college students",
#     #     "length": "100 words",
#     #     "tone": "curious",
#     #     "constraint": "If the user query is irrelevant to the uploaded academic documents or research papers, politely decline to answer."

#     # }

#     query_object = {
#     "task": user_query,
#     "audience": "university students and prospective applicants",
#     "length": "100 words",
#     "tone": "friendly and informative",
#     "constraint": "If the user query is unrelated to university information (such as admissions, courses, departments, campus life, facilities, etc.), politely decline to answer.",
#     "role": "You are a university information chatbot. Answer queries as a representative of the university, providing helpful, accurate, and student-focused information."
#     }


#     formatted_query = json.dumps(query_object, indent=2)

#     prompt = f"""Use the following context to answer the question.

#                 {context}

#                 Question: {formatted_query}
#             """
#     return prompt

# def generate_answer(context_chunks: List[str], user_query: str) -> str:
#     """
#     Sends RAG prompt to Gemini and returns the response.
#     """
#     prompt = format_rag_prompt(context_chunks, user_query)
#     response = model.generate_content(prompt)
#     return response.text


# """
# {
#     "task":"summmarize this article",
#     "audience":"college students",
#     "length":"100 words",
#     "tone":"curious"

    
# }
# {
#   "task": "summarize this article",
#   "audience": "college students",
#   "length": "100 words",
#   "tone": "curious",
#   "constraint": "If the user query is irrelevant to the uploaded academic documents or research papers, politely decline to answer."
# }

# """