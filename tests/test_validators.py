"""Unit tests for DevPulse AI input and file validators.

Uses standard Python unittest framework for universal compatibility
with both `pytest` and standard `python -m unittest`.
"""

import unittest
from backend.utils.validators import validate_code_input, validate_file_upload, ALLOWED_LANGUAGES


class TestValidators(unittest.TestCase):
    """Test suite for input sanitization and boundary constraints."""

    def test_valid_python_code_passes(self):
        """TC-V01: Normal valid Python input must pass validation."""
        code = "def add(x, y):\n    return x + y"
        result = validate_code_input(code, "python", "")
        self.assertEqual(result["language"], "python")
        self.assertEqual(result["code"], code)
        self.assertEqual(result["error_message"], "")

    def test_empty_code_raises_value_error(self):
        """TC-V02: Blank or whitespace-only code must be rejected with helpful error."""
        with self.assertRaises(ValueError) as ctx:
            validate_code_input("   \n   ", "python", "")
        self.assertIn("cannot be empty", str(ctx.exception).lower())

    def test_too_short_code_raises_value_error(self):
        """TC-V03: Code with fewer than minimum chars must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            validate_code_input("a", "python", "")
        self.assertIn("too short", str(ctx.exception).lower())

    def test_oversized_code_raises_value_error(self):
        """TC-V04: Massive code snippet exceeding char threshold must be rejected."""
        large_code = "print('hello')\n" * 2000  # > 15000 chars
        with self.assertRaises(ValueError) as ctx:
            validate_code_input(large_code, "python", "")
        self.assertIn("exceeds the maximum allowed size", str(ctx.exception).lower())

    def test_unsupported_language_raises_value_error(self):
        """TC-V05: Non-whitelisted language identifiers must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_code_input("x = 1", "unknown_lang_xyz", "")
        self.assertIn("unsupported language", str(ctx.exception).lower())

    def test_file_upload_validation(self):
        """TC-V06: File upload size and extension guards."""
        # Valid python file
        self.assertTrue(validate_file_upload("solution.py", 1024))
        
        # Empty file
        with self.assertRaises(ValueError):
            validate_file_upload("empty.py", 0)

        # Invalid extension
        with self.assertRaises(ValueError):
            validate_file_upload("executable.exe", 1024)


if __name__ == "__main__":
    unittest.main()
