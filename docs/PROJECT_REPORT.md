# DevPulse AI — Comprehensive Project Report
**Course / Track:** GMRIT Grand AI & NLP Projects  
**Project Track Number:** 06 — Code Explainer and Debugging Tutor  
**Author:** Student Developer  

---

## 1. Problem Statement
Novice programmers and undergraduate engineering students face steep learning curves when diagnosing runtime failures, syntax mistakes, and logical bugs. Modern IDEs and compilers emit cryptic stack traces and error messages that assume deep familiarity with low-level execution models (e.g., `Segmentation Fault`, `RecursionError: maximum recursion depth exceeded`, `TypeError: Cannot read properties of undefined`). Consequently, students frequently resort to blindly copying errors into public forums or copy-pasting solutions from generic AI tools without understanding the underlying flaw. This results in superficial learning, recurring programming errors, and poor problem-solving intuition.

**DevPulse AI** addresses this gap by creating an interactive, educational debugging tutor. Instead of serving as a passive code replacement engine, DevPulse AI explains what the code intends to do, identifies the precise theoretical root cause, offers progressive Socratic hints, demonstrates the minimal necessary fix, visualizes line-by-line diffs, and generates edge-case unit tests.

---

## 2. Objectives
1. **Plain-English Explanations:** Provide intuitive descriptions of confusing stack traces and source code logic.
2. **Pedagogical Socratic Scaffolding:** Prevent answer-copying by providing a 3-step hint progression (Observation, Diagnostic Clue, Targeted Remediation).
3. **Transparent & Minimal Remediation:** Pinpoint only the lines requiring adjustment, avoiding massive code rewrites that overwhelm beginners.
4. **Defensive Testing Culture:** Synthesize edge-case boundary tests (e.g. empty inputs, boundary values) to teach defensive software engineering.
5. **Architectural Decoupling & Reliability:** Maintain strict separation between UI orchestration and backend logic, supplemented with an offline mock fallback engine to guarantee zero demo failures.

---

## 3. Related Work and Theoretical Foundation
- **Automated Program Repair (APR):** Traditional APR tools utilize search-based genetic algorithms or constraint solvers (e.g. GenProg, SemFix). While mathematically rigorous, they lack natural language explanations suitable for novice pedagogy.
- **LLM-Based Coding Assistants:** Commercial tools (e.g. GitHub Copilot, ChatGPT) excel at autocomplete and code generation but default to providing complete solutions directly, short-circuiting student cognitive engagement.
- **Socratic Pedagogy in CS Education:** Educational research indicates that guided inquiry and minimal hint delivery improve long-term conceptual retention compared to direct answer disclosure. DevPulse AI operationalizes this through structured JSON-guided LLM prompting.

---

## 4. Architecture & System Design
The application is structured as a decoupled Streamlit architecture per GMRIT Project Handbook standards:

```
[ User Browser / Client ]
           │
           ▼
[ Streamlit Frontend (app.py, pages/) ]
           │
           ▼
[ backend.utils.validators ]
           │
           ▼
[ backend.core.pipeline ]
           │
           ▼
[ backend.services.llm_service ] ──► [ Google Gemini / Groq / Mock Engine ]
```

### Module Breakdown:
1. **Frontend Layer (`app.py`, `pages/`, `components/`):**
   - Collects inputs (code, language, error trace).
   - Manages state, loading spinners, and toast notifications.
   - Houses specialized views: Main Analyzer, Socratic Interactive Tutor, and Acceptance Test Lab.
   - Free of all prompt strings, API calls, and business logic.
2. **Configuration Manager (`backend/config.py`):**
   - Implements tiered configuration lookup (`st.secrets` -> `.env` -> `os.environ`).
   - Automatically detects provider availability and falls back to Mock Engine if credentials are absent.
3. **Validator Layer (`backend/utils/validators.py`):**
   - Validates character bounds (min 3 chars, max 15,000 chars).
   - Whitelists supported languages (`python`, `javascript`, `java`, `cpp`, `c`, `csharp`, `go`, `rust`, `sql`).
   - Guards against oversized stack traces and malformed file uploads.
