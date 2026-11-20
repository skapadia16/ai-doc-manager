# =====================================================
# rag/hybrid_search.py — Hybrid Search (Dense + Sparse)
# =====================================================
#
# Hybrid Search kya hai?
# 1. Dense Search (FAISS Vectors):
#    - Meaning, synonyms aur semantics samajhta hai.
#    - Example: "car" search karne par "automobile" bhi milta hai.
#
# 2. Sparse Search (BM25 Keyword Matching):
#    - Exact keywords, IDs, codes aur technical terms dhoondta hai.
#    - Example: "Section 4B", "Invoice-2024", "GSTIN" etc.
#
# 3. Reciprocal Rank Fusion (RRF):
#    - Dono ke ranks ko combine karta hai:
#      RRF_Score = (Weight_Dense / (60 + Rank_Dense)) + (Weight_Sparse / (60 + Rank_Sparse))
#    - Best of both worlds!
# =====================================================

import re
import math
from typing import List, Dict, Any, Optional

def tokenize(text: str) -> List[str]:
    """Simple clean word tokenizer (lowercase, alphanumeric words)"""
    return re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())

class BM25Okapi:
    """
    Lightweight, pure-Python BM25 implementation (0 external dependencies).
    Standard parameters: k1 = 1.5 (term saturation), b = 0.75 (length normalization).
    """
    def __init__(self, corpus_texts: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus_texts)
        self.avgdl = 0.0
        self.doc_lengths = []
        self.doc_freqs = []  # term frequencies per document
        self.idf = {}        # inverse document frequency

        if self.corpus_size > 0:
            total_len = 0
            df_counts = {}
            for doc in corpus_texts:
                tokens = tokenize(doc)
                doc_len = len(tokens)
                total_len += doc_len
                self.doc_lengths.append(doc_len)

                # Count term frequencies in this doc
                tf = {}
                for t in tokens:
                    tf[t] = tf.get(t, 0) + 1
                self.doc_freqs.append(tf)

                # Track document frequency for IDF
                for t in tf.keys():
                    df_counts[t] = df_counts.get(t, 0) + 1

            self.avgdl = total_len / self.corpus_size

            # Compute Robertson-Spärck Jones IDF
            for term, df in df_counts.items():
                self.idf[term] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

    def get_scores(self, query: str) -> List[float]:
        """Query ke against har document ka BM25 score nikalo"""
        if self.corpus_size == 0 or self.avgdl == 0:
            return []

        query_tokens = tokenize(query)
        scores = [0.0] * self.corpus_size

        for term in query_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]

            for idx in range(self.corpus_size):
                tf = self.doc_freqs[idx].get(term, 0)
                if tf > 0:
                    doc_len = self.doc_lengths[idx]
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                    scores[idx] += idf_val * (numerator / denominator)

        return scores


def hybrid_search(
    query: str,
    dense_results: List[Dict[str, Any]],
    candidate_chunks: List[Dict[str, Any]],
    top_k: int = 5,
    dense_weight: float = 1.0,
    sparse_weight: float = 1.0,
    rrf_k: int = 60
) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion (RRF) se Dense (Vector) aur Sparse (BM25) ko combine karo.
    
    Parameters:
    - query: User ka sawaal
    - dense_results: FAISS se mile top vector chunks (scores ke sath)
    - candidate_chunks: Accessible chunks jinme keyword search chalegi
    - top_k: Final kitne chunks return karne hain
    - dense_weight: Vector search weight (e.g. 0.6)
    - sparse_weight: Keyword search weight (e.g. 0.4)
    """
    if not candidate_chunks:
        return dense_results[:top_k]

    # Step 1: BM25 Sparse Search run karo
    corpus_texts = [c.get("text", "") for c in candidate_chunks]
    bm25 = BM25Okapi(corpus_texts)
    bm25_scores = bm25.get_scores(query)

    # BM25 results sort karo (highest score first)
    indexed_sparse = list(enumerate(bm25_scores))
    indexed_sparse.sort(key=lambda x: x[1], reverse=True)

    # Step 2: Dense Ranks map karo
    # chunk key identify karne ke liye (doc_id + chunk_index)
    def make_key(c: Dict) -> str:
        return f"{c.get('document_id', 0)}_{c.get('chunk_index', 0)}"

    dense_ranks = {}
    dense_map = {}
    for rank, c in enumerate(dense_results):
        k = make_key(c)
        dense_ranks[k] = rank + 1  # 1-based rank
        dense_map[k] = c

    # Step 3: Sparse Ranks map karo
    sparse_ranks = {}
    sparse_map = {}
    for rank, (idx, score) in enumerate(indexed_sparse):
        if score > 0:  # sirf woh jisme keyword match hua
            c = candidate_chunks[idx]
            k = make_key(c)
            sparse_ranks[k] = rank + 1
            sparse_map[k] = c

    # Step 4: RRF Fusion Score Compute Karo
    all_keys = set(dense_ranks.keys()).union(set(sparse_ranks.keys()))
    fusion_scores = []

    for k in all_keys:
        score = 0.0
        # Dense contribution
        if k in dense_ranks:
            score += dense_weight * (1.0 / (rrf_k + dense_ranks[k]))
        # Sparse contribution
        if k in sparse_ranks:
            score += sparse_weight * (1.0 / (rrf_k + sparse_ranks[k]))

        # Original chunk reference lo
        chunk_obj = dense_map.get(k) or sparse_map.get(k)
        if chunk_obj:
            item = chunk_obj.copy()
            item["rrf_score"] = score
            item["matched_dense"] = k in dense_ranks
            item["matched_sparse"] = k in sparse_ranks
            fusion_scores.append(item)

    # Step 5: Sort by RRF score descending
    fusion_scores.sort(key=lambda x: x["rrf_score"], reverse=True)

    # Agar koi results na bane, toh original dense fallback
    if not fusion_scores:
        return dense_results[:top_k]

    return fusion_scores[:top_k]
