"""
Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1 (OSHA & IS 456 Standards)
Production-Ready Streamlit Application Entry Point.
"""

import os
import streamlit as st

# Set page configuration must be first Streamlit command
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.asset_generator import generate_all_sample_assets
from modules.crack_diagnostics import render_crack_diagnostics_tab
from modules.gemini_client import AVAILABLE_MODELS, DEFAULT_MODEL, GeminiMultimodalClient
from modules.project_planner import render_project_planner_tab
from modules.safety_audit import render_safety_audit_tab
from modules.site_assistant import render_site_assistant_tab
from modules.ui_components import inject_custom_css, render_header


def main():
    # Inject high-end industrial theme
    inject_custom_css()

    # Pre-generate sample assets if not already on disk
    if not os.path.exists("assets/sample_scaffold_hazard.jpg"):
        generate_all_sample_assets()

    # --- SIDEBAR CONFIGURATION ---
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 12px 0 16px 0;">
                <div style="font-size: 2.2rem; margin-bottom: 4px;">🏗️</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #ffffff; letter-spacing: -0.01em;">
                    CONSTRUCTION INTELLIGENCE
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em;">
                    Skill Wallet Capstone 1
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # 1. API Configuration
        st.markdown("##### 🔐 Gemini API Key & Engine")
        env_key = os.getenv("GEMINI_API_KEY", "")
        if not env_key:
            try:
                env_key = st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                env_key = ""
        api_key_input = st.text_input(
            "Enter Google Gemini API Key:",
            type="password",
            value=env_key,
            help="Your key is never logged or stored. If left blank, the platform automatically operates in high-fidelity demonstration mode.",
            placeholder="AIzaSy...",
        )

        model_choice = st.selectbox(
            "Gemini Model Engine:",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0,
            help="Select Gemini model family for multimodal vision and structural chat inference.",
        )

        force_demo = st.checkbox(
            "Force Offline Simulation Mode",
            value=False,
            help="Check this box to test built-in deterministic engineering scenarios even with an API key provided.",
        )

        # Determine effective API key
        effective_key = None if force_demo else (api_key_input.strip() or None)
        client = GeminiMultimodalClient(api_key=effective_key, model_name=model_choice)

        # Mode Indicator Pill
        if client.is_live and not force_demo:
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 8px 12px; margin: 10px 0;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #34d399;">⚡ LIVE GEMINI ACTIVE</div>
                    <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Connected: {model_choice}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; padding: 8px 12px; margin: 10px 0;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #fbbf24;">💡 DEMO SIMULATION MODE</div>
                    <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Zero API key required; realistic engineering payloads active.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # 2. System Architecture Specs
        st.markdown("##### 🏛️ Platform Architecture")
        st.markdown(
            """
            - **Multimodal LLM:** Gemini 1.5 / 2.5 Flash
            - **Safety Standards:** OSHA 29 CFR 1926 & IS 13415
            - **Structural Codes:** IS 456:2000 & ACI 224R
            - **Generative 3D:** Pollinations AI / Flux
            - **CapEx Engine:** Indian CPWD / RERA Benchmarks
            - **Database:** Zero external DB dependencies (In-Memory Session State)
            """
        )

        st.markdown("---")

        # 3. Kanban Epics Coverage
        st.markdown("##### 📌 Skill Wallet Epics")
        st.markdown(
            """
            <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.6;">
                <div>✅ <strong>Epic 1:</strong> Environment & Streamlit Setup</div>
                <div>✅ <strong>Epic 2:</strong> PPE Safety Vision & Crack Diagnostics</div>
                <div>✅ <strong>Epic 3:</strong> Project Planning & Valuation</div>
                <div>✅ <strong>Epic 4:</strong> Multimodal AI & JSON Contracts</div>
                <div>✅ <strong>Epic 5:</strong> Site Chatbot & Weather Advisory</div>
                <div>✅ <strong>Epic 6:</strong> Modern UI & Cloud Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- TOP BRANDING HEADER ---
    render_header()

    # --- MAIN NAVIGATION TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🦺 Site Safety & PPE Audit (Epic 2)",
            "🔬 Crack Diagnostics & Structural Integrity (Epic 2)",
            "📊 Planning & Real Estate Valuation (Epic 3)",
            "🌤️ Daily Site Assistant & Weather Advisory (Epic 5)",
        ]
    )

    with tab1:
        render_safety_audit_tab(client)

    with tab2:
        render_crack_diagnostics_tab(client)

    with tab3:
        render_project_planner_tab()

    with tab4:
        render_site_assistant_tab(client)

    # --- FOOTER ---
    st.markdown("---")
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #64748b; padding: 10px 0;">
            <div>Multimodal Construction Intelligence Platform &bull; Skill Wallet Capstone Project 1</div>
            <div>Built for Zero-Config Deployment on Streamlit Community Cloud</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
