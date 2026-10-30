# DevPulse AI — Comprehensive Acceptance Test Report
**Course / Track:** GMRIT Grand AI & NLP Projects  
**Project Track Number:** 06 — Code Explainer and Debugging Tutor  
**Author:** Student Developer  
**Test Suite Status:** 100% Passed (8/8 Acceptance Tests, 15/15 Automated Unit Tests)  

---

## 1. Testing Scope & Methodology
In compliance with **Section 10 (Minimum Testing Checklist)** and **Section 11 (Deliverables to Submit)** of the GMRIT Student Project Handbook, DevPulse AI underwent systematic validation across four input categories:
1. **Normal / Valid Scenarios:** Typical programming bugs across multiple languages (Python, JavaScript).
2. **Runtime & Recursion Scenarios:** Stack overflows and index boundary violations.
3. **Edge & Boundary Scenarios:** Empty inputs, whitespace-only snippets, and minimal length thresholds.
4. **Adversarial & Safety Scenarios:** Oversized payloads, unsupported languages, and logical inversions.

---

## 2. Acceptance Test Matrix (8 Required Cases)

| Test ID | Category | Scenario / Description | Language | Input Snippet | Expected Result | Actual Result | Status |
|:---:|:---:|:---|:---:|:---|:---|:---|:---:|
| **TC-01** | Runtime Error | Python Off-by-one IndexError in loop upper bound | `python` | `for i in range(len(arr) + 1):`<br>`    print(arr[i])` | Identifies off-by-one boundary, removes `+1`, outputs corrected range. | Detected `IndexError: list index out of range`. Replaced `range(len(arr) + 1)` with `range(len(arr))`. Generated unified diff. | **PASS** |
| **TC-02** | Recursion Error | Python Infinite Recursion (missing base condition) | `python` | `def fact(n):`<br>`    return n * fact(n - 1)` | Identifies missing base condition (`n <= 1` or `n == 0`). | Flagged `RecursionError`. Inserted base case `if n <= 1: return 1`. Identified fault line. | **PASS** |
| **TC-03** | Input Validation | Empty / Whitespace-only code input | `python` | `"   \n\t  "` | Raises `ValueError` with clear guidance; rejects empty string. | Raised `ValueError: Code snippet cannot be empty. Please enter or paste your code.` Zero server crash. | **PASS** |
| **TC-04** | Input Validation | Unsupported programming language | `brainfuck` | `print('hello world')` | Rejects non-whitelisted language with list of allowed options. | Raised `ValueError: Unsupported language 'brainfuck'. Supported languages: c, cpp, csharp, go, java, javascript, php, python, ruby, rust, sql, typescript.` | **PASS** |
| **TC-05** | Type Error | JavaScript undefined property access (`TypeError`) | `javascript` | `const name = user.profile.name;` | Suggests optional chaining (`user?.profile?.name`) or defensive guard. | Identified `TypeError: Cannot read properties of undefined`. Suggested optional chaining `user?.profile?.name` and fallback. | **PASS** |
| **TC-06** | Logic Error | Inverted Boolean parity check (no runtime crash) | `python` | `def is_even(n):`<br>`    return n % 2 == 1` | Detects logical inversion (`n % 2 == 0` needed for even numbers). | Identified semantic bug in `return n % 2 == 1`. Corrected to `return n % 2 == 0`. | **PASS** |
| **TC-07** | Security Guard | Oversized input attack / stress test | `python` | `x = 1\n` * 4000 (>15,000 characters) | Rejects input exceeding safety limit with warning message. | Raised `ValueError: Code exceeds the maximum allowed size of 15000 characters`. Protected server memory. | **PASS** |
| **TC-08** | Clean Code | Syntactically and logically valid code snippet | `python` | `def add(a, b):`<br>`    return a + b` | Explains code function clearly without hallucinating false bugs. | Returned accurate plain-English summary. Corrected code matched original. No false positive errors reported. | **PASS** |

---

## 3. Deep-Dive Test Execution Logs

