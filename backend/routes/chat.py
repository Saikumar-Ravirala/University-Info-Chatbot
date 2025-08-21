from fastapi import APIRouter, UploadFile, Form, File, Request
from fastapi.responses import JSONResponse, StreamingResponse
from services.chatbot import index_pdfs_to_qdrant, query_rag, cleanup_user_collection
from utils.context import get_history, save_message
from services.gemini_client import stream_gemini_answer, generate_suggested_questions_gemini
from services.pdf_parser import extract_text_from_pdf
from anyio import to_thread
from typing import List
import os, json, shutil, asyncio, logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 🆕 Upload PDFs and index to session-specific collection
@router.post("/upload-pdfs")
async def upload_pdfs(request: Request, files: List[UploadFile] = File(...)):
    session_id = (await request.form()).get("session_id")
    if not session_id:
        return JSONResponse({"error": "Missing session_id"}, status_code=400)

    collection_name = f"user-session-{session_id}"
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf_paths = []
    file_names = []

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            pdf_paths.append(file_path)
            file_names.append(file.filename)

        await to_thread.run_sync(lambda: index_pdfs_to_qdrant(pdf_paths, file_names, collection_name))
        logger.info(f"Indexed PDFs for session {session_id}")
    except Exception as e:
        logger.error(f"Indexing failed for session {session_id}: {str(e)}")
        return JSONResponse({"error": f"Indexing failed: {str(e)}"}, status_code=500)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return JSONResponse({"message": "PDFs indexed successfully", "status": "completed"})

# 🆕 Stream chat response using session-specific collection
@router.post("/chat-stream")
async def chat_stream(request: Request):
    form = await request.form()
    query = form.get("query")
    session_id = form.get("session_id")

    if not query or not session_id:
        return JSONResponse({"error": "Missing query or session_id"}, status_code=400)

    collection_name = f"user-session-{session_id}"
    save_message(session_id, "user", query)
    history = get_history(session_id)

    async def bot_streamer():
        try:
            context_chunks, metadata = await to_thread.run_sync(
                lambda: query_rag(query, collection_name=collection_name, top_k=3)
            )
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        full_answer = ""
        for chunk in stream_gemini_answer(context_chunks, query, metadata, history):
            full_answer += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            await asyncio.sleep(0.5)  # keep-alive pacing

        save_message(session_id, "bot", full_answer.strip())

    return StreamingResponse(bot_streamer(), media_type="text/event-stream")

# 🆕 Generate suggested questions using session context
@router.post("/generate-suggested-questions")
async def generate_suggested_questions(request: Request, files: List[UploadFile] = File(...)):
    form = await request.form()
    session_id = form.get("session_id")
    if not session_id:
        return JSONResponse({"error": "Missing session_id"}, status_code=400)

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    all_text = ""

    try:
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            pages = await to_thread.run_sync(lambda: extract_text_from_pdf(file_path))
            all_text += pages[:3000]  # Trim for LLM
    except Exception as e:
        return JSONResponse({"error": f"PDF parsing failed: {str(e)}"}, status_code=500)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    query_object = {
        "task": "generate suggested questions based on the provided text",
        "size": "short not more than 1 line without numbering",
        "length": "10 words",
        "tone": "questionnaire and informative",
        "example": "What courses are available?, How to apply for admission?, What is the tuition fee?, Are there scholarships?, What hostel facilities are available?"
    }

    formatted_query = json.dumps(query_object, indent=2)
    history = get_history(session_id)
    previous_context = "\n".join(msg["content"] for msg in history[-5:] if msg["role"] == "bot")
    combined_context = previous_context + "\n" + all_text

    prompt = f"""Based on the following text from a university brochure,
{formatted_query}
suggest 5 relevant questions a student might ask:\n\n{combined_context}"""

    try:
        suggested_questions = generate_suggested_questions_gemini(prompt)
        save_message(session_id, "bot", "\n".join(suggested_questions))
    except Exception as e:
        return JSONResponse({"error": f"LLM generation failed: {str(e)}"}, status_code=500)

    return {"questions": suggested_questions}

