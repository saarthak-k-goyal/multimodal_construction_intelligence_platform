"""
UI Components and Theme Styling Module
Provides modern industrial styling, metric cards, status pills, and interactive widgets.
"""

import json
from typing import Any, Dict, List, Optional
import streamlit as st


def inject_custom_css():
    """Injects high-end industrial engineering dark theme with safety accents."""
    custom_css = """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-main: #0b1120;
        --bg-card: #151e32;
        --bg-card-hover: #1e2942;
        --accent-amber: #f59e0b;
        --accent-orange: #f97316;
        --accent-blue: #38bdf8;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --border-color: #24324f;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }

    /* Top App Bar & Typography */
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Header Container */
    .platform-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    .platform-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #f59e0b, #f97316, #38bdf8, #10b981);
    }
    .platform-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin: 0 0 6px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .platform-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .platform-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Card styling */
    .intel-card {
        background-color: #151e32;
        border: 1px solid #24324f;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .intel-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 4px 20px -2px rgba(56, 189, 248, 0.15);
    }

    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 20px;
    }
    .metric-box {
        background: #151e32;
        border: 1px solid #24324f;
        border-radius: 10px;
        padding: 16px 18px;
        position: relative;
    }
    .metric-box.gold { border-left: 4px solid #f59e0b; }
    .metric-box.green { border-left: 4px solid #10b981; }
    .metric-box.blue { border-left: 4px solid #38bdf8; }
    .metric-box.red { border-left: 4px solid #ef4444; }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Status Pills */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .pill-compliant {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .pill-minor {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .pill-high {
        background: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.4);
    }
    .pill-critical {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Severity Badges */
    .badge-severity {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }
    .badge-low { background: #064e3b; color: #a7f3d0; }
    .badge-medium { background: #78350f; color: #fde68a; }
    .badge-high { background: #7c2d12; color: #fed7aa; }
    .badge-critical { background: #7f1d1d; color: #fecaca; }

    /* Weather Alert Box */
    .weather-alert-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #3b82f6;
        border-left: 6px solid #3b82f6;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .weather-alert-card.danger {
        border-color: #ef4444;
        border-left: 6px solid #ef4444;
    }
    .weather-alert-card.warning {
        border-color: #f59e0b;
        border-left: 6px solid #f59e0b;
    }

    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #f59e0b !important;
        border-bottom: 2px solid #f59e0b !important;
    }

    /* Sidebar aesthetics */
    [data-testid="stSidebar"] {
        background-color: #0d1424;
        border-right: 1px solid #1e293b;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_header():
    """Renders the top branding header for the platform."""
    st.markdown(
        """
        <div class="platform-header">
            <div class="platform-title">
                <span>🏗️ Multimodal Construction Intelligence Platform</span>
                <span class="platform-badge">CapStone Pro Edition</span>
            </div>
            <p class="platform-subtitle">
                Site Safety (OSHA & IS 456) • AI Structural Crack Diagnostics • Dynamic CapEx & Real Estate Valuation • Weather Site Advisory
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    label: str,
    value: str,
    subtext: str = "",
    variant: str = "gold",
    help_text: Optional[str] = None,
):
    """Renders a styled metric card."""
    subtext_html = f'<div class="metric-sub">{subtext}</div>' if subtext else ""
    html = f"""
    <div class="metric-box {variant}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {subtext_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def get_status_pill(status: str) -> str:
    """Returns HTML for a status pill badge."""
    s_lower = str(status).lower()
    if "compliant" in s_lower and "non" not in s_lower and "minor" not in s_lower:
        return f'<span class="pill pill-compliant">🟢 {status}</span>'
    elif "minor" in s_lower or "warning" in s_lower or "medium" in s_lower:
        return f'<span class="pill pill-minor">🟡 {status}</span>'
    elif "high" in s_lower:
        return f'<span class="pill pill-high">🟠 {status}</span>'
    else:
        return f'<span class="pill pill-critical">🔴 {status}</span>'


def get_severity_badge(severity: str) -> str:
    """Returns HTML for a severity badge."""
    sev = str(severity).lower()
    if "low" in sev:
        return '<span class="badge-severity badge-low">LOW</span>'
    elif "med" in sev:
        return '<span class="badge-severity badge-medium">MEDIUM</span>'
    elif "high" in sev:
        return '<span class="badge-severity badge-high">HIGH</span>'
    else:
        return '<span class="badge-severity badge-critical">CRITICAL</span>'


def render_download_json(data: Dict[str, Any], filename: str, button_label: str = "📥 Download JSON Report"):
    """Renders a standard Streamlit download button for formatted JSON."""
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    st.download_button(
        label=button_label,
        data=json_bytes,
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )
