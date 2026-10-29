"""Integration and pipeline tests for DevPulse AI.

Verifies end-to-end pipeline execution, AST static analysis reliability,
syntax compilation error detection, unified diff generation, and edge cases.
"""

import unittest
from backend.core.pipeline import (
    process_debug_request,
    compute_unified_diff,
    extract_json_from_text
)
from backend.core.local_analyzer import analyze_with_local_engine
from backend.config import get_llm_provider, get_model_name


class TestPipeline(unittest.TestCase):
    """Pipeline and core logic acceptance tests."""

    def test_pipeline_index_error(self):
        """TC-P01: Verifies structured output for Python IndexError."""
        code = "for i in range(len(scores) + 1):\n    print(scores[i])"
        error = "IndexError: list index out of range"
        res = process_debug_request(code, "python", error)

        self.assertIn("code_summary", res)
        self.assertIn("root_cause", res)
        self.assertIn("minimal_fix_explanation", res)
        self.assertIn("corrected_code", res)
        self.assertIn("socratic_hints", res)
        self.assertIn("edge_cases", res)
        self.assertIn("unified_diff", res)
        self.assertGreaterEqual(len(res["socratic_hints"]), 3)
        self.assertIn("range(len(scores))", res["corrected_code"])

    def test_pipeline_recursion_error(self):
        """TC-P02: Verifies missing base case detection for RecursionError."""
        code = "def compute_factorial(n):\n    return n * compute_factorial(n - 1)"
        error = "RecursionError: maximum recursion depth exceeded"
        res = process_debug_request(code, "python", error)

        self.assertIn("Recursion", res.get("error_type", ""))
        self.assertTrue(len(res["corrected_code"]) > 0)
        self.assertIn("if n <= 1", res["corrected_code"])

    def test_pipeline_syntax_error_detection(self):
        """TC-P03: Verifies exact Python AST SyntaxError detection (missing colon)."""
        code = "def calculate_total(a, b)\n    return a + b"
        res = process_debug_request(code, "python")

        self.assertIn("SyntaxError", res.get("error_type", ""))
        self.assertEqual(res.get("highlight_line"), 1)
        self.assertIn("def calculate_total(a, b):", res.get("corrected_code", ""))

    def test_pipeline_zero_division_detection(self):
        """TC-P04: Verifies ZeroDivisionError validation and remedy."""
        code = "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))"
        error = "ZeroDivisionError: division by zero"
        res = process_debug_request(code, "python", error)

        self.assertIn("ZeroDivision", res.get("error_type", ""))
        self.assertIn("b == 0", res.get("corrected_code", ""))

    def test_pipeline_javascript_type_error(self):
        """TC-P05: Verifies JS TypeError handling (optional chaining)."""
        code = "const name = user.profile.name.toUpperCase();"
        error = "TypeError: Cannot read properties of undefined (reading 'name')"
        res = process_debug_request(code, "javascript", error)

        self.assertEqual(res["language"], "javascript")
        self.assertIn("user?.profile?.name", res["corrected_code"])

    def test_pipeline_cpp_segmentation_fault(self):
        """TC-P06: Verifies C++ out-of-bounds loop check."""
        code = "for (size_t i = 0; i <= numbers.size(); ++i) {\n    std::cout << numbers[i] << std::endl;\n}"
        error = "Segmentation fault"
        res = process_debug_request(code, "cpp", error)

        self.assertIn("i < numbers.size()", res["corrected_code"])

    def test_compute_unified_diff(self):
        """TC-P07: Verifies standard diff computation."""
        orig = "def add(a, b):\n    return a - b"
        corr = "def add(a, b):\n    return a + b"
        diff = compute_unified_diff(orig, corr)
        self.assertIn("-    return a - b", diff)
        self.assertIn("+    return a + b", diff)

    def test_extract_json_from_fenced_markdown(self):
        """TC-P08: Verifies JSON extractor cleans markdown fences properly."""
        markdown_json = "```json\n{\"code_summary\": \"Test summary\", \"error_type\": \"Syntax\"}\n```"
        parsed = extract_json_from_text(markdown_json)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["code_summary"], "Test summary")
        self.assertEqual(parsed["error_type"], "Syntax")

    def test_config_provider_fallback(self):
        """TC-P09: Config defaults to a valid provider without throwing exceptions."""
        provider = get_llm_provider()
        self.assertIn(provider, ("gemini", "groq", "mock"))
        model = get_model_name()
        self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
