"""
PPT Automation — AI-Powered Presentation Generator
Streamlit UI for generating themed PowerPoint presentations.
"""

import streamlit as st
import os
import sys
import logging

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from src.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO)

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="AI Presentation Generator",
    page_icon="🎯",
    layout="centered",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: #888;
        font-size: 1.05rem;
    }

    /* Cards */
    .config-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }

    /* Audience pills */
    .audience-info {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.9rem;
    }

    /* Status box */
    .status-box {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.85rem;
    }

    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
    }

    div[data-testid="stForm"] {
        border: none;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🎯 AI Presentation Generator</h1>
    <p>Generate professional, themed PowerPoint presentations with AI</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Audience info mapping
# ──────────────────────────────────────────────

AUDIENCE_DESCRIPTIONS = {
    "Beginner": "🟢 Simple language, real-world analogies, no jargon. Perfect for introducing new concepts.",
    "Intermediate": "🟡 Standard terminology with practical examples. Assumes basic background knowledge.",
    "Advanced": "🔴 Technical language, deep analysis, research-level depth. For experts in the field.",
}

# ──────────────────────────────────────────────
# Input form
# ──────────────────────────────────────────────

with st.form("ppt_form"):
    st.markdown("### 📝 Presentation Settings")

    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="e.g., History of Black Holes, Machine Learning Basics...",
            help="What should the presentation be about?",
        )

    with col2:
        num_slides = st.number_input(
            "Number of Slides",
            min_value=5,
            max_value=20,
            value=8,
            step=1,
            help="Between 5 and 20 slides",
        )

    st.markdown("### 🎯 Audience Level")

    audience_type = st.select_slider(
        "Who is this presentation for?",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate",
    )

    # Show audience description
    st.markdown(
        f'<div class="audience-info">{AUDIENCE_DESCRIPTIONS[audience_type]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")  # spacing

    submitted = st.form_submit_button(
        "🚀 Generate Presentation",
        use_container_width=True,
        type="primary",
    )

# ──────────────────────────────────────────────
# Generation logic
# ──────────────────────────────────────────────

if submitted:
    if not topic or not topic.strip():
        st.error("⚠️ Please enter a topic for your presentation.")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(fraction: float, message: str):
            progress_bar.progress(fraction)
            status_text.markdown(
                f'<div class="status-box">⏳ {message}</div>',
                unsafe_allow_html=True,
            )

        try:
            with st.spinner(""):
                final_path = run_pipeline(
                    topic=topic.strip(),
                    num_slides=int(num_slides),
                    audience_type=audience_type.lower(),
                    output_dir="output",
                    on_progress=update_progress,
                )

            # Success state
            progress_bar.progress(1.0)
            status_text.markdown(
                '<div class="status-box">✅ Presentation generated successfully!</div>',
                unsafe_allow_html=True,
            )

            # Download button
            with open(final_path, "rb") as f:
                ppt_bytes = f.read()

            st.download_button(
                label="📥 Download Presentation",
                data=ppt_bytes,
                file_name=f"{topic.strip().replace(' ', '_')}_presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                type="primary",
            )

            # Summary
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📑 Slides", int(num_slides))
            with col2:
                st.metric("🎯 Audience", audience_type)
            with col3:
                file_size_kb = len(ppt_bytes) / 1024
                st.metric("📦 File Size", f"{file_size_kb:.0f} KB")

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Generation failed: {str(e)}")
            st.info("💡 **Tip:** If you see a rate limit error, wait ~30 seconds and try again. The Groq free tier has token limits.")

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────

st.markdown("""
<div class="footer">
    Built with LangGraph • Groq AI • python-pptx • Unsplash<br>
    <strong>PPT Automation</strong> — AI-Powered Presentation Generator
</div>
""", unsafe_allow_html=True)
