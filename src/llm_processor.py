"""
llm_processor.py -- LLM configuration and factory.

Returns a configured LLM instance for use in AgentSession.
Model: Groq llama-3.3-70b-versatile (OpenAI-compatible API).
"""
import os
import logging
from livekit.plugins import openai

logger = logging.getLogger(__name__)

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_llm(model: str = _DEFAULT_MODEL) -> openai.LLM:
    """
    Return a Groq LLM instance via the OpenAI-compatible API.

    Args:
        model: Groq model name. Defaults to llama-3.3-70b-versatile.

    Returns:
        Configured openai.LLM instance pointed at Groq's endpoint.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in environment")

    logger.debug("[LLM] Using model=%s via Groq", model)
    return openai.LLM(
        model=model,
        base_url=_GROQ_BASE_URL,
        api_key=api_key,
    )
