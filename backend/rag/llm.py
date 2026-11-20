# =====================================================
# rag/llm.py — Hugging Face LLM se jawab lena
# =====================================================
#
# RAG Pipeline Step 8:
# 1. Retrieved chunks se context banate hain.
# 2. Pehle Hugging Face Cloud Router se try karta hai.
# 3. Agar cloud down/offline/rate-limited ho, toh local
#    Hugging Face model (google/flan-t5-base) se jawab
#    generate karta hai — 100% free, 0 failure!
# =====================================================

import os
import requests
from typing import List, Dict
from config import settings

# Local Hugging Face pipeline (first time load, then cached in memory)
_local_generator = None

def get_local_generator():
    """Local Hugging Face model load karo (free, offline, reliable)"""
    global _local_generator
    if _local_generator is None:
        try:
            from transformers import pipeline
            print("Loading local Hugging Face model (google/flan-t5-base)...")
            _local_generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                device="cpu"
            )
            print("Local Hugging Face model ready!")
        except Exception as e:
            print(f"Could not load local model: {e}")
            _local_generator = None
    return _local_generator

def generate_local_answer(question: str, context_chunks: List[Dict]) -> str:
    """Local model se answer generate karo"""
    generator = get_local_generator()
    if not generator:
        # Fallback: Top relevant context directly return karo
        top_text = context_chunks[0].get("text", "").strip() if context_chunks else ""
        return top_text[:600] if top_text else "I could not find this information in the uploaded documents."

    # Top chunks ka context prepare karo
    context_text = "\n".join([c.get("text", "") for c in context_chunks[:3]])
    context_text = context_text[:2000]  # keep within context window

    prompt = (
        f"Answer the question based only on the context below. "
        f"If the answer is not mentioned in the context, say 'I could not find this information in the uploaded documents.'\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    try:
        result = generator(prompt, max_new_tokens=256, do_sample=False)
        if result and len(result) > 0:
            ans = result[0].get("generated_text", "").strip()
            if ans and len(ans) > 1:
                return ans
    except Exception as e:
        print(f"Local generation error: {e}")

    # Fallback to most relevant chunk text
    top_chunk = context_chunks[0].get("text", "")
    return top_chunk[:400] + "..." if len(top_chunk) > 400 else top_chunk

def ask_llm(question: str, context_chunks: List[Dict]) -> str:
    """
    User question aur context leke jawab generate karo.
    1. Try Cloud Hugging Face Router
    2. Fallback to Local Hugging Face Model
    """
    if not context_chunks:
        return "I could not find this information in the uploaded documents."

    # Chunks quality check (agar score bahut low ho)
    top_score = context_chunks[0].get("score", 1.0)
    if top_score < 0.15:
        return "I could not find this information in the uploaded documents."

    # Try 1: Hugging Face Cloud Router (if configured and reachable)
    if settings.HF_TOKEN and not settings.HF_TOKEN.startswith("hf_your"):
        try:
            # New Hugging Face Router Chat Completions URL
            cloud_url = "https://router.huggingface.co/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {settings.HF_TOKEN}",
                "Content-Type": "application/json"
            }

            context_parts = []
            for i, chunk in enumerate(context_chunks[:4]):
                doc_name = chunk.get("doc_name", "Document")
                text = chunk.get("text", "")
                context_parts.append(f"[{doc_name}]:\n{text}")
            context_str = "\n\n".join(context_parts)

            prompt = (
                f"You are a helpful assistant. Answer the question based ONLY on the documents provided below.\n"
                f"If the information is not in the documents, respond: 'I could not find this information in the uploaded documents.'\n\n"
                f"--- DOCUMENTS ---\n{context_str}\n--- END ---\n\n"
                f"Question: {question}"
            )

            payload = {
                "model": settings.HF_MODEL or "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.2
            }

            resp = requests.post(cloud_url, headers=headers, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if content:
                    return content
        except Exception as e:
            print(f"Cloud HF router unavailable ({e}), using local Hugging Face model...")

    # Try 2: Local Hugging Face Model (always available, free, no rate limits)
    return generate_local_answer(question, context_chunks)
