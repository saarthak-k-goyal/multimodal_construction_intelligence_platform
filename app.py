"""
ConstructAI - Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1 • Production-Ready Streamlit Application
"""

import os
import streamlit as st

st.set_page_config(
    page_title="ConstructAI - Construction Intelligence Platform",
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
from modules.ui_components import inject_custom_css


def main():
    inject_custom_css()

    # Pre-generate synthetic reference assets if missing
    if not os.path.exists("assets/sample_scaffold_hazard.jpg"):
        generate_all_sample_assets()

    # --- SIDEBAR (Matching Reference UI Specs) ---
    with st.sidebar:
        # ConstructAI Logo & Brand
        st.markdown(
            """
            <div class="construct-brand">
                <span style="font-size:1.6rem;">🏗️</span>
                <span class="construct-brand-text">CONSTRUCT<span>AI</span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Feature Navigation Options
        st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;'>NAVIGATION MODULES</div>", unsafe_allow_html=True)
        nav_choice = st.radio(
            "Select Module:",
            [
                "🛡️ Safety Monitor (Epic 2)",
                "⚡ Crack Detection (Epic 2)",
                "🏢 Real Estate & Planning (Epic 3)",
                "💬 Daily Assistant & Weather (Epic 5)",
            ],
            index=0,
            label_visibility="collapsed",
            key="construct_nav_radio",
        )

        st.markdown("---")

        # API Configuration (with Streamlit Secrets & OS Environment integration)
        st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px;'>GEMINI AI ENGINE</div>", unsafe_allow_html=True)
        env_key = os.getenv("GEMINI_API_KEY", "")
        if not env_key:
            try:
                env_key = st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                env_key = ""

        api_key_input = st.text_input(
            "API Key (Free Tier Supported):",
            type="password",
            value=env_key,
            placeholder="AIzaSy...",
            help="Enter your Gemini API key. If left blank, demonstration mode activates with zero errors.",
            key="sidebar_api_key",
        )

        model_choice = st.selectbox(
            "Model Selection:",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0,
            help="gemini-1.5-flash is free and recommended for multimodal inference.",
            key="sidebar_model_select",
        )

        client = GeminiMultimodalClient(api_key=api_key_input.strip() or None, model_name=model_choice)

        if client.is_live:
            st.markdown(
                f"""
                <div style="background:rgba(16, 185, 129, 0.15); border:1px solid #10b981; border-radius:4px; padding:6px 10px; margin:8px 0; font-size:0.75rem; color:#34d399; font-weight:700;">
                    ● LIVE: {model_choice}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background:rgba(255, 107, 0, 0.12); border:1px solid #ff6b00; border-radius:4px; padding:6px 10px; margin:8px 0; font-size:0.75rem; color:#ff9800; font-weight:700;">
                    ○ DEMO SIMULATION MODE ACTIVE
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Standards & Codal Specs
        st.markdown(
            """
            <div style="font-size:0.72rem; color:#9ca3af; line-height:1.5;">
                <div><strong>Standards:</strong> OSHA 1926 &bull; IS 456:2000</div>
                <div><strong>Forensics:</strong> ACI 224R &bull; EN 1504</div>
                <div><strong>Generative 3D:</strong> Pollinations AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # System Status (Reference Footer)
        st.markdown(
            """
            <div style="font-size:0.72rem; color:#6b7280; padding-top:6px;">
                <div>v1.0.0 ConstructionGPT</div>
                <div style="color:#10b981; font-weight:700; margin-top:2px;">● System Online</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- TOP TABS (Mapped to Navigation) ---
    tab_list = [
        "🛡️ Safety Monitor (Epic 2)",
        "⚡ Crack Detection (Epic 2)",
        "🏢 Real Estate & Planning (Epic 3)",
        "💬 Daily Assistant & Weather (Epic 5)",
    ]

    # Map sidebar selection to active tab index
    active_idx = 0
    if "Crack" in nav_choice:
        active_idx = 1
    elif "Real Estate" in nav_choice or "Planning" in nav_choice:
        active_idx = 2
    elif "Daily Assistant" in nav_choice or "Weather" in nav_choice or "Chatbot" in nav_choice:
        active_idx = 3

    tab1, tab2, tab3, tab4 = st.tabs(tab_list)

    with tab1:
        render_safety_audit_tab(client)

    with tab2:
        render_crack_diagnostics_tab(client)

    with tab3:
        render_project_planner_tab()

    with tab4:
        render_site_assistant_tab(client)


if __name__ == "__main__":
    main()
