# DevPulse AI — Presentation Deck (5-8 Slides)
**GMRIT Grand AI & NLP Projects Presentation**

---

### Slide 1: Title & Executive Summary
- **Project Name:** DevPulse AI — Code Explainer & Debugging Tutor
- **Project Number:** Track 06
- **Student Name / Roll Number:** [Student Name]
- **Core Value Proposition:** Transforming frustrating error messages into structured learning experiences through Socratic guidance, minimal fixes, and visual diffs.

---

### Slide 2: The Problem & Target Audience
- **Target Audience:** Programming students, CS undergraduates, and junior developers.
- **The Core Problem:**
  - Beginners blindly copy compiler errors or entire solutions from ChatGPT/forums without understanding the underlying flaw.
  - Traditional tools provide either cryptic stack traces (too complex) or complete code dumps (short-circuits learning).
  - High repeat rate of common errors (off-by-one, null pointers, missing base cases).

---

### Slide 3: Solution & Key Features
- **Plain-English Code Summary:** Translates code flow into student-friendly narrative.
- **Root-Cause Identification:** Explains the theoretical mechanism of the bug.
- **Minimal Fix Philosophy:** Prescribes the smallest clean modification rather than rewriting the user's entire code.
- **Interactive Socratic Hint Mode:** 3-step progressive hinting (Observation → Clue → Guidance) to stimulate critical thinking.
- **Visual Unified Diff & Line-by-Line Changes:** Clear comparison of before vs after with line-specific reasons.
- **Edge-Case & Test Generator:** Synthesizes boundary unit tests to cultivate defensive coding.

---

### Slide 4: System Architecture & Data Flow
- **Strict Decoupled Architecture (GMRIT Standard):**
  - **Frontend:** Streamlit (`app.py`, `pages/`, `components/`) — purely UI, zero model logic.
  - **Validation:** `backend.utils.validators` — character limits, language whitelist, sanitization.
  - **Pipeline:** `backend.core.pipeline` — JSON schema prompt engineering, `difflib` calculations.
  - **Service Layer:** `backend.services.llm_service` — multi-provider (Gemini / Groq / Zero-Key Mock Engine).
- **Secret Safety:** `.env` and `.streamlit/secrets.toml` safeguarded via `.gitignore`.

---

### Slide 5: Live Demonstration Workflow
- **Demo Scenario 1: Python IndexError (Off-by-One)**
  - Load from Quick Presets with one click.
  - Inspect Plain Explanation -> Root Cause -> Minimal Fix.
  - Reveal Socratic Hints one by one.
- **Demo Scenario 2: Socratic Interactive Tutor (`pages/1_Interactive_Tutor.py`)**
  - Walkthrough of guided questioning mode where students formulate hypotheses.
- **Demo Scenario 3: Real-Time Acceptance Test Lab (`pages/2_Test_Lab.py`)**
  - Execute 8 automated test checks with instant visual pass/fail confirmation.

---

### Slide 6: Testing & Quality Assurance
- **12 Automated Unit & Pipeline Tests:**
  - Input validation (empty inputs, oversized code, unsupported languages).
  - JSON schema extraction and markdown fence stripping.
  - Standard unified diff generation.
  - Multi-language bug diagnosis (Python, JS, Java, C++).
- **Pass Rate:** 100% across all 12 tests (`pytest` & `python -m unittest`).

---

### Slide 7: Technical Decisions & Tradeoffs
| Choice | Why Selected | Tradeoff / Alternative Considered |
|---|---|---|
| **Streamlit Monorepo** | Direct deployment on Streamlit Community Cloud | Rejected separate FastAPI server to avoid multi-host complexity |
| **REST Calls via Requests** | Zero external heavy SDK conflicts; ultra-fast startup | Direct SDKs have frequent breaking version updates |
| **Zero-Key Mock Engine** | Guaranteed offline evaluation reliability for viva/grading | Remote-only LLMs fail if WiFi drops or API quotas exhaust |
| **No Remote Code Execution** | Server security & prevent malicious script execution | Client-side WebAssembly (Pyodide) reserved for future work |

---

### Slide 8: Limitations & Future Roadmap
- **Current Limitations:**
  - Code analysis is static and symbolic; arbitrary code is not executed on server for safety.
  - Multi-file projects currently require individual file evaluation.
- **Future Enhancements:**
  - Client-side browser execution via Pyodide / WebAssembly.
  - AST-based static syntax linting integrated before LLM prompting.
  - Audio explanation walkthroughs for multi-modal accessibility.
- **Q&A & Viva Readiness:** Open for technical discussion, code inspection, and edge case evaluation!
