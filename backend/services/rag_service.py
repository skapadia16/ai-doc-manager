# =====================================================
# services/rag_service.py — Hybrid RAG & Guardrails
# =====================================================
#
# Pipeline Architecture:
# 1. Input Guardrails: Prompt injection & PII sanitize
# 2. Hybrid Search:
#    - Dense Semantic Search (FAISS + MiniLM Embeddings)
#    - Sparse Lexical Search (BM25 Keyword Matching)
#    - Reciprocal Rank Fusion (RRF) combining both
# 3. LLM Generation: Hugging Face model
# 4. Output Guardrails: Hallucination check & secret leak prevention
# 5. Free Web Fallback: If not in docs, live DuckDuckGo search
# =====================================================

from sqlalchemy.orm import Session
from typing import List, Dict

from models.user import User, GroupMember, UserRole
from models.document import DocumentPermission, Document
from rag.embedder import embed_single
from rag.vector_store import get_vector_store
from rag.hybrid_search import hybrid_search
from rag.guardrails import validate_input, validate_output
from rag.llm import ask_llm
from config import settings

def free_web_search(query: str, max_results: int = 3) -> List[Dict]:
    """100% Free Web Search via ddgs (DuckDuckGo engine)"""
    try:
        from ddgs import DDGS
        results = list(DDGS().text(query, max_results=max_results))
        return results
    except Exception as e:
        print(f"Free web search warning: {e}")
        return []

def get_user_allowed_doc_ids(user: User, db: Session) -> List[int]:
    """Admin -> all documents; Normal user -> authorized documents only"""
    if user.role == UserRole.admin:
        all_docs = db.query(Document.id).all()
        return [doc.id for doc in all_docs]

    user_group_ids = [
        gm.group_id 
        for gm in db.query(GroupMember).filter(GroupMember.user_id == user.id).all()
    ]

    permissions = db.query(DocumentPermission).filter(
        (DocumentPermission.user_id == user.id) |
        (DocumentPermission.group_id.in_(user_group_ids) if user_group_ids else False)
    ).all()

    allowed_ids = list(set(p.document_id for p in permissions))
    return allowed_ids

def answer_question(question: str, user: User, db: Session) -> Dict:
    """
    Main RAG function with Input Guardrails, Hybrid Search (Dense+BM25),
    Output Guardrails, and Free Web Fallback.
    """
    # =====================================================
    # STEP 1: INPUT GUARDRAIL (Prompt injection & PII Check)
    # =====================================================
    is_valid, sanitized_question, rejection_reason = validate_input(question)
    if not is_valid:
        print(f"[Guardrails] Query blocked: {rejection_reason}")
        return {
            "answer": f"🛡️ **Guardrail Alert**: {rejection_reason}",
            "sources": []
        }

    allowed_doc_ids = get_user_allowed_doc_ids(user, db)
    hybrid_chunks = []

    if allowed_doc_ids:
        # =====================================================
        # STEP 2: DENSE VECTOR SEARCH (FAISS)
        # =====================================================
        question_vector = embed_single(sanitized_question)
        vector_store = get_vector_store(settings.VECTOR_DB_DIR)

        # Top 10 dense candidates
        dense_results = vector_store.search(
            query_vector=question_vector,
            top_k=10,
            allowed_doc_ids=allowed_doc_ids
        )

        # =====================================================
        # STEP 3: HYBRID SEARCH (Dense + Sparse BM25 with RRF)
        # =====================================================
        candidate_chunks = vector_store.get_candidate_chunks(allowed_doc_ids)

        hybrid_chunks = hybrid_search(
            query=sanitized_question,
            dense_results=dense_results,
            candidate_chunks=candidate_chunks,
            top_k=5,
            dense_weight=1.0,
            sparse_weight=1.0
        )

    # =====================================================
    # STEP 4: LLM GENERATION (From Hybrid Chunks)
    # =====================================================
    raw_answer = ask_llm(sanitized_question, hybrid_chunks)

    # =====================================================
    # STEP 5: OUTPUT GUARDRAIL (Grounding & Safety Check)
    # =====================================================
    safe_answer, is_grounded = validate_output(raw_answer, hybrid_chunks)

    # Check if answer was not found in uploaded documents
    not_found = (
        not hybrid_chunks
        or "could not find this information in the uploaded documents" in safe_answer.lower()
    )

    # =====================================================
    # STEP 6: AUTOMATED FREE WEB SEARCH FALLBACK
    # =====================================================
    if not_found:
        print(f"[Hybrid RAG] Not in documents. Searching Web for: '{sanitized_question}'...")
        web_results = free_web_search(sanitized_question, max_results=3)

        if web_results:
            web_chunks = [
                {
                    "doc_name": r.get("title", "Web Source"),
                    "text": r.get("body", ""),
                    "score": 0.95
                }
                for r in web_results
            ]

            raw_web_ans = ask_llm(sanitized_question, web_chunks)
            safe_web_ans, _ = validate_output(raw_web_ans, web_chunks)
            snippet = web_results[0].get("body", "").strip()

            formatted_answer = f"🌐 **Found via Web Search** *(Not present in uploaded documents)*:\n\n{safe_web_ans}"
            if snippet and len(snippet) > len(safe_web_ans):
                formatted_answer += f"\n\n> {snippet}"

            web_sources = [
                {
                    "document_name": f"🌐 {r.get('title', 'Web Result')}",
                    "chunk_index": i + 1
                }
                for i, r in enumerate(web_results)
            ]

            return {
                "answer": formatted_answer,
                "sources": web_sources
            }

        return {
            "answer": "I could not find this information in the uploaded documents or on the web.",
            "sources": []
        }

    # Step 7: Document se answer mila -> Return grounded answer + sources
    sources = [
        {
            "document_name": chunk.get("doc_name", "Unknown"),
            "chunk_index": chunk.get("chunk_index", 0)
        }
        for chunk in hybrid_chunks
    ]

    return {
        "answer": safe_answer,
        "sources": sources
    }
