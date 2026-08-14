"""
POST /api/upload-policy

Accepts a PDF file upload, extracts text with pdfplumber,
and ingests it into the JSON vector store via RAG.
"""

import io

import pdfplumber
from fastapi import APIRouter, File, HTTPException, UploadFile

from rag import ingest_document

router = APIRouter()


@router.post("/api/upload-policy")
async def upload_policy(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        contents = await file.read()

        # Extract text from PDF using pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise HTTPException(
                status_code=400, detail="Could not extract text from PDF"
            )

        # Call our RAG utility to split, embed, and save
        chunks_count = await ingest_document(text, file.filename)

        return {
            "success": True,
            "message": f"Successfully ingested document! Created {chunks_count} vectorized chunks.",
            "chunks": chunks_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload Policy Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}",
        )
