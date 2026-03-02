"""LLM configuration with retry logic for Groq free-tier rate limits."""

import os
import time
import logging

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

MODEL_NAME = "qwen/qwen3-32b"
MAX_RETRIES = 5
BASE_DELAY = 10  # seconds — Groq free tier typically asks for ~8s


# ──────────────────────────────────────────────
# LLM factory
# ──────────────────────────────────────────────


def get_llm() -> ChatGroq:
    """Return a ChatGroq instance with the API key loaded from .env."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")
    return ChatGroq(model=MODEL_NAME, api_key=api_key)


# ──────────────────────────────────────────────
# Retry wrapper
# ──────────────────────────────────────────────


def invoke_with_retry(llm, messages, *, structured_output=None, max_retries=MAX_RETRIES):
    """
    Invoke the LLM with automatic retry on 429 rate-limit errors.
    Uses exponential backoff starting at BASE_DELAY seconds.

    Parameters
    ----------
    llm : ChatGroq
        The LLM instance.
    messages : list
        Messages to send.
    structured_output : type | None
        If provided, use `llm.with_structured_output(...)` before invoking.
    max_retries : int
        Maximum number of retry attempts.

    Returns
    -------
    The LLM response.
    """
    chain = llm.with_structured_output(structured_output) if structured_output else llm

    for attempt in range(1, max_retries + 1):
        try:
            return chain.invoke(messages)
        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()

            if is_rate_limit and attempt < max_retries:
                delay = BASE_DELAY * attempt  # linear backoff: 10s, 20s, 30s ...
                logger.warning(
                    f"Rate limit hit (attempt {attempt}/{max_retries}). "
                    f"Waiting {delay}s before retry..."
                )
                time.sleep(delay)
            else:
                raise