4. **Pipeline Orchestrator (`backend/core/pipeline.py`):**
   - Injects structured JSON prompt contracts into LLM interactions.
   - Computes standard unified diffs using Python's `difflib`.
   - Structures 6 core learning outputs: summary, root cause, minimal fix, line diffs, Socratic hints, edge cases, and complexity.
5. **LLM Service Layer (`backend/services/llm_service.py`):**
   - Implements REST adapters for Google Gemini v1beta and Groq OpenAI-compatible endpoints.
   - Includes an intelligent Offline Mock Engine with rich, zero-key diagnostic responses for instant offline evaluation.

---

## 5. Implementation Details
- **Decoupled REST Calls:** Implemented via lightweight Python `requests` with 25-second timeouts to avoid third-party SDK version conflicts.
- **Safe JSON Extraction:** Utilizes regex matching to strip Markdown code blocks (````json ... ````) and handles malformed model output gracefully.
- **Visual Diff Renderer:** Formats unified diff lines into syntax-colored HTML badges (`diff-add`, `diff-del`, `diff-ctx`).
- **Secret Safety:** `.env` and `.streamlit/secrets.toml` are strictly excluded via `.gitignore`, while `.env.example` provides documentation for collaborators.

---

## 6. Testing & Evaluation
Testing was conducted using both unit tests (`test_validators.py`, `test_pipeline.py`) and manual acceptance checks in the interactive Test Lab (`pages/2_Test_Lab.py`):

| Test ID | Scenario | Input Type | Expected Outcome | Actual Outcome | Status |
|---|---|---|---|---|---|
| TC-01 | Python Off-by-one IndexError | Normal Valid | Detects index out of bounds, removes `+1` | Correctly identified off-by-one; fixed range | PASS |
| TC-02 | Infinite Recursion | Normal Valid | Detects missing base case in factorial | Added `if n <= 1: return 1` | PASS |
| TC-03 | Empty Input | Edge Case | Rejects empty string with helpful message | Raised `ValueError: Code snippet cannot be empty` | PASS |
| TC-04 | Unsupported Language | Edge Case | Rejects non-whitelisted language | Raised `ValueError: Unsupported language` | PASS |
| TC-05 | JS Undefined Property | Normal Valid | Suggests optional chaining (`?.`) | Successfully added `?.` and fallback | PASS |
| TC-06 | Logic Bug (No Error Message) | Logic Error | Analyzes code flow and flags inverted condition | Flagged `n % 2 == 1` inverted logic | PASS |
| TC-07 | Oversized Input (>15k chars) | Malicious / Stress | Rejects input exceeding safety limits | Rejected with character threshold alert | PASS |
| TC-08 | Valid Code (No Errors) | Normal Valid | Summarizes code without inventing false bugs | Clean explanation provided without false warnings | PASS |

---

## 7. Results & Key Findings
1. **Pedagogical Efficacy:** Separating the explanation into progressive tabs and Socratic hints prevents cognitive overload and encourages students to reflect on language-specific mechanics.
2. **Reliability Under Zero-Key Conditions:** The offline mock engine allows instructors and evaluators to test all core workflows without needing an active API key or uninhibited internet connection.
3. **Execution Latency:** Live Gemini API calls complete in 1.2–2.5 seconds, while Mock Mode responses evaluate in under 40 milliseconds.

---

## 8. Limitations & Future Scope
- **Limitations:**
  - Code execution is intentionally disallowed on the server for security reasons; test validation relies on symbolic reasoning.
  - LLMs may occasionally offer multiple valid refactorings where only one was intended by the student.
- **Future Work:**
  - Client-side WebAssembly execution (Pyodide) for safe, client-side test execution.
  - Multi-file project context awareness via AST-based dependency graphs.
  - Audio explanation synthesis for multi-modal student support.

---

## 9. Conclusion
DevPulse AI fulfills all GMRIT Grand AI & NLP Project requirements by delivering a robust, modular, attractive, and pedagogically sound debugging assistant. By emphasizing root-cause comprehension, line-by-line diffs, and progressive hinting, it equips students to become self-reliant, confident software developers.
