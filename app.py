"""DevPulse AI — Code Explainer and Debugging Tutor.

Frontend Streamlit application following the GMRIT Student Project Handbook:
- Strict UI orchestration (no model prompts or business logic in frontend).
- Validates input via backend.utils.validators.
- Processes logic via backend.core.pipeline (Dual Engine: Local AST + Neural LLM).
- Evaluator Quick-Preset loader, interactive line highlighter, and exportable reports.
"""

import json
import os
import streamlit as st

from backend.config import get_llm_provider, get_model_name, is_live_mode
from backend.utils.validators import validate_code_input
from backend.core.pipeline import process_debug_request
from backend.services.llm_service import test_api_connection
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
if "custom_api_key" not in st.session_state:
    st.session_state["custom_api_key"] = ""
if "engine_mode" not in st.session_state:
    st.session_state["engine_mode"] = "Auto (Local AST + Neural Fallback)"

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ Quick Presets (Evaluator Demo)")
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
    st.markdown("### 🧠 Intelligence Engine Settings")
    
    engine_choice = st.radio(
        "Analysis Engine Mode",
        ["Hybrid (Neural LLM with AST Guard)", "Local Static AST Engine (100% Offline)"],
        index=0
    )
    st.session_state["engine_mode"] = engine_choice

    with st.expander("🔑 Optional API Key (Gemini / Groq)", expanded=True):
        current_prov = os.getenv("LLM_PROVIDER", "groq").lower()
        prov_idx = 1 if current_prov == "gemini" else 0
        prov_select = st.selectbox("Provider", ["groq", "gemini"], index=prov_idx)
        
        if prov_select == "groq":
            model_options = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama-3.3-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
        else:
            model_options = [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash-exp"
            ]
            
        selected_model = st.selectbox("Model", model_options, index=0)
        api_key_val = st.text_input("API Key", type="password", value=st.session_state["custom_api_key"])
        if api_key_val:
            st.session_state["custom_api_key"] = api_key_val
            os.environ["GEMINI_API_KEY" if prov_select == "gemini" else "GROQ_API_KEY"] = api_key_val
            os.environ["LLM_PROVIDER"] = prov_select
            os.environ["MODEL_NAME"] = selected_model
        
        if st.button("⚡ Test API Connection"):
            with st.spinner(f"Testing {prov_select.upper()} ({selected_model})..."):
                ok, msg = test_api_connection(prov_select, api_key_val, selected_model)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.markdown("---")
    provider = get_llm_provider()
    model = get_model_name()
    live = is_live_mode()

    if live and "Local" not in engine_choice:
        st.markdown(f"**Active Provider:** `{provider.upper()}`")
        st.markdown(f"**Model:** `{model}`")
        st.info("🟢 Neural AI Engine Active")
    else:
        st.markdown(f"**Active Provider:** `DEV-PULSE LOCAL AST`")
        st.markdown(f"**Mode:** `Deterministic Static Compiler`")
        st.success("⚡ 100% Offline AST Engine Active (Instant & Accurate)")

    st.markdown("---")
    if st.button("🔄 Reset App & Clear Inputs", use_container_width=True):
        st.session_state["code_input"] = ""
        st.session_state["error_input"] = ""
        st.session_state["analysis_result"] = None
        st.session_state["revealed_hints"] = 0
        st.rerun()

# Top Hero banner
render_hero(live and "Local" not in st.session_state["engine_mode"], provider, model)

# Main form input area
st.markdown("#### 📝 Code & Error Input")

col_lang, col_status = st.columns([3, 2])
with col_lang:
    languages = [
        "python", "javascript", "typescript", "java",
        "cpp", "c", "csharp", "go", "rust", "sql"
    ]
    current_lang_idx = languages.index(st.session_state["selected_lang"]) if st.session_state["selected_lang"] in languages else 0
    selected_language = st.selectbox(
        "Target Programming Language",
        languages,
        index=current_lang_idx
    )
    st.session_state["selected_lang"] = selected_language

with col_status:
    st.caption("Engine Status:")
    if "Local" in st.session_state["engine_mode"]:
        st.caption("⚡ **Local Static AST Mode**: Analyzes syntax trees and bytecode logic locally.")
    else:
        st.caption("🤖 **Hybrid Mode**: Combines Neural LLM reasoning with local AST validation.")

col1, col2 = st.columns(2)

with col1:
    code_text = st.text_area(
        "Source Code Snippet",
        value=st.session_state["code_input"],
        height=280,
        placeholder="Paste your source code here..."
    )
    st.session_state["code_input"] = code_text

with col2:
    error_text = st.text_area(
        "Compiler Error / Stack Trace (Optional)",
        value=st.session_state["error_input"],
        height=280,
        placeholder="Paste terminal traceback or compiler error here (Optional: Leave blank for logic bug analysis)..."
    )
    st.session_state["error_input"] = error_text

col_action, col_spacer = st.columns([2, 5])
with col_action:
    analyze_clicked = st.button("🚀 Analyze & Debug Code", type="primary", use_container_width=True)

# Processing trigger
if analyze_clicked:
    try:
        # Step 1: Input Validation
        validated_input = validate_code_input(
            code=st.session_state["code_input"],
            language=st.session_state["selected_lang"],
            error_message=st.session_state["error_input"]
        )

        force_local_mode = "Local" in st.session_state["engine_mode"]

        # Step 2: Backend Pipeline Execution
        with st.spinner("DevPulse AI is inspecting syntax tree, control flow, and error states..."):
            result = process_debug_request(
                code=validated_input["code"],
                language=validated_input["language"],
                error_message=validated_input["error_message"],
                force_local=force_local_mode
            )
            st.session_state["analysis_result"] = result
            st.session_state["revealed_hints"] = 0
            st.toast("Diagnosis complete!", icon="✅")

    except ValueError as val_err:
        st.warning(f"⚠️ Validation Warning: {val_err}")
    except Exception as exc:
        st.error(f"❌ Analysis failed: {exc}")

# Display Results
result = st.session_state.get("analysis_result")
if result:
    st.markdown("---")
    
    # Engine & Classification Banner
    col_e1, col_e2 = st.columns([3, 1])
    with col_e1:
        st.markdown(f"### 📊 Diagnostic Results: `{result.get('error_type', 'General Debugging')}`")
    with col_e2:
        engine_label = result.get("engine_used", "DevPulse Engine")
        st.markdown(f"<span style='background: #312E81; color: #818CF8; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;'>⚡ {engine_label}</span>", unsafe_allow_html=True)

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
        
        # Display code with highlighted error line if available
        if "highlight_line" in result and result["highlight_line"] > 0:
            st.markdown(f"**Identified Fault Line:** `Line {result['highlight_line']}`")

    with tab_root:
        st.markdown("#### Why the error occurs (Root Cause):")
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
                    st.caption(f"Reason: {item.get('reason', '')}")
        else:
            st.caption("No individual line replacements reported.")

        st.markdown("#### Unified Text Diff:")
        render_diff_view(result.get("unified_diff", ""))

    with tab_hints:
        st.markdown("#### 💡 Socratic Hint-First Progression")
        st.caption("Stuck? Reveal hints step-by-step to understand the bug instead of just copying the answer:")
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
                st.markdown(f"🔒 *Hint {idx + 1} is locked. Click 'Reveal Next Hint' to view.*")

        if st.session_state["revealed_hints"] == len(hints) and len(hints) > 0:
            st.success("🎉 You've unlocked all hints! Now attempt writing your fix.")

    with tab_tests:
        st.markdown("#### 🧪 Generated Edge Cases & Test Scenarios")
        st.caption("Test your corrected program against these boundary conditions:")
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

    # Download Report Button
    st.markdown("---")
    report_content = f"""# DevPulse AI — Debugging Audit Report

## 1. Overview
- **Language:** {result.get('language', selected_language).upper()}
- **Issue Classification:** {result.get('error_type', 'N/A')}
- **Engine Used:** {result.get('engine_used', 'DevPulse')}

## 2. Code Summary
{result.get('code_summary', '')}

## 3. Root Cause Analysis
{result.get('root_cause', '')}

## 4. Minimal Remedy
{result.get('minimal_fix_explanation', '')}

## 5. Corrected Code
```
{result.get('corrected_code', '')}
```

## 6. Unified Diff
```diff
{result.get('unified_diff', '')}
```

## 7. Edge Cases & Boundary Conditions
{json.dumps(result.get('edge_cases', []), indent=2)}
"""
    st.download_button(
        label="📥 Download Comprehensive Debugging Report (.md)",
        data=report_content,
        file_name="DevPulse_Debug_Report.md",
        mime="text/markdown"
    )

# Footer with GMRIT compliance notice
render_safety_notice()
