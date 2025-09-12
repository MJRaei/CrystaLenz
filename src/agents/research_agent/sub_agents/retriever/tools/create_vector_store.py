import os
import json
import pickle
import pathlib
from typing import List, Dict, Any

import numpy as np
import faiss
from dataclasses import dataclass
from openai import OpenAI
import dotenv

# Load API key
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Directories
EXTRACTED_DIR = "papers/extracted_texts"
VECTOR_STORE_DIR = "papers/vector_store"
INDEX_FILE = os.path.join(VECTOR_STORE_DIR, "papers.faiss")
CHUNKS_FILE = os.path.join(VECTOR_STORE_DIR, "papers.chunks")

# ---------- Data Structures ----------

@dataclass
class PaperChunk:
    text: str
    metadata: Dict[str, Any]

# ---------- Chunking ----------

def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks of max length `chunk_size` with `chunk_overlap`.
    Works on characters, not tokens (approximation).
    """
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        start = 0
        while start < len(para):
            end = min(start + chunk_size, len(para))
            part = para[start:end]
            chunks.append(part)
            if end == len(para):
                current = ""
                break
            start = max(end - chunk_overlap, start + 1)

    if current:
        chunks.append(current)

    # Optional: handle overlap post-pass
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped: List[str] = []
        for i, ch in enumerate(chunks):
            if i == 0:
                overlapped.append(ch)
                continue
            prev = overlapped[-1]
            prefix = prev[max(0, len(prev) - chunk_overlap):]
            merged = (prefix + "\n\n" + ch).strip()
            if len(merged) <= chunk_size + chunk_overlap:
                overlapped.append(merged)
            else:
                overlapped.append(ch)
        chunks = overlapped

    return chunks

# ---------- Embedding ----------

def _embed_texts_openai(
    texts: List[str],
    model: str = "text-embedding-3-small",
    batch_size: int = 64
) -> np.ndarray:
    client = OpenAI(api_key=OPENAI_API_KEY)
    vectors: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model=model, input=batch)
        vectors.extend([d.embedding for d in resp.data])

    arr = np.array(vectors, dtype=np.float32)
    # Normalize embeddings for cosine similarity
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    arr = arr / norms
    return arr

# ---------- Main Tool ----------

def create_vector_store() -> Dict[str, Any]:
    """
    Build a FAISS vector index from extracted text files.

    Returns:
        dict: { status, files_indexed, chunks, index_paths }
    """
    print(">>> Creating vector store...")
    extracted_dir = EXTRACTED_DIR
    vector_store_dir = VECTOR_STORE_DIR
    chunk_size = 1200
    chunk_overlap = 200
    embedding_model = "text-embedding-3-large"
    os.makedirs(vector_store_dir, exist_ok=True)

    txt_files = [f for f in os.listdir(extracted_dir) if f.endswith(".txt")]
    if not txt_files:
        return {"status": "error", "message": "No .txt files found.", "files_indexed": 0, "chunks": 0}

    docs_texts: List[str] = []
    docs_metas: List[Dict[str, Any]] = []

    for fname in sorted(txt_files):
        path = os.path.join(extracted_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        # Expect first line to contain [SOURCE_PDF_PATH]
        lines = raw.split("\n", 1)
        if len(lines) < 2 or not lines[0].startswith("[SOURCE_PDF_PATH]:"):
            continue

        source_path = lines[0].replace("[SOURCE_PDF_PATH]:", "").strip()
        content = lines[1]

        chunks = _split_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for idx, chunk in enumerate(chunks):
            docs_texts.append(chunk)
            docs_metas.append({
                "source_file": fname,
                "source_path": source_path,
                "chunk_index": idx,
                "chunk_size": len(chunk),
            })

    if not docs_texts:
        return {"status": "error", "message": "No content to index.", "files_indexed": len(txt_files), "chunks": 0}

    embeddings = _embed_texts_openai(docs_texts, model=embedding_model)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_base = os.path.join(vector_store_dir, "papers")
    faiss_path = index_base + ".faiss"
    chunks_path = index_base + ".chunks"

    faiss.write_index(index, faiss_path)

    paper_chunks: List[PaperChunk] = [PaperChunk(text=t, metadata=m) for t, m in zip(docs_texts, docs_metas)]
    with open(chunks_path, "wb") as f:
        pickle.dump(paper_chunks, f, protocol=pickle.HIGHEST_PROTOCOL)

    return {
        "status": "ok",
        "files_indexed": len(txt_files),
        "chunks": len(docs_texts),
        "index_paths": {"faiss": faiss_path, "chunks": chunks_path}
    }

def check_vector_store() -> Dict[str, Any]:
    """
    Check whether the vector store exists (FAISS index and chunks file).

    Returns:
        dict: {
            "status": "ok" if both files exist else "error",
            "index_paths": {"faiss": <path or None>, "chunks": <path or None>}
        }
    """
    print(">>> Checking vector store...")
    faiss_exists = os.path.exists(INDEX_FILE)
    chunks_exists = os.path.exists(CHUNKS_FILE)

    if faiss_exists and chunks_exists:
        return {
            "status": "ok",
            "index_paths": {
                "faiss": INDEX_FILE,
                "chunks": CHUNKS_FILE
            }
        }
    else:
        return {
            "status": "error",
            "index_paths": {
                "faiss": INDEX_FILE if faiss_exists else None,
                "chunks": CHUNKS_FILE if chunks_exists else None
            }
        }

# if __name__ == "__main__":
#     print(">>> Building vector store from extracted texts...")
#     result = create_vector_store()
#     print(">>> Done.")
#     print(json.dumps(result, indent=2))
