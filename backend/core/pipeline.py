"""Core Processing Pipeline for DevPulse AI.

Implements all MVP and advanced capabilities required by Project 06:
- Plain language code explanation
- Root-cause identification & minimal fix
- Corrected code generation & line-by-line diff
- Socratic hint-first pedagogical progression
- Edge case & test case generation
- Time & Space complexity evaluation
"""

import difflib
import json
import logging
import re
from typing import Dict, Any, List, Optional

from backend.services.llm_service import ask_llm

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
      "notes": "Why this edge case matters (e.g. empty collection, boundary values)."
    }
  ],
  "complexity": {
    "time_complexity": "Time complexity analysis (e.g., O(N) or O(N log N))",
    "space_complexity": "Space complexity analysis (e.g., O(1) or O(N))"
  }
}
Do not wrap your response in markdown fences other than ```json if needed. Return strictly valid JSON.
"""


def extract_json_from_text(raw_text: str) -> Dict[str, Any]:
    """Safely extract and parse JSON object from LLM response text."""
    clean_text = raw_text.strip()

    # Remove markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
    if match:
        clean_text = match.group(1).strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # Fallback regex search for outer braces
        brace_match = re.search(r"\{[\s\S]*\}", clean_text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Failed to decode JSON from model. Building fallback structured response.")
        return {
            "code_summary": "The model processed your code snippet.",
            "error_type": "Debugging Analysis",
            "root_cause": raw_text[:500],
            "minimal_fix_explanation": "Review the suggested corrections below.",
            "corrected_code": clean_text,
            "line_by_line_changes": [],
            "socratic_hints": [
                "Check variable values at each step.",
                "Verify loop conditions and array bounds.",
                "Ensure return values match expected types."
            ],
            "edge_cases": [
                {"input": "Empty input", "expected": "Handled without crash", "notes": "Boundary test"}
            ],
            "complexity": {
                "time_complexity": "O(N)",
                "space_complexity": "O(1)"
            }
        }


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


def process_debug_request(code: str, language: str, error_message: str = "") -> Dict[str, Any]:
    """Execute end-to-end debugging analysis pipeline.
    
    Args:
        code: The student's code snippet.
        language: Programming language.
        error_message: Optional runtime or syntax error string.
        
    Returns:
        Structured dictionary with explanation, root cause, fix, hints, diff, and edge cases.
    """
    error_context = f"\nError Message/Stack Trace:\n{error_message}" if error_message else "\n(No error message provided - analyze for logic bugs, infinite loops, or bad practices)"

    prompt = f"""Language: {language}

Code:
```
{code}
```
{error_context}

Analyze this code carefully. Provide plain English explanation, identify the root cause, provide a minimal fix, corrected code, line-by-line breakdown, 3 progressive socratic hints, edge cases, and complexity analysis in valid JSON.
"""

    raw_response = ask_llm(prompt, system_prompt=SYSTEM_PROMPT)
    result = extract_json_from_text(raw_response)

    # Ensure all required keys exist
    result.setdefault("code_summary", "No summary generated.")
    result.setdefault("error_type", "General Issue")
    result.setdefault("root_cause", "No root cause identified.")
    result.setdefault("minimal_fix_explanation", "Check the corrected code.")
    result.setdefault("corrected_code", code)
    result.setdefault("line_by_line_changes", [])
    result.setdefault("socratic_hints", [
        "What is the expected vs actual state of your variables?",
        "Check boundary conditions and loop bounds.",
        "Verify your edge cases."
    ])
    result.setdefault("edge_cases", [])
    result.setdefault("complexity", {"time_complexity": "N/A", "space_complexity": "N/A"})

    # Attach computed unified diff for precise visual display
    result["unified_diff"] = compute_unified_diff(code, result["corrected_code"])
    result["language"] = language

    return result
