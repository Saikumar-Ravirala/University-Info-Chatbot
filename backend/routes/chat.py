from fastapi import APIRouter, UploadFile, Form, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from services.chatbot import index_pdfs_to_qdrant,query_rag
from utils.context import get_history, save_message
import os
from typing import List
from services.gemini_client import stream_gemini_answer,generate_suggested_questions_gemini


router = APIRouter()


from anyio import to_thread
from services.pdf_parser import  extract_text_from_pdf

@router.post("/upload-pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf_paths = []
    file_names = []

    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths.append(file_path)
        file_names.append(file.filename)

    # Index PDFs into Qdrant
    await to_thread.run_sync(lambda: index_pdfs_to_qdrant(pdf_paths, file_names))

    return JSONResponse({"message": "PDFs indexed successfully", "status": "completed"})

@router.post("/chat-stream")
async def chat_stream(request: Request, query: str = Form(...)):
    session_id = request.client.host
    save_message(session_id, "user", query)
    history = get_history(session_id)

    async def bot_streamer():
        context_chunks, metadata = await to_thread.run_sync(
            lambda: query_rag(query)
        )

        full_answer = ""
        for chunk in stream_gemini_answer(context_chunks, query, metadata, history):
            full_answer += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        save_message(session_id, "bot", full_answer.strip())

    return StreamingResponse(bot_streamer(), media_type="text/event-stream")



@router.post("/generate-suggested-questions")
async def generate_suggested_questions(request: Request,files: List[UploadFile] = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    all_text = ""
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pages = await to_thread.run_sync(lambda: extract_text_from_pdf(file_path))
        # for page in pages:
        #     all_text += page + "\n"
        # for _, text in pages:  # ignore page number
        #     all_text += text + "\n"

    # Trim to avoid overloading LLM
    all_text = pages[:3000]

    # Use your LLM (Gemini/OpenAI) to create 5 questions
    # Example: Hardcoded now, replace with LLM later
    # suggested_questions = [
    #     "What courses are available?",
    #     "How to apply for admission?",
    #     "What is the tuition fee?",
    #     "Are there scholarships?",
    #     "What hostel facilities are available?"
    # ]
    query_object = {
        "task": "generate suggested questions based on the provided text",
        "size": "short not more than 1 line without numbering",
        "length": "10 words",
        "tone": "questioniare and informative",
        "example": "What courses are available?, How to apply for admission?, What is the tuition fee?, Are there scholarships?,What hostel facilities are available?"

    }

    formatted_query = json.dumps(query_object, indent=2)

    session_id = request.client.host

    # 🔁 Retrieve session history
    history = get_history(session_id)

    # 🧠 Extract relevant past context (e.g., last few bot responses)
    previous_context = "\n".join(
        msg["content"] for msg in history[-5:] if msg["role"] == "bot"
    )

    combined_context = previous_context + "\n" + all_text

    prompt = f"""Based on the following text from a university brochure,
     
            {formatted_query} 
        suggest 5 relevant questions a student might ask:\n\n{all_text}"""
    
    suggested_questions = generate_suggested_questions_gemini(prompt)

    save_message(session_id, "bot", "\n".join(suggested_questions))

    return {"questions": suggested_questions}



@router.post("/chat")
async def chat(request: Request, query: str = Form(...), files: List[UploadFile] = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Use client IP or custom header as session_id
    session_id = request.client.host

    pdf_paths = []
    file_names = []

    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths.append(file_path)
        file_names.append(file.filename)

    # Save user query to history
    save_message(session_id, "user", query)

    # Get history
    history = get_history(session_id)

    # Generate answer
    answer = answer_query_from_pdfs(pdf_paths, file_names, query, history)

    # Save bot response
    save_message(session_id, "bot", answer)

    return JSONResponse(content={"answer": answer, "history": history})

from fastapi.responses import StreamingResponse
import asyncio
import json

# @router.post("/chat-stream")
# async def chat_stream(request: Request, query: str = Form(...), files: List[UploadFile] = File(...)):
    # temp_dir = "temp"
    # os.makedirs(temp_dir, exist_ok=True)

    # session_id = request.client.host
    # pdf_paths = []
    # file_names = []

    # for file in files:
    #     file_path = os.path.join(temp_dir, file.filename)
    #     with open(file_path, "wb") as f:
    #         f.write(await file.read())
    #     pdf_paths.append(file_path)
    #     file_names.append(file.filename)

    # save_message(session_id, "user", query)
    # history = get_history(session_id)

    # # Simulated streaming of the answer
    # answer = answer_query_from_pdfs(pdf_paths, file_names, query, history)

    # async def bot_streamer():
        # full_answer = ""
        # for sentence in answer.split(". "):  # Split by sentence or any chunk logic
        #     full_answer += sentence + ". "
        #     yield f"data: {json.dumps({'chunk': sentence + '. '})}\n\n"
        #     await asyncio.sleep(0.2)  # Simulate typing delay

    #     # save_message(session_id, "bot", full_answer)
    # async def bot_streamer():
    #     full_answer = ""
    #     for char in answer:
    #         full_answer += char
    #         yield f"data: {json.dumps({'chunk': char})}\n\n"
    #         await asyncio.sleep(0.02)  # 20ms per character (adjust this!)
    
    #     save_message(session_id, "bot", full_answer)
    

    # return StreamingResponse(bot_streamer(), media_type="text/event-stream")



# @router.post("/chat-stream")
# async def chat_stream(request: Request, query: str = Form(...), files: List[UploadFile] = File(...)):
#     import os
#     from anyio import to_thread

#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     session_id = request.client.host
#     pdf_paths = []
#     file_names = []

#     for file in files:
#         file_path = os.path.join(temp_dir, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         pdf_paths.append(file_path)
#         file_names.append(file.filename)

#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     async def bot_streamer():
#         # Step 1: Run RAG pipeline to get chunks + metadata
#         context_chunks, metadata = await to_thread.run_sync(
#             lambda: get_rag_context_from_pdfs(pdf_paths, file_names, query)
#         )

#         # Step 2: Stream Gemini response
#         full_answer = ""
#         for chunk in await to_thread.run_sync(
#             lambda: list(stream_gemini_answer(context_chunks, query, metadata, history))
#         ):
#             full_answer += chunk
#             yield f"data: {json.dumps({'chunk': chunk})}\n\n"
#             await asyncio.sleep(0.5)

#         save_message(session_id, "bot", full_answer)

#     return StreamingResponse(bot_streamer(), media_type="text/event-stream")

# @router.post("/chat-stream")
# async def chat_stream(request: Request, query: str = Form(...), files: List[UploadFile] = File(...)):
#     import os
#     from anyio import to_thread

#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     session_id = request.client.host
#     pdf_paths = []
#     file_names = []

#     for file in files:
#         file_path = os.path.join(temp_dir, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         pdf_paths.append(file_path)
#         file_names.append(file.filename)

#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     async def bot_streamer():
#         # Step 1: Run RAG pipeline to get chunks + metadata
#         context_chunks, metadata = await to_thread.run_sync(
#             lambda: get_rag_context_from_pdfs(pdf_paths, file_names, query)
#         )

#         # Step 2: Stream Gemini response
#         full_answer = ""

#         # Fetch Gemini streamed response in a thread
#         chunks = await to_thread.run_sync(
#             lambda: list(stream_gemini_answer(context_chunks, query, metadata, history))
#         )

#         # Step 3: Stream words (or characters) gradually
#         for chunk in chunks:
#             #words = chunk.split(" ")  # For char-by-char: use `list(chunk)`
#             words = list(chunk)  # Stream character-by-character

#             for word in words:
#                 full_answer += word + " "
#                 yield f"data: {json.dumps({'chunk': word + ' '})}\n\n"
#                 await asyncio.sleep(0.05)  # Adjust to control typing speed

#         # Step 4: Save the full message to history
#         save_message(session_id, "bot", full_answer.strip())

#     return StreamingResponse(bot_streamer(), media_type="text/event-stream")

#working version latest 13/8
# @router.post("/chat-stream")
# async def chat_stream(request: Request, query: str = Form(...), files: List[UploadFile] = File(...)):
#     from anyio import to_thread
#     import os

#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     session_id = request.client.host
#     pdf_paths = []
#     file_names = []

#     for file in files:
#         file_path = os.path.join(temp_dir, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         pdf_paths.append(file_path)
#         file_names.append(file.filename)

#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     async def bot_streamer():
#         context_chunks, metadata = await to_thread.run_sync(
#             lambda: get_rag_context_from_pdfs(pdf_paths, file_names, query)
#         )

#         full_answer = ""

#         # chunks = await to_thread.run_sync(
#         #     lambda: list(stream_gemini_answer(context_chunks, query, metadata, history))
#         # )

#         # Stream the answer character by character
#         # for chunk in chunks:
#         #     for char in chunk:
#         #         if char.strip() == "" and char != " ":
#         #             continue  # Ignore tabs, newlines, etc.
#         #         full_answer += char
#         #         yield f"data: {json.dumps({'chunk': char})}\n\n"
#         #         await asyncio.sleep(0.01)

#         # Stream directly from Gemini as chunks come in
#         for chunk in stream_gemini_answer(context_chunks, query, metadata, history):
#             full_answer += chunk
#             yield f"data: {json.dumps({'chunk': chunk})}\n\n"

#         save_message(session_id, "bot", full_answer.strip())

#     return StreamingResponse(bot_streamer(), media_type="text/event-stream")


# @router.post("/chat")
# async def chat(query: str = Form(...), files: List[UploadFile] = File(...)):
#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     pdf_paths = []
#     file_names = []

#     for file in files:
#         file_path = os.path.join(temp_dir, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         pdf_paths.append(file_path)
#         file_names.append(file.filename)

#     answer = answer_query_from_pdfs(pdf_paths, file_names, query)
#     return JSONResponse(content={"answer": answer})

# from fastapi import APIRouter, UploadFile, Form
# from fastapi.responses import JSONResponse
# import numpy as np

# from services.pdf_parser import extract_text_from_pdf
# from services.chunker import chunk_text
# from services.embedder import get_embeddings
# from services.vector_store import build_faiss_index, search_faiss_index
# from services.gemini_client import generate_answer

# router = APIRouter()

# # @router.post("/chat")
# # async def chat(query: str = Form(...), file: UploadFile = Form(...)):
# #     print("Received query:")
# #     print("Received:", query, file.filename)
# #     return JSONResponse(content={"answer": f"Received query: {query}, file: {file.filename}"})



# @router.post("/chat")
# async def chat(query: str = Form(...), file: UploadFile = Form(...)):
#     contents = await file.read()
#     temp_path = "temp/temp.pdf"
#     with open(temp_path, "wb") as f:
#         f.write(contents)

#     text = extract_text_from_pdf(temp_path)
#     chunks = chunk_text(text)
#     embeddings = get_embeddings(chunks)
#     index = build_faiss_index(np.array(embeddings))

#     query_embedding = get_embeddings([query])[0]
#     top_indices = search_faiss_index(index, query_embedding)

#     context = " ".join([chunks[i] for i in top_indices])
#     answer = generate_answer(query, context)

#     return JSONResponse(content={"answer": answer})

# # from services.chatbot import answer_query_from_pdf

# # @router.post("/chat")
# # async def chat(query: str = Form(...), file: UploadFile = Form(...)):
# #     contents = await file.read()
# #     temp_path = "temp/temp.pdf"
# #     with open(temp_path, "wb") as f:
# #         f.write(contents)

# #     answer = answer_query_from_pdf(temp_path, query)
# #     return JSONResponse(content={"answer": answer})



# # from fastapi import UploadFile, File, APIRouter



# # @router.post("/suggested-questions")
# # # async def suggested_questions(file: UploadFile = File(...)):
# #     contents = await file.read()
# #     temp_path = "temp/temp.pdf"

# #     # Save uploaded PDF
# #     with open(temp_path, "wb") as f:
# #         f.write(contents)

# #     # Extract text from PDF
# #     text = extract_text_from_pdf(temp_path)
# #     short_text = text[:3000]

# #     # Create prompt
# #     # prompt = f"""
# #     #             You are an academic assistant. Based on the following paper content, generate 5–6 smart questions a student might ask:

# #     #             \"\"\"{short_text}\"\"\"

# #     #             List the questions only, without numbering or explanation.
# #     # """
# #     prompt = """
# #                 Read the provided research paper and generate 5 concise questions.
# #                 Each question must be no more than 10 words long.

# #                 Example:
# #                 - Summarize the main findings of this paper
# #                 - What methodology was used in this research?
# #                 - List the key references cited
# #                 - Explain the theoretical framework
# #                 - What are the limitations mentioned?
# #                 List the questions only, without numbering or explanation.
# #                 Now, generate questions:
# #             """



# #     # Call your LLM
# #     questions_text = generate_answer("Generate questions", prompt)

# #     # Parse and clean
# #     questions = [q.strip("-• ").strip() for q in questions_text.strip().split("\n") if q.strip()]
# #     return JSONResponse(content={"questions": questions[:6]})
