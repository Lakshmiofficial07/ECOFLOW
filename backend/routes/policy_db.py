"""
GET /api/policy-db    — List documents in the vector store
DELETE /api/policy-db — Clear the entire vector store
DELETE /api/policy-db/{filename} — Delete a specific document from the vector store
"""

import json
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter

from rag import DB_PATH

router = APIRouter()


@router.get("/api/policy-db")
async def get_policy_db():
    try:
        if not DB_PATH.exists():
            return {"documents": []}

        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

        # Group by source (filename)
        docs_map: dict[str, int] = defaultdict(int)
        for chunk in db:
            docs_map[chunk["source"]] += 1

        documents = [
            {"filename": filename, "chunkCount": count}
            for filename, count in docs_map.items()
        ]

        return {"documents": documents}

    except Exception as e:
        return {"error": str(e)}


@router.delete("/api/policy-db")
async def delete_policy_db():
    try:
        if DB_PATH.exists():
            DB_PATH.unlink()
        return {"success": True, "message": "Knowledge base cleared"}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/api/policy-db/{filename}")
async def delete_single_policy(filename: str):
    try:
        if not DB_PATH.exists():
            return {"success": True, "message": "Knowledge base is already empty"}

        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

        original_count = len(db)
        # Keep only chunks whose source is not the requested filename
        updated_db = [chunk for chunk in db if chunk.get("source") != filename]

        if len(updated_db) == original_count:
            return {"error": "Document not found"}

        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, indent=2)

        return {"success": True, "message": f"Document '{filename}' deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
