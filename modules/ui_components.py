"""
UI Components and Theme Styling Module
ConstructAI Lightweight Industrial Theme matching reference UI design.
"""

import json
from typing import Any, Dict, Optional
import streamlit as st


def inject_custom_css():
    """Injects lightweight modern ConstructAI styling matching reference specs."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {
        --c-orange: #ff6b00;
        --c-orange-hover: #e05e00;
        --c-orange-light: rgba(255, 107, 0, 0.08);
        --c-dark-sidebar: #121316;
        --c-bg-canvas: #f4f5f7;
        --c-card: #ffffff;
        --c-border: #e2e4e8;
        --c-text-primary: #111827;
        --c-text-secondary: #6b7280;
    }

    /* Main App Background */
    .stApp {
        background-color: var(--c-bg-canvas);
        color: var(--c-text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--c-dark-sidebar) !important;
        border-right: 2px solid var(--c-orange) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] hr {
        border-color: #262930 !important;
        margin: 14px 0 !important;
    }

    /* ConstructAI Brand Header in Sidebar */
    .construct-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 0 18px 0;
    }
    .construct-brand-text {
        font-size: 1.25rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .construct-brand-text span {
        color: var(--c-orange);
    }

    /* Top Navigation Bar & Action Header */
    .top-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    .top-page-title {
        font-size: 1.55rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: -0.01em;
        color: #111827;
        margin: 0;
    }
    .ai-active-pill {
        background-color: var(--c-orange);
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 5px 14px;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Clean White Cards */
    .ui-panel-card {
        background: #ffffff;
        border: 1px solid var(--c-border);
        border-radius: 6px;
        padding: 22px 24px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        min-height: 480px;
    }
    .ui-card-title {
        font-size: 0.95rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #111827;
        margin-top: 0;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Empty State Waiting For Input */
    .empty-state-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 380px;
        color: #9ca3af;
        font-size: 0.95rem;
        font-style: italic;
        text-align: center;
    }

    /* Primary Orange Action Button */
    div.stButton > button[kind="primary"] {
        background-color: var(--c-orange) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        padding: 12px 20px !important;
        border-radius: 4px !important;
        box-shadow: 0 2px 4px rgba(255, 107, 0, 0.25) !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: var(--c-orange-hover) !important;
        box-shadow: 0 4px 10px rgba(255, 107, 0, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* Metric Boxes */
    .metric-grid-clean {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin-bottom: 18px;
    }
    .metric-item-clean {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 14px 16px;
    }
    .metric-item-clean.highlight {
        border-left: 4px solid var(--c-orange);
    }
    .metric-item-clean.green {
        border-left: 4px solid #10b981;
    }
    .metric-label-clean {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #6b7280;
        margin-bottom: 4px;
    }
    .metric-val-clean {
        font-size: 1.55rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-sub-clean {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 4px;
    }

    /* Tags and Badges */
    .tag-hazard {
        display: inline-block;
        background-color: var(--c-orange);
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        padding: 4px 10px;
        border-radius: 4px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .tag-check {
        display: inline-block;
        background-color: #e5e7eb;
        color: #374151;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        padding: 4px 10px;
        border-radius: 4px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .tag-compliant {
        display: inline-block;
        background-color: #10b981;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 4px;
    }
    .tag-critical {
        display: inline-block;
        background-color: #ef4444;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 4px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #ffffff;
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid var(--c-border);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #4b5563;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--c-orange-light) !important;
        color: var(--c-orange) !important;
        border-bottom: 2px solid var(--c-orange) !important;
    }

    /* Clean Table Styling */
    .clean-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        margin-top: 10px;
    }
    .clean-table th {
        background: #111827;
        color: #ffffff;
        text-align: left;
        padding: 10px 14px;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .clean-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #e5e7eb;
        color: #1f2937;
    }
    .clean-table tr:hover {
        background-color: #f9fafb;
    }
    .clean-table tr.total-row {
        background-color: #f3f4f6;
        font-weight: 800;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_top_header(title: str, is_active: bool = True):
    """Renders clean uppercase module title with AI ACTIVE status badge."""
    badge_html = '<div class="ai-active-pill">● AI ACTIVE</div>' if is_active else '<div class="ai-active-pill" style="background:#4b5563;">OFFLINE</div>'
    st.markdown(
        f"""
        <div class="top-header-row">
            <h1 class="top-page-title">{title}</h1>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label: str,
    value: str,
    subtext: str = "",
    variant: str = "highlight",
):
    """Renders lightweight metric item."""
    sub_html = f'<div class="metric-sub-clean">{subtext}</div>' if subtext else ""
    st.markdown(
        f"""
        <div class="metric-item-clean {variant}">
            <div class="metric-label-clean">{label}</div>
            <div class="metric-val-clean">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_status_pill(status: str) -> str:
    """Returns HTML status pill tag."""
    s = str(status).lower()
    if "compliant" in s and "non" not in s and "minor" not in s:
        return f'<span class="tag-compliant">COMPLIANT</span>'
    elif "minor" in s or "caution" in s or "warning" in s:
        return f'<span class="tag-hazard" style="background:#f59e0b;">{status.upper()}</span>'
    else:
        return f'<span class="tag-critical">{status.upper()}</span>'


def render_download_json(data: Dict[str, Any], filename: str, button_label: str = "📥 EXPORT JSON REPORT"):
    """Renders formatted JSON download button."""
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    st.download_button(
        label=button_label,
        data=json_bytes,
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )
