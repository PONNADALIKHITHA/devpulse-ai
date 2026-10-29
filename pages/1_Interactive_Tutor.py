"""DevPulse AI — Socratic Interactive Tutor Mode.

Advanced Extension page providing an active guided tutoring environment:
- Encourages student reasoning: quizzes the student on the bug's origin.
- Evaluates the student's own hypothesis in real time.
- Delivers progressive pedagogical hints before revealing the code fix.
"""

import streamlit as st
from backend.utils.validators import validate_code_input
from backend.core.pipeline import process_debug_request
from components.ui_cards import load_custom_css, render_safety_notice

st.set_page_config(page_title="Socratic Tutor | DevPulse AI", page_icon="🎓", layout="wide")
load_custom_css()

st.title("🎓 DevPulse Socratic Debugging Tutor")
st.caption("Active Learning Mode: Understand the 'Why' behind code bugs through guided inquiry rather than copying solutions.")

col_lang, _ = st.columns([2, 4])
with col_lang:
    language = st.selectbox("Programming Language", ["python", "javascript", "java", "cpp", "sql"], key="tutor_lang")

sample_starter = """def find_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

# Bug occurs when list is empty
print(find_average([]))"""

code_snippet = st.text_area("Buggy Code to Analyze", value=sample_starter, height=180)
error_msg = st.text_input("Observed Error (Optional)", value="ZeroDivisionError: division by zero")

if "tutor_data" not in st.session_state:
    st.session_state["tutor_data"] = None
if "revealed_step" not in st.session_state:
    st.session_state["revealed_step"] = 1

col_btn, _ = st.columns([2, 4])
with col_btn:
    if st.button("🚀 Start Tutoring Session", type="primary", use_container_width=True):
        try:
            validated = validate_code_input(code_snippet, language, error_msg)
            with st.spinner("Analyzing syntax tree and preparing Socratic prompts..."):
                data = process_debug_request(validated["code"], validated["language"], validated["error_message"])
                st.session_state["tutor_data"] = data
                st.session_state["revealed_step"] = 1
        except ValueError as e:
            st.warning(str(e))
        except Exception as e:
            st.error(f"Error: {e}")

data = st.session_state.get("tutor_data")
if data:
    st.markdown("---")
    st.markdown(f"### 🎯 Guided Diagnosis: `{data.get('error_type', 'Code Analysis')}`")
    
    st.info(f"**Context:** {data.get('code_summary', '')}")

    hints = data.get("socratic_hints", [])
    step = st.session_state.get("revealed_step", 1)

    st.markdown("#### Step 1: Formulate Your Hypothesis")
    if len(hints) > 0:
        st.markdown(f"> 💬 **Tutor Inquiry:** {hints[0]}")

    student_guess = st.text_input("What do you think is causing this behavior?", placeholder="e.g. len(numbers) is 0 so division by zero occurs", key="guess_input")
    if student_guess:
        guess_lower = student_guess.lower()
        root_lower = data.get("root_cause", "").lower()
        err_lower = data.get("error_type", "").lower()

        # Check for semantic match
        keywords = [w for w in guess_lower.split() if len(w) > 3]
        matches = [w for w in keywords if w in root_lower or w in err_lower]
        
        if len(matches) >= 2 or any(k in guess_lower for k in ["zero", "bound", "range", "colon", "null", "loop", "base"]):
            st.success("🌟 **Spot on!** You identified the core flaw. Compare your reasoning with the diagnostic clue below.")
        else:
            st.info("💡 Good attempt! Check the diagnostic clue below to sharpen your hypothesis.")

    if step >= 2:
        st.markdown("#### Step 2: Diagnostic Clue")
        if len(hints) > 1:
            st.markdown(f"> 🔎 **Tutor Hint:** {hints[1]}")
    
    if step >= 3:
        st.markdown("#### Step 3: Targeted Remediation")
        if len(hints) > 2:
            st.markdown(f"> 🛠️ **Tutor Guidance:** {hints[2]}")

    col_btn1, col_btn2, _ = st.columns([2, 2, 4])
    with col_btn1:
        if step < len(hints):
            if st.button(f"Next Hint ({step + 1}/{len(hints)})", use_container_width=True):
                st.session_state["revealed_step"] = step + 1
                st.rerun()
    with col_btn2:
        reveal_final = st.button("🔓 Reveal Solution & Code Diff", use_container_width=True)

    if reveal_final or step > len(hints):
        st.markdown("---")
        st.markdown("### 🏆 Solution & Verification")
        st.markdown(f"**Root Cause:** {data.get('root_cause', '')}")
        st.markdown(f"**Minimal Fix:** {data.get('minimal_fix_explanation', '')}")
        st.code(data.get("corrected_code", ""), language=language)

render_safety_notice()
