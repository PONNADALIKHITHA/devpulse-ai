"""DevPulse AI — Socratic Interactive Tutor Mode.

Advanced Extension page providing a dedicated step-by-step tutoring environment.
Instead of immediately revealing the answer, it quizzes the student on the bug's origin
and checks their proposed fix.
"""

import streamlit as st
from backend.utils.validators import validate_code_input
from backend.core.pipeline import process_debug_request
from components.ui_cards import load_custom_css, render_safety_notice

st.set_page_config(page_title="Socratic Tutor | DevPulse AI", page_icon="🎓", layout="wide")
load_custom_css()

st.title("🎓 DevPulse Socratic Tutor")
st.caption("Active Learning Mode: Understand the 'Why' behind errors through guided questioning rather than copying answers.")

col_lang, _ = st.columns([2, 4])
with col_lang:
    language = st.selectbox("Language", ["python", "javascript", "java", "cpp", "sql"], key="tutor_lang")

sample_starter = """def find_average(numbers):\n    total = 0\n    for i in range(len(numbers)):\n        total += numbers[i]\n    return total / len(numbers)\n\nprint(find_average([]))"""

code_snippet = st.text_area("Buggy Code to Analyze", value=sample_starter, height=180)
error_msg = st.text_input("Observed Error (Optional)", value="ZeroDivisionError: division by zero")

if "tutor_data" not in st.session_state:
    st.session_state["tutor_data"] = None
if "revealed_step" not in st.session_state:
    st.session_state["revealed_step"] = 1

if st.button("🚀 Start Tutoring Session", type="primary"):
    try:
        validated = validate_code_input(code_snippet, language, error_msg)
        with st.spinner("Preparing interactive tutoring session..."):
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
    st.markdown(f"### 🎯 Guided Debugging: `{data.get('error_type', 'Code Analysis')}`")
    
    st.info(f"**Context:** {data.get('code_summary', '')}")

    hints = data.get("socratic_hints", [])
    step = st.session_state.get("revealed_step", 1)

    st.markdown(f"#### Step 1: Investigation Question")
    if len(hints) > 0:
        st.markdown(f"> 💬 **Tutor Prompt:** {hints[0]}")

    student_guess = st.text_input("Your Hypothesis (What do you think is causing the issue?):", key="guess_input")
    if student_guess:
        st.success("Great job formulating a hypothesis! Compare it with the guidance below.")

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
            if st.button(f"Next Hint ({step + 1}/{len(hints)})"):
                st.session_state["revealed_step"] = step + 1
                st.rerun()
    with col_btn2:
        reveal_final = st.button("🔓 Reveal Full Solution & Diff")

    if reveal_final or step > len(hints):
        st.markdown("---")
        st.markdown("### 🏆 Solution & Explanation")
        st.markdown(f"**Root Cause:** {data.get('root_cause', '')}")
        st.markdown(f"**Minimal Fix:** {data.get('minimal_fix_explanation', '')}")
        st.code(data.get("corrected_code", ""), language=language)

render_safety_notice()
