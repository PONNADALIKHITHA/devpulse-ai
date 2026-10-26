"""Configuration Manager for DevPulse AI.

Reads secrets and environment variables safely according to the GMRIT project handbook:
1. Checks streamlit secrets (st.secrets) first (used on Streamlit Cloud & local secrets.toml).
2. Falls back to python-dotenv or os.environ for local terminal runs.
3. Provides graceful fallback to 'mock' mode if no API key is configured.
"""

import os
from typing import Optional

# Optional dotenv loading (pure standard library fallback if not installed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a setting from Streamlit secrets, environment variables, or default.
    
    Args:
        name: Configuration variable name.
        default: Fallback value if setting is not found.
        
    Returns:
        The configuration string or default.
    """
    # 1. Try Streamlit secrets
    if HAS_STREAMLIT:
        try:
            if hasattr(st, "secrets") and name in st.secrets:
                return str(st.secrets[name])
        except Exception:
            pass

    # 2. Try OS environment variables
    env_val = os.getenv(name)
    if env_val is not None and env_val.strip() != "":
        return env_val.strip()

    return default


def get_llm_provider() -> str:
    """Return the configured LLM provider ('gemini', 'groq', or 'mock')."""
    provider = (get_setting("LLM_PROVIDER") or "").lower()
    gemini_key = get_setting("GEMINI_API_KEY")
    groq_key = get_setting("GROQ_API_KEY")

    if provider == "groq" and groq_key:
        return "groq"
    if (provider == "gemini" or not provider) and gemini_key:
        return "gemini"
    if groq_key:
        return "groq"
    
    # If explicitly requested mock or no keys found:
    return "mock"


def get_model_name() -> str:
    """Return model identifier based on current provider."""
    provider = get_llm_provider()
    custom_model = get_setting("MODEL_NAME")
    if custom_model:
        return custom_model

    if provider == "groq":
        return "llama-3.3-70b-versatile"
    elif provider == "gemini":
        return "gemini-1.5-flash"
    return "devpulse-mock-engine"


def is_live_mode() -> bool:
    """Check if a live API key is configured."""
    return get_llm_provider() in ("gemini", "groq")