### Case TC-01: Python Off-by-one IndexError
- **Input Code:**
  ```python
  for i in range(len(arr) + 1):
      print(arr[i])
  ```
- **Error Trace:** `IndexError: list index out of range`
- **Output JSON Schema Verification:**
  - `code_summary`: "Iterates through an array and prints each element."
  - `error_type`: "IndexError / Off-by-One Loop"
  - `root_cause`: "In 0-indexed languages like Python, valid indices are 0 to len(arr) - 1. `range(len(arr) + 1)` iterates up to `len(arr)`."
  - `minimal_fix_explanation`: "Change `range(len(arr) + 1)` to `range(len(arr))`."
  - `unified_diff`:
    ```diff
    --- Original Code
    +++ Corrected Code
    @@ -1,2 +1,2 @@
    -for i in range(len(arr) + 1):
    +for i in range(len(arr)):
         print(arr[i])
    ```
- **Latency:** 32ms (Local AST Engine) / 1.4s (Neural LLM)
- **Verdict:** **PASS**

---

### Case TC-03: Empty Code Input Validation
- **Input:** `"   "` (3 whitespace characters)
- **Validation Guard:** `validate_code_input` in `backend/utils/validators.py`
- **Output:**
  ```
  ValueError: Code snippet cannot be empty. Please enter or paste your code.
  ```
- **Verdict:** **PASS** (Zero crash, caught in Streamlit UI with `st.warning`)

---

### Case TC-07: Oversized Input Guardrail
- **Input:** 4,000 lines (`x = 1\n` * 4000 = 24,000 characters)
- **Threshold Limit:** 15,000 characters (`MAX_CODE_CHARS`)
- **Output:**
  ```
  ValueError: Code exceeds the maximum allowed size of 15000 characters (current length: 24000). Please provide a smaller snippet.
  ```
- **Verdict:** **PASS** (DoS defense verified)

---

## 4. Automated Unit Test Suite Summary
DevPulse AI provides a full automated test suite executed via Python's `unittest` / `pytest`:

```powershell
PS C:\devpulse-ai> python -m unittest discover tests
...............
----------------------------------------------------------------------
Ran 15 tests in 0.057s

OK
```

### Breakdown of Automated Tests (`tests/`):
1. `test_validators.py`:
   - `test_valid_python_code`: Checks clean code input passes validation.
   - `test_empty_code_raises_error`: Validates empty string rejection.
   - `test_short_code_raises_error`: Validates minimum length (<3 chars).
   - `test_oversized_code_raises_error`: Enforces 15,000 character maximum limit.
   - `test_unsupported_language_raises_error`: Checks language whitelist enforcement.
   - `test_file_size_and_extension_validation`: Enforces 2MB upload limit and valid extensions.
2. `test_pipeline.py`:
   - `test_index_error_diagnosis`: Validates full diagnostic JSON schema and fix.
   - `test_recursion_error_diagnosis`: Validates base condition insertion.
   - `test_javascript_type_error`: Validates JS optional chaining suggestions.
   - `test_unified_diff_generation`: Verifies `difflib` unified diff format.
   - `test_json_extraction_from_markdown`: Validates regex cleaning of markdown fences.
   - `test_config_fallback`: Verifies graceful fallback when API keys are absent.
   - `test_logic_error_handling`: Tests parity check inversion without error traceback.
   - `test_clean_code_analysis`: Validates analysis of non-buggy code.
   - `test_socratic_hints_progression`: Validates 3-tier progressive hint structure.

---

## 5. Compliance Verification
- [x] Application starts using only documented commands (`streamlit run app.py`).
- [x] Home page explains what the project does and how to begin.
- [x] Valid sample inputs produce structured, useful diagnostic outputs.
- [x] Empty input is rejected with a helpful warning message.
- [x] Missing API key automatically activates the Offline AST Engine without crashing.
- [x] No secrets, private keys, or student data are stored or committed.
- [x] At least 8 comprehensive test cases documented with pass/fail evidence.
