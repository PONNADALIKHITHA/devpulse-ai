"""DevPulse AI — Code Explainer and Debugging Tutor.

Frontend Streamlit application following the GMRIT Student Project Handbook:
- Pure UI orchestration (no prompts or model logic in frontend).
- Validates input via backend.utils.validators.
- Processes logic via backend.core.pipeline.
- Includes sample scenario quick-loader for evaluators.
"""

import json
import os
import streamlit as st

from backend.config import get_llm_provider, get_model_name, is_live_mode
from backend.utils.validators import validate_code_input
from backend.core.pipeline import process_debug_request
from components.ui_cards import (
    render_hero,
    render_diff_view,
    render_safety_notice
)

# Page configuration
st.set_page_config(
    page_title="DevPulse AI | Debugging Tutor",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load sample scenarios
SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample", "sample_bugs.json")


@st.cache_data
def load_sample_scenarios():
    """Load pre-configured sample bugs for quick evaluator demonstration."""
    try:
        with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


sample_bugs = load_sample_scenarios()

# Session state initialization
if "code_input" not in st.session_state:
    st.session_state["code_input"] = ""
if "error_input" not in st.session_state:
    st.session_state["error_input"] = ""
if "selected_lang" not in st.session_state:
    st.session_state["selected_lang"] = "python"
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "revealed_hints" not in st.session_state:
    st.session_state["revealed_hints"] = 0

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ Quick Presets")
    st.caption("Select a sample bug scenario to test instantly:")

    preset_options = ["-- Choose a Preset --"] + [f"{b['title']}" for b in sample_bugs]
    chosen_preset = st.selectbox("Sample Bug Library", preset_options)

    if chosen_preset != "-- Choose a Preset --":
        selected_sample = next((b for b in sample_bugs if b["title"] == chosen_preset), None)
        if selected_sample:
            st.session_state["code_input"] = selected_sample["code"]
            st.session_state["error_input"] = selected_sample["error_message"]
            st.session_state["selected_lang"] = selected_sample["language"]
            st.session_state["analysis_result"] = None
            st.session_state["revealed_hints"] = 0
            st.success(f"Loaded: {selected_sample['title']}")

    st.markdown("---")
    st.markdown("### 🔧 Engine Status")
    provider = get_llm_provider()
    model = get_model_name()
    live = is_live_mode()

    if live:
        st.markdown(f"**Provider:** `{provider.upper()}`")
        st.markdown(f"**Model:** `{model}`")
        st.info("Live AI API connection active.")
    else:
        st.markdown(f"**Provider:** `MOCK ENGINE`")
        st.markdown(f"**Mode:** `Offline Demo / Zero Key`")
        st.warning("Running in Zero-Key Mock Mode (Offline ready). Configure API key in `.env` or Streamlit Secrets for live LLM.")

    st.markdown("---")
    if st.button("🔄 Reset App & Clear Inputs", use_container_width=True):
        st.session_state["code_input"] = ""
        st.session_state["error_input"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["revealed_hints"] = 0
        st.rerun()

# Top Hero banner
render_hero(live, provider, model)

# Main form input area
st.markdown("#### 📝 Code & Error Input")

col_lang, col_clear = st.columns([3, 1])
with col_lang:
    languages = [
        "python", "javascript", "typescript", "java",
        "cpp", "c", "csharp", "go", "rust", "sql"
    ]
    current_lang_idx = languages.index(st.session_state["selected_lang"]) if st.session_state["selected_lang"] in languages else 0
    selected_language = st.selectbox(
        "Select Programming Language",
        languages,
        index=current_lang_idx
    )
    st.session_state["selected_lang"] = selected_language

col1, col2 = st.columns(2)

with col1:
    code_text = st.text_area(
        "Your Code Snippet",
        value=st.session_state["code_input"],
        height=280,
        placeholder="Paste your source code here..."
    )
    st.session_state["code_input"] = code_text

with col2:
    error_text = st.text_area(
        "Error Message / Traceback (Optional)",
        value=st.session_state["error_input"],
        height=280,
        placeholder="Paste error message or console traceback here (Leave empty for logic bugs/clean explanations)..."
    )
    st.session_state["error_input"] = error_text

col_action, col_spacer = st.columns([2, 5])
with col_action:
    analyze_clicked = st.button("🚀 Analyze & Debug Code", type="primary", use_container_width=True)

# Processing trigger
if analyze_clicked:
    try:
        # Step 1: Input Validation through backend validator
        validated_input = validate_code_input(
            code=st.session_state["code_input"],
            language=st.session_state["selected_lang"],
            error_message=st.session_state["error_input"]
        )

        # Step 2: Backend Pipeline Execution
        with st.spinner("DevPulse AI is analyzing syntax, execution flow, and root cause..."):
            result = process_debug_request(
                code=validated_input["code"],
                language=validated_input["language"],
                error_message=validated_input["error_message"]
            )
            st.session_state["analysis_result"] = result
            st.session_state["revealed_hints"] = 0
            st.toast("Analysis complete!", icon="✅")

    except ValueError as val_err:
        st.warning(f"⚠️ Validation Warning: {val_err}")
    except Exception as exc:
        st.error(f"❌ Analysis failed: {exc}")

# Display Results
result = st.session_state.get("analysis_result")
if result:
    st.markdown("---")
    st.markdown("### 📊 Diagnostic Results")

    # Diagnostic Summary Badges
    st.markdown(
        f"**Issue Classification:** `{result.get('error_type', 'General Debugging')}` | "
        f"**Language:** `{result.get('language', selected_language).upper()}`"
    )

    tab_summary, tab_root, tab_code, tab_hints, tab_tests, tab_complexity = st.tabs([
        "📖 Plain Explanation",
        "🔍 Root Cause & Fix",
        "🔄 Corrected Code & Diff",
        "💡 Socratic Hint Mode",
        "🧪 Edge Cases & Tests",
        "⏱️ Complexity"
    ])

    with tab_summary:
        st.markdown("#### What this code does:")
        st.info(result.get("code_summary", "No summary available."))

    with tab_root:
        st.markdown("#### Why the error occurs:")
        st.error(result.get("root_cause", "No root cause identified."))

        st.markdown("#### Minimal recommended remedy:")
        st.success(result.get("minimal_fix_explanation", "Check corrected code."))

    with tab_code:
        st.markdown("#### Corrected Code:")
        st.code(result.get("corrected_code", ""), language=result.get("language", "python"))

        st.markdown("#### Line-by-Line Changes:")
        changes = result.get("line_by_line_changes", [])
        if changes:
            for item in changes:
                with st.expander(f"📍 Line {item.get('line', '?')}: {item.get('reason', 'Modification')}", expanded=True):
                    st.markdown(f"**Original:** `{item.get('original', '')}`")
                    st.markdown(f"**Modified:** `{item.get('modified', '')}`")
                    st.caption(f"Explanation: {item.get('reason', '')}")
        else:
            st.caption("No individual line replacements reported.")

        st.markdown("#### Unified Text Diff:")
        render_diff_view(result.get("unified_diff", ""))

    with tab_hints:
        st.markdown("#### 💡 Socratic Hint-First Progression")
        st.caption("Stuck? Reveal hints step-by-step instead of reading the solution right away!")
        hints = result.get("socratic_hints", [])
        current_hints = st.session_state.get("revealed_hints", 0)

        if st.button("🔍 Reveal Next Hint", key="reveal_hint_btn"):
            if current_hints < len(hints):
                st.session_state["revealed_hints"] = current_hints + 1
                st.rerun()

        for idx, hint_text in enumerate(hints):
            if idx < st.session_state["revealed_hints"]:
                st.markdown(f"""
                <div class="hint-step-box">
                    <div class="hint-title">Hint {idx + 1} of {len(hints)}</div>
                    <div>{hint_text}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"🔒 *Hint {idx + 1} is hidden. Click 'Reveal Next Hint' to view.*")

        if st.session_state["revealed_hints"] == len(hints) and len(hints) > 0:
            st.success("🎉 You've revealed all pedagogical hints! Now try writing your fix.")

    with tab_tests:
        st.markdown("#### 🧪 Generated Edge Cases & Test Scenarios")
        st.caption("Verify your fixed program against these boundary conditions:")
        edge_cases = result.get("edge_cases", [])
        if edge_cases:
            for idx, ec in enumerate(edge_cases, 1):
                st.markdown(f"""
                <div class="feature-card">
                    <strong>Test Case {idx}:</strong> <code>{ec.get('input', '')}</code><br/>
                    <strong>Expected Output:</strong> <code>{ec.get('expected', '')}</code><br/>
                    <small style="color: #94A3B8;">{ec.get('notes', '')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific edge cases generated.")

    with tab_complexity:
        st.markdown("#### ⏱️ Algorithmic Complexity Breakdown")
        comp = result.get("complexity", {})
        col_t, col_s = st.columns(2)
        with col_t:
            st.metric("Time Complexity", comp.get("time_complexity", "O(N)"))
        with col_s:
            st.metric("Space Complexity", comp.get("space_complexity", "O(1)"))

# Footer with GMRIT compliance notice
render_safety_notice()
