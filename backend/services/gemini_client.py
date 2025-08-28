# backend/services/gemini_client.py
import google.generativeai as genai
from typing import List, Dict, Generator, Optional
import json
from dotenv import load_dotenv
# import os
from langsmith import traceable
import logging
from config.app_config import AppConfig

load_dotenv()

class GeminiClient:
    """
    A class for handling interactions with Google's Gemini AI model.
    Provides RAG prompt formatting, response generation, and suggested questions.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.model_name = "gemini-2.5-flash"
        self.api_key = config.gemini_api_key
        
        if not self.api_key:
            raise ValueError("Gemini API key must be provided or set in GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.logger = logging.getLogger(__name__)
    
    def format_rag_prompt(self, context_chunks: List[str], user_query: str, metadata: List[Dict]) -> str:
        """
        Formats the RAG prompt with retrieved context, metadata, and user query.
        
        Args:
            context_chunks: List of text chunks retrieved from vector store
            user_query: User's original query
            metadata: Metadata associated with each context chunk
            
        Returns:
            Formatted prompt string for Gemini
        """
        if len(context_chunks) != len(metadata):
            self.logger.warning("Mismatch between context chunks and metadata length")
        
        # Combine context with metadata
        formatted_context = ""
        for i, chunk in enumerate(context_chunks):
            source = metadata[i].get("source", "Unknown Source") if i < len(metadata) else "Unknown Source"
            page = metadata[i].get("page", "Unknown Page") if i < len(metadata) else "Unknown Page"
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
    def generate_suggested_questions(self, prompt: str) -> List[str]:
        """
        Generates suggested questions based on the provided prompt.
        
        Args:
            prompt: Input prompt for generating suggested questions
            
        Returns:
            List of suggested questions
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.splitlines()
        except Exception as e:
            self.logger.error(f"❌ Failed to generate suggested questions: {e}")
            return ["What would you like to know about our university?"]
    
    @traceable(name="stream_gemini_answer", run_type="llm")
    def stream_answer(
        self, 
        context_chunks: List[str], 
        user_query: str, 
        metadata: List[Dict], 
        history: Optional[List[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """
        Streams Gemini's answer with context and conversation history.
        
        Args:
            context_chunks: List of text chunks retrieved from vector store
            user_query: User's current query
            metadata: Metadata associated with each context chunk
            history: Conversation history as list of message dictionaries
            
        Yields:
            Text chunks from the streaming response
        """
        prompt = self.format_rag_prompt(context_chunks, user_query, metadata)

        if history:
            history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
            prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

        try:
            response = self.model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.parts:
                    yield chunk.text
        except Exception as e:
            self.logger.error(f"❌ Failed to stream Gemini response: {e}")
            yield "I apologize, but I'm having trouble generating a response at the moment."
    
    def generate_answer(
        self,
        context_chunks: List[str],
        user_query: str,
        metadata: List[Dict],
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generates a complete answer without streaming.
        
        Args:
            context_chunks: List of text chunks retrieved from vector store
            user_query: User's current query
            metadata: Metadata associated with each context chunk
            history: Conversation history as list of message dictionaries
            
        Returns:
            Complete response text
        """
        prompt = self.format_rag_prompt(context_chunks, user_query, metadata)

        if history:
            history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
            prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"❌ Failed to generate Gemini response: {e}")
            return "I apologize, but I'm having trouble generating a response at the moment."
    
    def update_model(self, model_name: str) -> None:
        """
        Update the Gemini model to use.
        
        Args:
            model_name: New model name
        """
        if model_name != self.model_name:
            self.model_name = model_name
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info(f"🔄 Updated Gemini model to: {model_name}")

# import google.generativeai as genai
# from typing import List, Dict
# import json
# from dotenv import load_dotenv
# import os
# from langsmith import traceable

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-2.5-flash")

# def format_rag_prompt(context_chunks: List[str], user_query: str, metadata: List[Dict]) -> str:
#     """
#     Formats the RAG prompt with retrieved context, metadata, and user query.
#     """
#     # Combine context with metadata
#     formatted_context = ""
#     for i, chunk in enumerate(context_chunks):
#         source = metadata[i].get("source", "Unknown Source")
#         page = metadata[i].get("page", "Unknown Page")
#         formatted_context += f"[Source: {source}, Page: {page}]\n{chunk}\n\n"

#     # Query object for Gemini
#     query_object = {
#         "task": user_query,
#         "audience": "university students and prospective applicants",
#         "length": "100 words",
#         "tone": "friendly and informative",
#         "constraint": "If the user query is unrelated to university information (such as admissions, courses, departments, campus life, facilities, etc.), politely decline to answer.",
#         "role": "You are a university information chatbot. Answer queries as a representative of the university, providing helpful, accurate, and student-focused information."
#     }

#     formatted_query = json.dumps(query_object, indent=2)

#     # Final prompt
#     prompt = f"""Use the following context to answer the question. Cite sources where relevant.

#                 {formatted_context}

#                 Question: {formatted_query}
#               """
#     return prompt

# @traceable(name="generate_suggested_questions_gemini", run_type="llm")
# def generate_suggested_questions_gemini(prompt: str) -> List[str]:
#     """
#     Generates suggested questions based on the provided prompt.
#     """
#     response = model.generate_content(prompt)
#     return response.text.splitlines()

# # def generate_answer(context_chunks: List[str], user_query: str, metadata: List[Dict]) -> str:
# #     """
# #     Sends RAG prompt to Gemini and returns the response.
# #     """
# #     prompt = format_rag_prompt(context_chunks, user_query, metadata)
# #     response = model.generate_content(prompt)
# #     return response.text

# # def generate_answer(context_chunks: List[str], user_query: str, metadata: List[Dict], history: List[Dict[str, str]]) -> str:
#     # prompt = format_rag_prompt(context_chunks, user_query, metadata)

#     # # Optionally append history to prompt
#     # if history:
#     #     history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
#     #     prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

#     # response = model.generate_content(prompt, stream=True)
#     # return response.text
# from google.generativeai.types import content_types

# @traceable(name="stream_gemini_answer", run_type="llm")
# def stream_gemini_answer(context_chunks: List[str], user_query: str, metadata: List[Dict], history: List[Dict[str, str]]):
#     prompt = format_rag_prompt(context_chunks, user_query, metadata)

#     if history:
#         history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
#         prompt = f"Conversation History:\n{history_text}\n\n{prompt}"

#     response = model.generate_content(prompt, stream = True)

#     for chunk in response:
#         if chunk.parts:
#             yield chunk.text


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