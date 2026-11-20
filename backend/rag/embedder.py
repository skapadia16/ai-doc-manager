# =====================================================
# rag/embedder.py — Text ko numbers (vectors) mein badalna
# =====================================================
#
# RAG Pipeline Step 5:
#
# Embedding kya hai?
# "Cat is an animal" → [0.23, -0.14, 0.87, ...]  (384 numbers)
# Similar meaning → similar numbers (close vectors)
#
# Isi liye search karte waqt:
# User ka sawaal → vector
# Document chunks → vectors
# Closest vectors = most relevant chunks
#
# Model: sentence-transformers/all-MiniLM-L6-v2 (free, fast, good)
# =====================================================

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Model ek baar load karo (costly operation)
# Baad mein sirf inference hogi (fast)
_model = None

def get_embedding_model() -> SentenceTransformer:
    """Model ko pehli baar load karo, baad mein cache karo"""
    global _model
    if _model is None:
        print("Loading embedding model (first time only)...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Embedding model loaded!")
    return _model

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Texts ki list lo → numpy array of vectors return karo
    Shape: (len(texts), 384)
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings

def embed_single(text: str) -> np.ndarray:
    """Ek text embed karo (user question ke liye)"""
    model = get_embedding_model()
    embedding = model.encode([text], convert_to_numpy=True)
    return embedding[0]  # 1D array return karo
