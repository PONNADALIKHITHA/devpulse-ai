"""LLM Service for DevPulse AI.

Provides resilient integrations for Google Gemini (1.5 / 2.0 Flash) and Groq (LLaMA 3.3).
Compliant with the GMRIT handbook guidelines:
- Handles timeouts, rate limits, and network errors gracefully.
- Safely enforces JSON structured outputs.
- Never prints or logs secrets.
- Provides test connection verification for live demonstration.
"""

import json
import logging
import time
import requests
from typing import Dict, Any, Optional, Tuple

from backend.config import get_setting, get_llm_provider, get_model_name

logger = logging.getLogger("devpulse.llm_service")

# Request timeout in seconds
REQUEST_TIMEOUT = 25


def call_gemini(prompt: str, system_prompt: str, api_key: str, model: str) -> str:
    """Call Google Gemini Generative Language REST API with JSON response enforcement."""
    # Default to gemini-1.5-flash if not specified
    model_id = model if model and "gemini" in model else "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    full_instruction = f"{system_prompt}\n\nTask:\n{prompt}" if system_prompt else prompt

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_instruction}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3500,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as err:
            raise RuntimeError(f"Unexpected response structure from Gemini API: {err}")
    elif response.status_code == 429:
        raise RuntimeError("Gemini API rate limit reached (HTTP 429). Please wait a moment or switch to Local Static Analyzer.")
    elif response.status_code == 400:
        raise RuntimeError(f"Gemini API Bad Request (HTTP 400): {response.text}")
    elif response.status_code in (401, 403):
        raise RuntimeError("Gemini API key is invalid or lacks required permissions (HTTP 403).")
    else:
        raise RuntimeError(f"Gemini API returned status {response.status_code}: {response.text}")


def call_groq(prompt: str, system_prompt: str, api_key: str, model: str) -> str:
    """Call Groq API using OpenAI-compatible chat completions endpoint."""
    model_id = model if model and "llama" in model else "llama-3.3-70b-versatile"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 3000,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    elif response.status_code == 429:
        raise RuntimeError("Groq API rate limit reached. Please try again shortly or use Local Engine.")
    elif response.status_code in (401, 403):
        raise RuntimeError("Groq API key is invalid or unauthorized.")
    else:
        raise RuntimeError(f"Groq API error ({response.status_code}): {response.text}")


def test_api_connection(provider: str, api_key: str, model: Optional[str] = None) -> Tuple[bool, str]:
    """Verify live API connectivity and latency for viva demonstration."""
    if not api_key or "your_" in api_key.lower():
        return False, "No valid API key provided."

    start_time = time.time()
    try:
        prov = (provider or "").lower().strip()
        if prov == "gemini":
            mod = model or "gemini-1.5-flash"
            resp = call_gemini(
                prompt='Respond with JSON: {"status": "ok"}',
                system_prompt="Return strict JSON only.",
                api_key=api_key,
                model=mod
            )
            elapsed = time.time() - start_time
            return True, f"Connected to Google Gemini ({mod}) in {elapsed:.2f}s."
        elif prov == "groq":
            mod = model or "llama-3.3-70b-versatile"
            resp = call_groq(
                prompt='Respond with JSON: {"status": "ok"}',
                system_prompt="Return strict JSON only.",
                api_key=api_key,
                model=mod
            )
            elapsed = time.time() - start_time
            return True, f"Connected to Groq ({mod}) in {elapsed:.2f}s."
        else:
            return False, f"Unknown provider: {provider}"
    except Exception as err:
        return False, f"Connection failed: {str(err)}"


def ask_llm(prompt: str, system_prompt: str = "") -> Optional[str]:
    """Send prompt to the active LLM provider if configured.
    
    Returns raw JSON string response or None if no API is available / error occurs.
    """
    provider = get_llm_provider()
    model = get_model_name()

    if provider == "gemini":
        api_key = get_setting("GEMINI_API_KEY")
        if api_key and "your_" not in api_key.lower():
            try:
                return call_gemini(prompt, system_prompt, api_key, model)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to Local Engine.")
                return None

    elif provider == "groq":
        api_key = get_setting("GROQ_API_KEY")
        if api_key and "your_" not in api_key.lower():
            try:
                return call_groq(prompt, system_prompt, api_key, model)
            except Exception as e:
                logger.warning(f"Groq API call failed: {e}. Falling back to Local Engine.")
                return None

    return None
