"""Reusable UI components and custom CSS styling for DevPulse AI.

Provides a modern, visually stunning developer experience while maintaining
strict modularity and adherence to the handbook guidelines.
"""

import streamlit as st
from typing import Dict, Any, List


def load_custom_css():
    """Inject polished modern CSS styling for DevPulse AI."""
    st.markdown("""
    <style>
    /* Global Container Tweaks */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Gradient Hero Banner */
    .hero-card {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #1E293B 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #F8FAFC;
        margin-bottom: 0.3rem;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        line-height: 1.5;
    }

    /* Badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-live {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-mock {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    /* Feature Cards */
    .feature-card {
        background: #1E293B;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .feature-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
    }

    /* Diff View Styling */
    .diff-block {
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 0.9rem;
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        line-height: 1.6;
    }
    .diff-add {
        color: #4ADE80;
        background-color: rgba(74, 222, 128, 0.1);
        display: block;
        padding: 0 4px;
        border-radius: 2px;
    }
    .diff-del {
        color: #F87171;
        background-color: rgba(248, 113, 113, 0.1);
        display: block;
        padding: 0 4px;
        border-radius: 2px;
    }
    .diff-ctx {
        color: #94A3B8;
        display: block;
        padding: 0 4px;
    }

    /* Socratic Hint Box */
    .hint-step-box {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #6366F1;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .hint-title {
        font-weight: 700;
        color: #818CF8;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }

    /* Safety Notice Callout */
    .safety-callout {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 0.85rem 1.2rem;
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero(is_live: bool, provider_name: str, model_name: str):
    """Render top hero banner with live status badge."""
    load_custom_css()
    badge_class = "badge-live" if is_live else "badge-mock"
    badge_label = f"🟢 LIVE AI: {provider_name.upper()} ({model_name})" if is_live else f"⚡ READY: DEMO MOCK MODE (Zero-Key Offline)"

    st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <div class="hero-title">💡 DevPulse AI</div>
                <div class="hero-subtitle">Code Explainer & Intelligent Debugging Tutor for Students</div>
            </div>
            <div style="margin-top: 0.5rem;">
                <span class="status-badge {badge_class}">{badge_label}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_diff_view(unified_diff: str):
    """Render clean syntax-colored diff block."""
    if not unified_diff or unified_diff.startswith("No textual differences"):
        st.info("No line differences detected between original and corrected code.")
        return

    html_lines = []
    for line in unified_diff.splitlines():
        # Escape HTML entities
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith("+") and not line.startswith("+++"):
            html_lines.append(f'<span class="diff-add">{escaped}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            html_lines.append(f'<span class="diff-del">{escaped}</span>')
        else:
            html_lines.append(f'<span class="diff-ctx">{escaped}</span>')

    diff_html = f'<div class="diff-block">{"".join(html_lines)}</div>'
    st.markdown(diff_html, unsafe_allow_html=True)


def render_safety_notice():
    """Render GMRIT Handbook compliance academic safety warning."""
    st.markdown("""
    <div class="safety-callout">
        <strong>🛡️ Academic Integrity & Responsible Use:</strong>
        DevPulse AI is an educational assistant designed to foster problem-solving intuition.
        AI answers can be imperfect; always test and verify suggested code in your local environment
        before using. Do not paste sensitive credentials, passwords, or private institutional data.
    </div>
    """, unsafe_allow_html=True)
