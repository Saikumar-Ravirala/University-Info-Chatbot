# backend/routes/chat.py
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Request, Body, Form
from fastapi.responses import JSONResponse, StreamingResponse
from config.app_config import AppConfig
from services.services_manager import ServiceManager
from utils.context import get_history, save_message
from services.parser.pdf_parser import PDFParser
from anyio import to_thread
from utils.logger import get_logger
import json
import shutil
import asyncio
import uuid
import os

# Initialize configuration and services
config = AppConfig.from_env()
service_manager = ServiceManager(config)
rag_service = service_manager.rag_service
gemini_client = service_manager.gemini_client
pdf_parser = PDFParser()

router = APIRouter()
logger = get_logger("chat_routes")

@router.post("/upload-pdfs")
async def upload_pdfs(request: Request, files: List[UploadFile] = File(...)):
    logger.info("Upload PDFs endpoint called")
    
    form = await request.form()
    session_id = form.get("session_id") or str(uuid.uuid4())
    collection_name = f"user-session-{session_id}"
    temp_dir = "temp"
    
    try:
        pdf_paths = []
        file_names = []
        os.makedirs(temp_dir, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            pdf_paths.append(file_path)
            file_names.append(file.filename)
            logger.debug(f"Saved PDF file: {file.filename}")

        logger.info(f"Starting PDF indexing for session: {session_id}")
        await to_thread.run_sync(
            lambda: rag_service.index_documents_to_qdrant(pdf_paths, file_names, collection_name)
        )
        logger.info(f"✅ Successfully indexed PDFs for session {session_id}")
        
        return JSONResponse({
            "message": "PDFs indexed successfully",
            "status": "completed",
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"❌ PDF indexing failed for session {session_id}: {str(e)}")
        return JSONResponse({"error": f"Indexing failed: {str(e)}"}, status_code=500)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.debug("Cleaned up temporary directory")

@router.post("/upload-docs")
async def upload_docs(request: Request, files: List[UploadFile] = File(...)):
    logger.info("Upload documents endpoint called")
    
    form = await request.form()
    session_id = form.get("session_id") or str(uuid.uuid4())
    collection_name = f"user-session-{session_id}"
    temp_dir = "temp"
    
    try:
        file_paths = []
        file_names = []
        os.makedirs(temp_dir, exist_ok=True)

        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            file_paths.append(file_path)
            file_names.append(file.filename)
            logger.debug(f"Saved document: {file.filename}")

        logger.info(f"Starting document indexing for session: {session_id}")
        await to_thread.run_sync(
            lambda: rag_service.index_documents_to_qdrant(file_paths, file_names, collection_name)
        )
        logger.info(f"✅ Successfully indexed documents for session {session_id}")
        
        return JSONResponse({
            "message": "Documents indexed successfully",
            "status": "completed",
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"❌ Document indexing failed for session {session_id}: {str(e)}")
        return JSONResponse({"error": f"Indexing failed: {str(e)}"}, status_code=500)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.debug("Cleaned up temporary directory")

@router.post("/upload-urls")
async def upload_urls(
    request: Request,
    urls: List[str] = Form(...),
    selectors: Optional[List[str]] = Form(default=["*"]),
    session_id: Optional[str] = Form(default=None)
):
    logger.info("Upload URLs endpoint called")
    
    form = await request.form()
    session_id = form.get("session_id") or str(uuid.uuid4())
    collection_name = f"user-session-{session_id}"

    try:
        logger.info(f"Starting URL indexing for session: {session_id}")
        for url in urls:
            if not url:
                continue
            logger.debug(f"Processing URL: {url}")
            await rag_service.index_scraped_url_to_qdrant(url, selectors, collection_name)
            logger.info(f"✅ Scraped and indexed URL: {url}")
        
        logger.info(f"✅ Successfully indexed all URLs for session {session_id}")
        
        return JSONResponse({
            "message": "URLs indexed successfully",
            "status": "completed",
            "session_id": session_id,
        })
        
    except Exception as e:
        logger.error(f"❌ URL ingestion failed for session {session_id}: {str(e)}")
        return JSONResponse(
            {"error": f"URL ingestion failed: {str(e)}"}, status_code=500
        )

@router.post("/chat")
async def chat(payload: dict = Body(...)):
    logger.info("Chat endpoint called")
    
    query = payload.get("query")
    session_id = payload.get("session_id") or str(uuid.uuid4())

    if not query:
        logger.warning("Chat request missing query")
        return JSONResponse({"error": "Missing query"}, status_code=400)

    collection_name = f"user-session-{session_id}"
    save_message(session_id, "user", query)
    history = get_history(session_id)

    try:
        logger.info(f"Processing chat query for session {session_id}: '{query[:50]}...'")
        
        context_chunks, metadata = await to_thread.run_sync(
            lambda: rag_service.query_rag(query, collection_name=collection_name, top_k=3)
        )
        logger.debug(f"Retrieved {len(context_chunks)} context chunks")
        
        full_answer = "".join(gemini_client.stream_answer(
            context_chunks, query, metadata, history
        ))
        
        save_message(session_id, "bot", full_answer.strip())
        logger.info(f"✅ Successfully generated answer for session {session_id}")
        
        return {
            "answer": full_answer,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"❌ Chat processing failed for session {session_id}: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/chat-stream")
async def chat_stream(request: Request):
    logger.info("Chat stream endpoint called")
    
    form = await request.form()
    query = form.get("query")
    session_id = form.get("session_id") or str(uuid.uuid4())

    if not query:
        logger.warning("Chat stream request missing query")
        return JSONResponse({"error": "Missing query"}, status_code=400)

    collection_name = f"user-session-{session_id}"
    save_message(session_id, "user", query)
    history = get_history(session_id)

    async def bot_streamer():
        try:
            logger.info(f"Starting stream processing for session {session_id}: '{query[:50]}...'")
            
            context_chunks, metadata = await to_thread.run_sync(
                lambda: rag_service.query_rag(query, collection_name=collection_name, top_k=3)
            )
            logger.debug(f"Retrieved {len(context_chunks)} context chunks for streaming")

            full_answer = ""
            for chunk in gemini_client.stream_answer(context_chunks, query, metadata, history):
                full_answer += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                await asyncio.sleep(0.1)  # Reduced sleep for better streaming

            save_message(session_id, "bot", full_answer.strip())
            logger.info(f"✅ Stream processing completed for session {session_id}")
            
        except Exception as e:
            error_msg = f"Stream processing failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return StreamingResponse(bot_streamer(), media_type="text/event-stream")

@router.post("/generate-suggested-questions")
async def generate_suggested_questions(request: Request, files: List[UploadFile] = File(...)):
    logger.info("Generate suggested questions endpoint called")
    
    form = await request.form()
    session_id = form.get("session_id") or str(uuid.uuid4())
    temp_dir = "temp"
    all_text = ""

    try:
        os.makedirs(temp_dir, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            logger.debug(f"Processing file for questions: {file.filename}")
            pages = await to_thread.run_sync(lambda: pdf_parser.extract_text_from_pdf(file_path))
            all_text += pages[:3000]
        
        logger.debug(f"Extracted {len(all_text)} characters for question generation")

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

        logger.info("Generating suggested questions using Gemini")
        suggested_questions = gemini_client.generate_suggested_questions(prompt)
        
        save_message(session_id, "bot", "\n".join(suggested_questions))
        logger.info(f"✅ Generated {len(suggested_questions)} suggested questions for session {session_id}")

        return {
            "questions": suggested_questions,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"❌ Suggested questions generation failed: {str(e)}")
        return JSONResponse({"error": f"LLM generation failed: {str(e)}"}, status_code=500)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.debug("Cleaned up temporary directory")

@router.post("/cleanup-session")
async def cleanup_session(request: Request):
    logger.info("Cleanup session endpoint called")
    
    try:
        body = await request.json()
        session_id = body.get("session_id")
        
        if not session_id:
            logger.warning("Cleanup request missing session_id")
            return JSONResponse({"error": "Missing session_id"}, status_code=400)

        collection_name = f"user-session-{session_id}"
        logger.info(f"Cleaning up collection for session: {session_id}")
        
        rag_service.cleanup_collection(collection_name)
        logger.info(f"✅ Successfully cleaned up collection for session {session_id}")
        
        return JSONResponse({"status": "collection deleted"})
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


# Similar updates for other endpoints...
# Continue this pattern for upload-docs, upload-urls, chat, etc.
# from dotenv import load_dotenv
# load_dotenv()

# from typing import Optional, List
# from fastapi import APIRouter, UploadFile, File, Request, Body, Form
# from fastapi.responses import JSONResponse, StreamingResponse
# from services.chatbot import index_pdfs_to_qdrant, query_rag, cleanup_user_collection,index_scraped_url_to_qdrant,index_docs_to_qdrant
# from utils.context import get_history, save_message
# from services.gemini_client import stream_gemini_answer, generate_suggested_questions_gemini
# from services.parser.pdf_parser import extract_text_from_pdf
# from anyio import to_thread
# import os, json, shutil, asyncio, logging, uuid
# from langsmith import Client

# router = APIRouter()
# logger = logging.getLogger(__name__)
# client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# # 🆕 Upload PDFs and index to session-specific collection
# @router.post("/upload-pdfs")
# async def upload_pdfs(request: Request, files: List[UploadFile] = File(...)):
#     print("Upload PDFs endpoint called")
#     form = await request.form()
#     session_id = form.get("session_id") or str(uuid.uuid4())  # ✅ fallback
#     collection_name = f"user-session-{session_id}"
#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     pdf_paths = []
#     file_names = []

#     try:
#         for file in files:
#             file_path = os.path.join(temp_dir, file.filename)
#             with open(file_path, "wb") as f:
#                 f.write(await file.read())
#             pdf_paths.append(file_path)
#             file_names.append(file.filename)

#         print("about to index PDFs to Qdrant")
#         await to_thread.run_sync(lambda: index_pdfs_to_qdrant(pdf_paths, file_names, collection_name))
#         logger.info(f"Indexed PDFs for session {session_id}")
#     except Exception as e:
#         logger.error(f"Indexing failed for session {session_id}: {str(e)}")
#         return JSONResponse({"error": f"Indexing failed: {str(e)}"}, status_code=500)
#     finally:
#         shutil.rmtree(temp_dir, ignore_errors=True)

#     return JSONResponse({
#         "message": "PDFs indexed successfully",
#         "status": "completed",
#         "session_id": session_id  # ✅ return for reuse
#     })

# @router.post("/upload-docs")
# async def upload_docs(request: Request, files: List[UploadFile] = File(...)):
#     form = await request.form()
#     session_id = form.get("session_id") or str(uuid.uuid4())
#     collection_name = f"user-session-{session_id}"
#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)

#     file_paths = []
#     file_names = []

#     try:
#         for file in files:
#             file_path = os.path.join(temp_dir, file.filename)
#             with open(file_path, "wb") as f:
#                 f.write(await file.read())
#             file_paths.append(file_path)
#             file_names.append(file.filename)

#         await to_thread.run_sync(lambda: index_docs_to_qdrant(file_paths, file_names, collection_name))
#         logger.info(f"Indexed docs for session {session_id}")
#     except Exception as e:
#         logger.error(f"Indexing failed for session {session_id}: {str(e)}")
#         return JSONResponse({"error": f"Indexing failed: {str(e)}"}, status_code=500)
#     finally:
#         shutil.rmtree(temp_dir, ignore_errors=True)

#     return JSONResponse({
#         "message": "Documents indexed successfully",
#         "status": "completed",
#         "session_id": session_id
#     })


# @router.post("/upload-urls")
# async def upload_urls(
#     request: Request,
#     urls: List[str] = Form(...),
#     selectors: Optional[List[str]] = Form(default=["*"]),
#     session_id: Optional[str] = Form(default=None)
# ):
#     form = await request.form()
#     session_id = form.get("session_id") or str(uuid.uuid4())
#     collection_name = f"user-session-{session_id}"

#     try:
#         for url in urls:
#             if not url:
#                 continue
#             await index_scraped_url_to_qdrant(url, selectors, collection_name)
#             logger.info(f"Scraped and indexed URL: {url}")
#     except Exception as e:
#         logger.error(f"URL ingestion failed for session {session_id}: {str(e)}")
#         return JSONResponse(
#             {"error": f"URL ingestion failed: {str(e)}"}, status_code=500
#         )

#     return JSONResponse(
#         {
#             "message": "URLs indexed successfully",
#             "status": "completed",
#             "session_id": session_id,
#         }
#     )

# @router.post("/chat")
# async def chat(
#     payload: dict = Body(...),
# ):
#     query = payload.get("query")
#     session_id = payload.get("session_id") or str(uuid.uuid4())

#     if not query:
#         return JSONResponse({"error": "Missing query"}, status_code=400)

#     collection_name = f"user-session-{session_id}"
#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     try:
#         context_chunks, metadata = await to_thread.run_sync(
#             lambda: query_rag(query, collection_name=collection_name, top_k=3)
#         )
#         full_answer = "".join(stream_gemini_answer(context_chunks, query, metadata, history))
#         save_message(session_id, "bot", full_answer.strip())
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

#     return {
#         "answer": full_answer,
#         "session_id": session_id
#     }


# # 🆕 Stream chat response using session-specific collection
# @router.post("/chat-stream")
# async def chat_stream(request: Request):
#     form = await request.form()
#     query = form.get("query")
#     session_id = form.get("session_id") or str(uuid.uuid4())  # ✅ fallback

#     if not query:
#         return JSONResponse({"error": "Missing query"}, status_code=400)

#     collection_name = f"user-session-{session_id}"
#     save_message(session_id, "user", query)
#     history = get_history(session_id)

#     async def bot_streamer():
#         try:
#             context_chunks, metadata = await to_thread.run_sync(
#                 lambda: query_rag(query, collection_name=collection_name, top_k=3)
#             )
#         except Exception as e:
#             yield f"data: {json.dumps({'error': str(e)})}\n\n"
#             return

#         full_answer = ""
#         for chunk in stream_gemini_answer(context_chunks, query, metadata, history):
#             full_answer += chunk
#             yield f"data: {json.dumps({'chunk': chunk})}\n\n"
#             await asyncio.sleep(0.5)

#         save_message(session_id, "bot", full_answer.strip())

#     return StreamingResponse(bot_streamer(), media_type="text/event-stream")

# # 🆕 Generate suggested questions using session context
# @router.post("/generate-suggested-questions")
# async def generate_suggested_questions(request: Request, files: List[UploadFile] = File(...)):
#     form = await request.form()
#     session_id = form.get("session_id") or str(uuid.uuid4())  # ✅ fallback

#     temp_dir = "temp"
#     os.makedirs(temp_dir, exist_ok=True)
#     all_text = ""

#     try:
#         for file in files:
#             file_path = os.path.join(temp_dir, file.filename)
#             with open(file_path, "wb") as f:
#                 f.write(await file.read())
#             pages = await to_thread.run_sync(lambda: extract_text_from_pdf(file_path))
#             all_text += pages[:3000]
#     except Exception as e:
#         return JSONResponse({"error": f"PDF parsing failed: {str(e)}"}, status_code=500)
#     finally:
#         shutil.rmtree(temp_dir, ignore_errors=True)

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
# {formatted_query}
# suggest 5 relevant questions a student might ask:\n\n{combined_context}"""

#     try:
#         suggested_questions = generate_suggested_questions_gemini(prompt)
#         save_message(session_id, "bot", "\n".join(suggested_questions))
#     except Exception as e:
#         return JSONResponse({"error": f"LLM generation failed: {str(e)}"}, status_code=500)

#     return {
#         "questions": suggested_questions,
#         "session_id": session_id  # ✅ return for reuse
#     }

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
#         logger.info(f"Cleaned up collection for session {session_id}")
#         return JSONResponse({"status": "collection deleted"})
#     except Exception as e:
#         logger.error(f"Cleanup failed: {str(e)}")
#         return JSONResponse({"error": str(e)}, status_code=500)
