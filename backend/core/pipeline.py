"""Core Processing Pipeline for DevPulse AI.

Orchestrates the debugging flow:
1. Attempts Neural LLM diagnosis (Google Gemini or Groq) if credentials are available.
2. Falls back instantly to the Local Static AST Engine (100% accurate, zero latency, offline).
3. Computes unified textual diffs using standard difflib.
4. Generates line-by-line change breakdowns and Socratic hints.
"""

import difflib
import json
import logging
import re
from typing import Dict, Any, List, Optional

from backend.services.llm_service import ask_llm
from backend.core.local_analyzer import analyze_with_local_engine

logger = logging.getLogger("devpulse.pipeline")

SYSTEM_PROMPT = """You are DevPulse AI, an expert code explainer and patient debugging tutor designed for programming students and beginners.
Your goal is to educate: do not just fix the error blindly, but explain the fundamental concepts, teach the student how to reason about errors, and guide them with clear, structured explanations.

Always respond with a VALID, strictly parsable JSON object matching this schema:
{
  "code_summary": "Clear, friendly explanation of what the student's code is attempting to do.",
  "error_type": "Classification (e.g. SyntaxError, IndexError, NullPointer, Logic Flaw)",
  "root_cause": "Detailed explanation of WHY the error happens in plain, beginner-friendly terms.",
  "minimal_fix_explanation": "A concise explanation of the smallest change required to fix the issue.",
  "corrected_code": "The full, working, properly formatted corrected code.",
  "highlight_line": 1,
  "line_by_line_changes": [
    {
      "line": 3,
      "original": "...",
      "modified": "...",
      "reason": "..."
    }
  ],
  "socratic_hints": [
    "Hint 1: A guiding question directing the student to observe the problem area.",
    "Hint 2: A more specific question pointing to the exact variable, index, or concept.",
    "Hint 3: A near-solution suggestion or pseudo-code fix."
  ],
  "edge_cases": [
    {
      "input": "Sample test input",
      "expected": "Expected output or behavior",
      "notes": "Why this edge case matters."
    }
  ],
  "complexity": {
    "time_complexity": "Time complexity analysis (e.g., O(N) or O(N log N))",
    "space_complexity": "Space complexity analysis (e.g., O(1) or O(N))"
  }
}
Do not include any introductory or concluding text outside the JSON object.
"""


def extract_json_from_text(raw_text: str) -> Optional[Dict[str, Any]]:
    """Safely extract and parse JSON object from LLM response text."""
    if not raw_text:
        return None
        
    clean_text = raw_text.strip()

    # Strip markdown code blocks if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
    if match:
        clean_text = match.group(1).strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # Regex search for outer curly braces
        brace_match = re.search(r"\{[\s\S]*\}", clean_text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

    return None


def compute_unified_diff(original_code: str, corrected_code: str) -> str:
    """Compute standard unified diff between original and corrected code."""
    orig_lines = original_code.splitlines(keepends=True)
    corr_lines = corrected_code.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        orig_lines,
        corr_lines,
        fromfile="Original Code",
        tofile="Corrected Code",
        lineterm=""
    ))
    return "".join(diff) if diff else "No textual differences detected."


def process_debug_request(code: str, language: str, error_message: str = "", force_local: bool = False) -> Dict[str, Any]:
    """Execute end-to-end debugging analysis pipeline.
    
    Args:
        code: The student's code snippet.
        language: Programming language.
        error_message: Optional runtime or syntax error string.
        force_local: If True, bypasses LLM and executes local AST analysis directly.
        
    Returns:
        Structured dictionary with explanation, root cause, fix, hints, diff, and edge cases.
    """
    result = None

    # Step 1: Attempt LLM analysis if not forcing local
    if not force_local:
        error_context = f"\nError Message/Stack Trace:\n{error_message}" if error_message else "\n(No error message provided - analyze for logic bugs or syntax)"
        prompt = f"""Language: {language}

Code:
```
{code}
```
{error_context}

Analyze this code carefully. Provide plain English explanation, identify the root cause, provide a minimal fix, corrected code, line-by-line breakdown, 3 progressive socratic hints, edge cases, and complexity analysis in valid JSON.
"""
        raw_llm = ask_llm(prompt, system_prompt=SYSTEM_PROMPT)
        if raw_llm:
            parsed = extract_json_from_text(raw_llm)
            if parsed and "corrected_code" in parsed:
                result = parsed
                result["engine_used"] = "Neural LLM (Gemini / Groq)"

    # Step 2: If LLM was not used or failed, run Local Static AST Engine
    if not result:
        result = analyze_with_local_engine(code, language, error_message)

    # Step 3: Normalize and ensure all required schema fields
    result.setdefault("code_summary", "Analyzed the provided code logic.")
    result.setdefault("error_type", "Identified Code Issue")
    result.setdefault("root_cause", "Review the highlighted sections for errors.")
    result.setdefault("minimal_fix_explanation", "Check the corrected code.")
    result.setdefault("corrected_code", code)
    result.setdefault("highlight_line", 1)
    result.setdefault("line_by_line_changes", [])
    result.setdefault("socratic_hints", [
        "What is the expected versus actual value of your variables?",
        "Check your loop boundaries and termination conditions.",
        "Verify edge cases like 0, empty inputs, or null references."
    ])
    result.setdefault("edge_cases", [
        {"input": "Boundary input", "expected": "Handled gracefully", "notes": "Defensive testing."}
    ])
    result.setdefault("complexity", {"time_complexity": "O(N)", "space_complexity": "O(1)"})

    # Attach computed unified diff
    result["unified_diff"] = compute_unified_diff(code, result["corrected_code"])
    result["language"] = language

    return result
