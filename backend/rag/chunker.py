# =====================================================
# rag/chunker.py — Text ko chote tukdon mein baantna
# =====================================================
#
# RAG Pipeline Step 3 & 4:
#
# Kyun chunking zaroori hai?
# LLM ek baar mein bahut lamba text nahi le sakta.
# Isliye hum document ko chote "chunks" mein todten hain.
# Phir sirf relevant chunks retrieve karte hain.
#
# Example:
# Original text: 10,000 words
# Chunk size: 1000 characters
# Overlap: 200 (taaki context na toote)
# Result: ~11 chunks
# =====================================================

from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,    # har chunk kitna bada hoga
    chunk_overlap: int = 200   # chunks ke beech overlap (context ke liye)
) -> List[str]:
    """
    Bada text lo, chote chunks mein baanto, list return karo.
    
    RecursiveCharacterTextSplitter pehle paragraph,
    phir sentence, phir word pe todta hai — smart splitting.
    """
    
    # Text clean karo pehle
    text = _clean_text(text)
    
    if not text.strip():
        return []  # empty text? kuch nahi karo
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # priority order mein toda karo
    )
    
    chunks = splitter.split_text(text)
    return chunks

def _clean_text(text: str) -> str:
    """Extra spaces aur blank lines hatao"""
    import re
    
    # Multiple spaces ko ek karo
    text = re.sub(r' +', ' ', text)
    
    # 3 se zyada newlines ko 2 karo
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
