"""
RAG (Retrieval-Augmented Generation) utility for EcoFlow AI.

Manages a JSON-based vector store for government policy documents.
Uses HuggingFace Inference API (BAAI/bge-small-en-v1.5) for embeddings
and cosine similarity for semantic search.
"""

import json
import os
from pathlib import Path
from typing import List, TypedDict

import numpy as np
from huggingface_hub import InferenceClient

# The vector store lives alongside the Next.js project root (one level up from backend/)
DB_PATH = Path(__file__).resolve().parent.parent / "policy_db.json"


class PolicyChunk(TypedDict):
    id: str
    text: str
    source: str
    vector: List[float]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks of roughly `chunk_size` characters."""
    chunks: List[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        i += chunk_size - overlap
    return chunks


_embedding_model = None

def _get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using local sentence-transformers."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    embeddings = _embedding_model.encode(texts)
    return embeddings.tolist()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def ingest_document(text: str, filename: str) -> int:
    """
    Process a document: split into chunks, embed, and save to the JSON vector DB.
    Returns the number of chunks created.
    """
    string_chunks = split_text_into_chunks(text, 500, 50)

    print(f"Generating embeddings for {len(string_chunks)} chunks...")
    embeddings = _get_embeddings(string_chunks)

    import time

    new_records: List[PolicyChunk] = []
    for i, chunk_text in enumerate(string_chunks):
        new_records.append(
            PolicyChunk(
                id=f"{filename}_{i}_{int(time.time() * 1000)}",
                text=chunk_text,
                source=filename,
                vector=embeddings[i],
            )
        )

    # Load existing DB
    existing_db: List[PolicyChunk] = []
    if DB_PATH.exists():
        with open(DB_PATH, "r", encoding="utf-8") as f:
            existing_db = json.load(f)

    updated_db = existing_db + new_records
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_db, f, indent=2)

    return len(new_records)


async def semantic_search(query: str, top_k: int = 3) -> List[PolicyChunk]:
    """
    Perform semantic search on the JSON vector DB.
    Returns the top-K most relevant chunks.
    """
    if not DB_PATH.exists():
        return []

    # Generate embedding for the query with retry
    query_embedding: List[float] = []
    retries = 3
    while retries > 0:
        try:
            result = _get_embeddings([query])
            query_embedding = result[0]
            break
        except Exception as e:
            print(f"HF API Error during search. Retries left: {retries - 1} — {e}")
            retries -= 1
            if retries == 0:
                raise
            import asyncio
            await asyncio.sleep(1)

    # Load the DB
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db: List[PolicyChunk] = json.load(f)

    # Calculate similarity for each chunk
    scored = []
    for chunk in db:
        score = cosine_similarity(query_embedding, chunk["vector"])
        scored.append((chunk, score))

    # Sort by highest score and return top K
    scored.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, _ in scored[:top_k]]
