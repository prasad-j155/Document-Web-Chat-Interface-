# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException # ADDED: Form
from pydantic import BaseModel
from app.utils.cache import get_cached_response, set_cached_response
from app.services.document import process_file          # ADDED: Import for parsing
from app.services.retriever import store_chunks_in_db   # ADDED: Import for DB storage
import time
from app.services.llm import generate_rag_response
router = APIRouter()

# 1. Define the Expected Input Data
class ChatRequest(BaseModel):
    session_id: str
    query: str

# 2. Document Upload Endpoint (Updated with DB Storage)
@router.post("/upload")
async def upload_document(
    session_id: str = Form(...), # ADDED: We need the session_id to link the document to the right user
    file: UploadFile = File(...)
):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    
    try:
        # Read the file into memory
        file_bytes = await file.read()
        
        # Parse it and chunk the text
        chunks = process_file(file.filename, file_bytes)
        
        # ADDED: Store the chunks in ChromaDB linked to the session_id
        store_chunks_in_db(session_id, chunks)
        
        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks_saved": len(chunks), # Changed to reflect it was saved to DB
            "message": "File parsed, chunked, and embedded into Vector DB successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# 3. The Core Chat Endpoint
@router.post("/chat")
async def chat(request: ChatRequest):
    # Step 2: Cache Check 
    cached_result = get_cached_response(request.session_id, request.query)
    if cached_result:
        cached_result["cached"] = True
        return cached_result

    try:
        # Steps 3 & 4: Retrieve Data & Generate AI Answer (NO MORE MOCKING!)
        response_data = generate_rag_response(request.session_id, request.query)
        
        # Format the final dictionary
        final_response = {
            "answer": response_data["answer"],
            "source": response_data["source"],
            "cached": False
        }

        # Step 6: Store in Redis for next time
        set_cached_response(request.session_id, request.query, final_response)

        # Step 7: Return to user
        return final_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")