# 🆕 Cleanup session collection (called on tab close)
@router.post("/cleanup-session")
async def cleanup_session(request: Request):
    try:
        body = await request.json()
        session_id = body.get("session_id")
        if not session_id:
            return JSONResponse({"error": "Missing session_id"}, status_code=400)

        collection_name = f"user-session-{session_id}"
        cleanup_user_collection(collection_name)
        logger.info(f"Cleaned up collection for session {session_id}")
        return JSONResponse({"status": "collection deleted"})
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

# from fastapi import APIRouter, UploadFile, Form, File, Request
# from fastapi.responses import JSONResponse, StreamingResponse
# from services.chatbot import index_pdfs_to_qdrant, query_rag, cleanup_user_collection
# from utils.context import get_history, save_message
# from services.gemini_client import stream_gemini_answer, generate_suggested_questions_gemini
# from services.pdf_parser import extract_text_from_pdf
# from anyio import to_thread
# from typing import List
# import os, json

# router = APIRouter()

# # 🆕 Upload PDFs and index to session-specific collection
# @router.post("/upload-pdfs")
# async def upload_pdfs(request: Request, files: List[UploadFile] = File(...)):
#     session_id = (await request.form()).get("session_id")
#     if not session_id:
#         return JSONResponse({"error": "Missing session_id"}, status_code=400)

#     collection_name = f"user-session-{session_id}"

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

#     await to_thread.run_sync(lambda: index_pdfs_to_qdrant(pdf_paths, file_names, collection_name))

#     return JSONResponse({"message": "PDFs indexed successfully", "status": "completed"})

# # 🆕 Stream chat response using session-specific collection
# @router.post("/chat-stream")
# async def chat_stream(request: Request):
#     form = await request.form()
#     query = form.get("query")
#     session_id = form.get("session_id")

#     if not query or not session_id:
#         return JSONResponse({"error": "Missing query or session_id"}, status_code=400)

#     collection_name = f"user-session-{session_id}"

#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     async def bot_streamer():
#         context_chunks, metadata = await to_thread.run_sync(
#             lambda: query_rag(query, collection_name=collection_name, top_k=3)
#         )

#         full_answer = ""
#         for chunk in stream_gemini_answer(context_chunks, query, metadata, history):
#             full_answer += chunk
#             yield f"data: {json.dumps({'chunk': chunk})}\n\n"

#         save_message(session_id, "bot", full_answer.strip())

#     return StreamingResponse(bot_streamer(), media_type="text/event-stream")

# # 🆕 Generate suggested questions using session context
# @router.post("/generate-suggested-questions")
# async def generate_suggested_questions(request: Request, files: List[UploadFile] = File(...)):
#     form = await request.form()
#     session_id = form.get("session_id")
#     if not session_id:
#         return JSONResponse({"error": "Missing session_id"}, status_code=400)

#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     all_text = ""
#     for file in files:
#         file_path = os.path.join(temp_dir, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         pages = await to_thread.run_sync(lambda: extract_text_from_pdf(file_path))
#         all_text += pages[:3000]  # Trim for LLM

#     query_object = {
#         "task": "generate suggested questions based on the provided text",
#         "size": "short not more than 1 line without numbering",
#         "length": "10 words",
#         "tone": "questionnaire and informative",
#         "example": "What courses are available?, How to apply for admission?, What is the tuition fee?, Are there scholarships?, What hostel facilities are available?"
#     }

#     formatted_query = json.dumps(query_object, indent=2)
#     history = get_history(session_id)
#     previous_context = "\n".join(msg["content"] for msg in history[-5:] if msg["role"] == "bot")
#     combined_context = previous_context + "\n" + all_text

#     prompt = f"""Based on the following text from a university brochure,
#         {formatted_query}
#         suggest 5 relevant questions a student might ask:\n\n{combined_context}"""

#     suggested_questions = generate_suggested_questions_gemini(prompt)
#     save_message(session_id, "bot", "\n".join(suggested_questions))

#     return {"questions": suggested_questions}

# # 🆕 Cleanup session collection (called on tab close)
# @router.post("/cleanup-session")
# async def cleanup_session(request: Request):
#     try:
#         body = await request.json()
#         session_id = body.get("session_id")
#         if not session_id:
#             return JSONResponse({"error": "Missing session_id"}, status_code=400)

#         collection_name = f"user-session-{session_id}"
#         cleanup_user_collection(collection_name)
#         return JSONResponse({"status": "collection deleted"})
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)
