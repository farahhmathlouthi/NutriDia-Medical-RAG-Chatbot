import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from ingestion.loader import load_pdf
from ingestion.chunker import chunk_documents
from vectorstore.chroma_store import vectorstore

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Load, chunk, embed, and store
        docs = load_pdf(file_path)
        chunks = chunk_documents(docs)
        vectorstore.add_documents(chunks)
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_ingested": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
