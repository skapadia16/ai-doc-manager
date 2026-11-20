# =====================================================
# rag/guardrails.py — RAG Safety & Security Guardrails
# =====================================================
#
# Guardrails kya karte hain?
# 1. Input Guardrails (User ke sawaal par):
#    - Prompt Injection & Jailbreak attack rokna
#    - Malicious code / SQL injection rokna
#    - PII (Credit card, phone, API keys) redact karna
#    - Input length limit check karna
#
# 2. Output Guardrails (AI ke jawab par):
#    - System prompt ya secret leakage rokna
#    - Factual grounding check (Hallucination prevention)
#    - Safe standard refusal maintain karna
# =====================================================

import re
from typing import Tuple, List, Dict

# Known Prompt Injection / Jailbreak Attack Patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) (instructions|prompts|rules)",
    r"you are now (dan|unrestricted|godmode|jailbroken)",
    r"bypass (all )?(guardrails|safety|filters)",
    r"system override",
    r"reveal (your )?(system prompt|instructions|secret key)",
    r"act as an evil|act as a hacker",
    r"drop (table|database)",
    r"delete from users",
    r"<script\b[^>]*>",
]

# Sensitive Information (PII) Regular Expressions
PII_PATTERNS = [
    # 16-digit Credit Card Numbers
    (r"\b(?:\d{4}[ -]?){3}\d{4}\b", "[REDACTED_CARD]"),
    # Standard SSN / National ID formats
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    (r"\b\d{4}\s\d{4}\s\d{4}\b", "[REDACTED_AADHAAR]"),
    # API Keys / Tokens (hf_..., sk-..., etc.)
    (r"\b(hf_[a-zA-Z0-9]{30,}|sk-[a-zA-Z0-9]{20,})\b", "[REDACTED_API_KEY]"),
]

# Secret Leakage Keywords that should never appear in user output
LEAKAGE_KEYWORDS = [
    "system prompt",
    "developer mode",
    "secret_key",
    "hf_token",
    "password_hash",
]

# =====================================================
# 1. INPUT GUARDRAIL
# =====================================================

def validate_input(query: str) -> Tuple[bool, str, str]:
    """
    User query ko sanitize aur validate karo.
    
    Returns:
    - is_valid (bool): Kya query safe hai?
    - sanitized_query (str): Cleaned query (with PII redacted)
    - reason (str): Agar reject hui toh wajah
    """
    if not query or not query.strip():
        return False, "", "Empty query is not allowed."

    cleaned_query = query.strip()

    # 1. Input Length Guardrail (min 2, max 2000 chars)
    if len(cleaned_query) < 2:
        return False, "", "Query is too short."
    if len(cleaned_query) > 2000:
        return False, "", "Query exceeds maximum allowed length of 2000 characters."

    # 2. Prompt Injection / Jailbreak Check
    query_lower = cleaned_query.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            print(f"[Guardrail Block] Prompt injection attempt detected: '{pattern}' in '{query}'")
            return (
                False,
                "",
                "Security Alert: Your request was flagged as potential prompt injection or unauthorized instruction override."
            )

    # 3. PII Redaction Guardrail
    sanitized = cleaned_query
    for pii_regex, replacement in PII_PATTERNS:
        sanitized = re.sub(pii_regex, replacement, sanitized)

    return True, sanitized, "Passed"


# =====================================================
# 2. OUTPUT GUARDRAIL
# =====================================================

def validate_output(answer: str, context_chunks: List[Dict]) -> Tuple[str, bool]:
    """
    AI model ke answer ko inspect karo pehle frontend ko bhejne se.
    
    Returns:
    - safe_answer (str): Screen par dikhane layak safe answer
    - is_safe (bool): Grounded & safe status
    """
    if not answer or not answer.strip():
        return "I could not find this information in the uploaded documents.", False

    ans_lower = answer.lower()

    # 1. System Prompt & Secret Leakage Check
    for leak_word in LEAKAGE_KEYWORDS:
        if leak_word in ans_lower:
            print(f"[Guardrail Block] Potential system secret leakage detected: '{leak_word}'")
            return "I could not find this information in the uploaded documents.", False

    # 2. Refusal Standardization
    if any(phrase in ans_lower for phrase in [
        "cannot find",
        "could not find",
        "not mentioned",
        "not found in the document",
        "no information provided"
    ]):
        # Keep standard refusal format
        return "I could not find this information in the uploaded documents.", True

    # 3. Factual Grounding (Keyword Check against retrieved chunks)
    # Agar document chunks the, check karein ki answer context se match karta hai
    if context_chunks:
        context_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', " ".join([c.get("text", "") for c in context_chunks]).lower()))
        answer_words = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', answer.lower()))

        # Common stop words exclude karo
        common_stops = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "been", "have", "has"}
        answer_words = answer_words - common_stops

        if answer_words:
            overlap = context_words.intersection(answer_words)
            overlap_ratio = len(overlap) / len(answer_words)
            # Agar answer ka 15% se bhi kam words context se aate hain aur lamba answer hai
            if overlap_ratio < 0.15 and len(answer.split()) > 25:
                print(f"[Guardrail Warning] Low context overlap ratio ({overlap_ratio:.2f}). Possible hallucination.")

    return answer.strip(), True
