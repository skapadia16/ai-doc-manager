# =====================================================
# rag/vector_store.py — FAISS Vector Database
# =====================================================
#
# RAG Pipeline Step 6 & 7:
#
# FAISS kya karta hai?
# Lakho vectors mein se sabse similar vector dhundta hai — milliseconds mein!
# (Facebook ka open-source library)
#
# Hum store karte hain:
# - Document chunks ke vectors (FAISS index)
# - Metadata: document_id, chunk_index, text (Python list)
#
# Structure:
# vector_db/
#   faiss.index      ← vectors
#   metadata.pkl     ← corresponding metadata
# =====================================================

import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Optional

class VectorStore:
    """Simple FAISS wrapper — samajhna aasan hai"""
    
    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        self.index_path = os.path.join(db_dir, "faiss.index")
        self.meta_path  = os.path.join(db_dir, "metadata.pkl")
        
        # In-memory data
        self.index: Optional[faiss.IndexFlatIP] = None  # vectors
        self.metadata: List[Dict] = []                  # text + doc info
        
        # Existing data load karo (agar hai toh)
        self._load()
    
    def _load(self):
        """Disk se load karo (restart ke baad bhi data rahe)"""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"Vector store loaded: {len(self.metadata)} chunks")
        else:
            # Naya index banao (384 = MiniLM embedding size)
            self.index = faiss.IndexFlatIP(384)  # Inner Product = cosine similarity
            self.metadata = []
    
    def _save(self):
        """Memory se disk par save karo"""
        os.makedirs(self.db_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
    
    def get_candidate_chunks(self, allowed_doc_ids: Optional[List[int]] = None) -> List[Dict]:
        """Return all metadata chunks for allowed document IDs (for BM25 / Hybrid search)"""
        if allowed_doc_ids is None:
            return self.metadata
        allowed_set = set(allowed_doc_ids)
        return [c for c in self.metadata if c.get("document_id") in allowed_set]

    def add_chunks(self, embeddings: np.ndarray, chunks_info: List[Dict]):
        """
        Chunks aur unke vectors store karo.
        
        chunks_info example:
        [{"document_id": 1, "chunk_index": 0, "text": "...", "doc_name": "report.pdf"}]
        """
        # Vectors normalize karo (cosine similarity ke liye)
        faiss.normalize_L2(embeddings)
        
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(chunks_info)
        self._save()
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        allowed_doc_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Sawaal ka vector leke sabse relevant chunks dhundo.
        
        allowed_doc_ids: Sirf in documents mein se dhundo (permission filter)
        Returns: List of chunks with their content and scores
        """
        if self.index.ntotal == 0:
            return []  # koi data nahi
        
        # Query normalize karo
        query = query_vector.reshape(1, -1).astype("float32")
        faiss.normalize_L2(query)
        
        # Zyada results lo, phir filter karenge
        search_k = min(top_k * 10, self.index.ntotal)
        scores, indices = self.index.search(query, search_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            
            chunk = self.metadata[idx].copy()
            chunk["score"] = float(score)
            
            # Permission check: sirf allowed documents return karo
            if allowed_doc_ids is not None:
                if chunk["document_id"] not in allowed_doc_ids:
                    continue  # skip karo, permission nahi hai
            
            results.append(chunk)
            
            if len(results) >= top_k:
                break  # kaafi results mil gaye
        
        return results
    
    def delete_document_chunks(self, document_id: int):
        """
        Ek document ke saare chunks hatao.
        FAISS deletion support nahi karta seedha,
        isliye rebuild karte hain without that document.
        """
        # Remaining chunks nikalo
        remaining = [m for m in self.metadata if m["document_id"] != document_id]
        
        if not remaining:
            # Sab kuch khali
            self.index = faiss.IndexFlatIP(384)
            self.metadata = []
        else:
            # Naya index banao sirf remaining ke saath
            # (Embeddings dobara compute nahi karte, store karte hain)
            # NOTE: Simple approach — production mein FAISS IDMap use karo
            self.metadata = remaining
            # Index rebuild zaroor hoga (yahan skip, document service handle karegi)
        
        self._save()

# Global instance — ek hi baar banao
_store: Optional[VectorStore] = None

def get_vector_store(db_dir: str = "vector_db") -> VectorStore:
    """Global VectorStore instance lo"""
    global _store
    if _store is None:
        _store = VectorStore(db_dir)
    return _store
