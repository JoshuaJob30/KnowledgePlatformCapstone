# app/services/vector_service.py
import faiss, numpy as np
from sentence_transformers import SentenceTransformer
from app.core.logging import logger
from functools import lru_cache

# Globals
vector_model = None
faiss_index = None
documents = []

def init_vector_store():
    """Initialize model and FAISS index once."""
    global vector_model, faiss_index
    if vector_model is None or faiss_index is None:
        try:
            vector_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            dimension = vector_model.get_sentence_embedding_dimension()
            faiss_index = faiss.IndexFlatL2(dimension)
            logger.info("Vector model and FAISS index initialized.")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

def add_document(chunks: list[str], filename: str):
    """Add document chunks to FAISS index with metadata."""
    init_vector_store()
    try:
        embeddings = vector_model.encode(chunks)
        faiss_index.add(np.array(embeddings, dtype="float32"))
        for i, chunk in enumerate(chunks):
            documents.append({
                "filename": filename,
                "chunk_index": i,
                "text": chunk
            })
        logger.info(f"Added {len(chunks)} chunks from {filename} to vector store.")
    except Exception as e:
        logger.error(f"Error adding document {filename}: {e}")
        raise

def search_documents(query: str, k: int = 5, hybrid: bool = True):
    """Search FAISS index and optionally combine with keyword search."""
    init_vector_store()
    if not documents:
        logger.warning("Vector store is empty. No documents to search.")
        return []

    results = []

    # Vector search
    try:
        embedding = vector_model.encode([query])
        D, I = faiss_index.search(np.array(embedding, dtype="float32"), k)
        for i in I[0]:
            if i < len(documents):
                results.append(documents[i])
    except Exception as e:
        logger.error(f"Error in vector search: {e}")

    # Keyword search (hybrid mode)
    if hybrid:
        keyword_hits = [doc for doc in documents if query.lower() in doc["text"].lower()]
        results.extend(keyword_hits)

    # Deduplicate results
    seen = set()
    unique_results = []
    for r in results:
        key = (r["filename"], r["chunk_index"])
        if key not in seen:
            unique_results.append(r)
            seen.add(key)

    logger.info(f"Hybrid search for '{query}' returned {len(unique_results)} results.")
    return unique_results[:k]

@lru_cache(maxsize=128)
def cached_search(query: str, k: int = 5):
    """
    Cached wrapper around search_documents.
    Stores up to 128 unique queries in memory.
    """
    return search_documents(query, k, hybrid=True)
