"""Input and file validators for DevPulse AI.

Provides strict validation and safety checks according to the project handbook.
"""

from typing import Dict, Any, Optional

ALLOWED_LANGUAGES = {
    "python",
    "javascript",
    "typescript",
    "java",
    "cpp",
    "c",
    "csharp",
    "go",
    "rust",
    "sql",
    "php",
    "ruby",
    "other"
}

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs",
    ".go", ".rs", ".sql", ".php", ".rb", ".txt"
}

MAX_CODE_CHARS = 15000
MIN_CODE_CHARS = 3
MAX_ERROR_CHARS = 8000
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2MB


def validate_code_input(
    code: Optional[str],
    language: Optional[str],
    error_message: Optional[str] = ""
) -> Dict[str, str]:
    """Validate and sanitize user code, selected language, and error string.
    
    Args:
        code: Raw code text provided by student.
        language: Programming language identifier.
        error_message: Optional runtime/syntax error message or stack trace.
        
    Returns:
        Dict with sanitized 'code', 'language', and 'error_message'.
        
    Raises:
        ValueError: If any input fails validation criteria.
    """
    if code is None or not code.strip():
        raise ValueError("Code snippet cannot be empty. Please enter or paste your code.")

    sanitized_code = code.strip()

    if len(sanitized_code) < MIN_CODE_CHARS:
        raise ValueError(f"Code is too short ({len(sanitized_code)} chars). Minimum length is {MIN_CODE_CHARS} characters.")

    if len(sanitized_code) > MAX_CODE_CHARS:
        raise ValueError(
            f"Code exceeds the maximum allowed size of {MAX_CODE_CHARS} characters "
            f"(current length: {len(sanitized_code)}). Please provide a smaller snippet."
        )

    if not language:
        raise ValueError("Please select a valid programming language.")

    sanitized_lang = language.strip().lower()
    if sanitized_lang not in ALLOWED_LANGUAGES:
        valid_options = ", ".join(sorted(ALLOWED_LANGUAGES))
        raise ValueError(
            f"Unsupported language '{language}'. Supported languages: {valid_options}."
        )

    sanitized_error = (error_message or "").strip()
    if len(sanitized_error) > MAX_ERROR_CHARS:
        raise ValueError(
            f"Error message exceeds maximum limit of {MAX_ERROR_CHARS} characters. "
            "Please truncate the traceback to the relevant section."
        )

    return {
        "code": sanitized_code,
        "language": sanitized_lang,
        "error_message": sanitized_error
    }


def validate_file_upload(file_name: str, file_size_bytes: int) -> bool:
    """Validate uploaded file name extension and size limit.
    
    Args:
        file_name: Name of the uploaded file.
        file_size_bytes: Size in bytes.
        
    Returns:
        True if valid.
        
    Raises:
        ValueError: If file is too large or not an allowed extension.
    """
    if file_size_bytes <= 0:
        raise ValueError("The uploaded file is empty (0 bytes).")

    if file_size_bytes > MAX_FILE_BYTES:
        max_mb = MAX_FILE_BYTES / (1024 * 1024)
        raise ValueError(f"File size exceeds the {max_mb:.0f}MB limit.")

    ext = "." + file_name.split(".")[-1].lower() if "." in file_name else ""
    if ext not in ALLOWED_EXTENSIONS:
        allowed_str = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"File type '{ext}' is not supported. Allowed extensions: {allowed_str}")

    return True
