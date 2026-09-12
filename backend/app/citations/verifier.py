"""Guardrail layer: verify that everything the LLM cited actually exists in, and is actually
supported by, the evidence it was given. This is what stops a hallucinated citation or an
invented quote from ever reaching the user — the LLM's output is treated as a claim, not as
ground truth, until it passes this check.
"""
import difflib
import re
from dataclasses import dataclass


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


@dataclass
class VerificationResult:
    citation_exists: bool
    quote_supported: bool
    similarity: float


def verify_citation(citation: str, quote: str, known_chunks: dict[str, str]) -> VerificationResult:
    """known_chunks maps citation_id -> full chunk text."""
    if citation not in known_chunks:
        return VerificationResult(citation_exists=False, quote_supported=False, similarity=0.0)

    chunk_text = _normalize(known_chunks[citation])
    quote_norm = _normalize(quote)

    if not quote_norm:
        return VerificationResult(citation_exists=True, quote_supported=False, similarity=0.0)

    if quote_norm in chunk_text:
        return VerificationResult(citation_exists=True, quote_supported=True, similarity=1.0)

    # Fuzzy fallback: find the best-matching window in the chunk text of similar length.
    matcher = difflib.SequenceMatcher(a=chunk_text, b=quote_norm, autojunk=False)
    match = matcher.find_longest_match(0, len(chunk_text), 0, len(quote_norm))
    coverage = match.size / max(len(quote_norm), 1)
    supported = coverage >= 0.7
    return VerificationResult(citation_exists=True, quote_supported=supported, similarity=coverage)
