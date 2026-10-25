"""
Site Safety & PPE Audit Module (Epic 2)
ConstructAI Lightweight UI Layout matching Reference Design.
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, Optional
from PIL import Image
import streamlit as st

from modules.gemini_client import GeminiMultimodalClient
from modules.ui_components import (
    get_status_pill,
    render_download_json,
    render_metric_card,
    render_top_header,
)

SAFETY_AUDIT_PROMPT = """
You are an expert Senior Construction Safety Auditor certified in OSHA (29 CFR 1926) and Indian Standards (IS 456:2000, IS 13415, IS 2925, IS 3521).
Analyze the provided construction site photograph with meticulous visual scrutiny.

Evaluate:
1. Worker PPE Compliance:
   - Helmets / Hard Hats (OSHA 1926.100 / IS 2925)
   - High-Visibility Vests / Retroreflective Apparel (OSHA 1926.201 / ANSI 107 / IS 15809)
   - Steel-Toe Safety Footwear (OSHA 1926.96 / IS 15298)
   - Fall Protection & Safety Harnesses (OSHA 1926.501 / IS 3521 for work > 1.8m / 6ft)
2. Construction Site Environmental Hazards:
   - Scaffolding & edge protection (guardrails, toe-boards, fall distance)
   - Uncapped vertical rebar dowels (IS 456 impalement hazard)
   - Slip/trip housekeeping, unprotected floor openings, unstable stacking

Return STRICT JSON ONLY conforming exactly to this structure without markdown fences:
{
  "safety_score": <integer between 0 and 100>,
  "overall_status": "<Compliant | Minor Violations | High Risk | Critical Risk>",
  "audit_timestamp": "<ISO timestamp>",
  "workers_detected_count": <integer>,
  "workers_compliant_count": <integer>,
  "standards_referenced": ["OSHA 29 CFR 1926.100", "OSHA 1926.501", "IS 456:2000", "IS 13415:1992"],
  "ppe_detection": [
    {
      "item": "Safety Helmets / Hard Hats",
      "standard": "OSHA 1926.100 / IS 2925",
      "required": true,
      "detected": true,
      "compliance_status": "<Compliant | Non-Compliant | Partial>",
      "compliance_rate": <percentage integer 0-100>,
      "details": "<observed details on workers>"
    },
    {
      "item": "High-Visibility Safety Vests",
      "standard": "OSHA 1926.201 / IS 15809",
      "required": true,
      "detected": true,
      "compliance_status": "<Compliant | Non-Compliant | Partial>",
      "compliance_rate": <percentage integer 0-100>,
      "details": "<observed details>"
    },
    {
      "item": "Steel-Toe Safety Boots",
      "standard": "OSHA 1926.96 / IS 15298",
      "required": true,
      "detected": true,
      "compliance_status": "<Compliant | Non-Compliant | Partial>",
      "compliance_rate": <percentage integer 0-100>,
      "details": "<observed details>"
    },
    {
      "item": "Fall Arrest Harness & Lanyard",
      "standard": "OSHA 1926.501 / IS 3521",
      "required": true,
      "detected": true,
      "compliance_status": "<Compliant | Non-Compliant | Partial>",
      "compliance_rate": <percentage integer 0-100>,
      "details": "<observed details>"
    }
  ],
  "identified_site_hazards": [
    {
      "hazard_id": "HAZ-001",
      "title": "<Concise hazard title>",
      "severity": "<Low | Medium | High | Critical>",
      "location": "<Specific location within frame>",
      "standard_violated": "<OSHA or IS code clause>",
      "risk_description": "<Technical risk explanation>",
      "corrective_remedy": "<Immediate OSHA/IS compliant corrective action>",
      "immediate_stop_work": <true | false>
    }
  ],
  "executive_summary": "<Professional summary of site safety condition>",
  "recommended_immediate_actions": [
    "<Action 1>",
    "<Action 2>"
  ]
}
"""


def get_mock_safety_audit(preset_key: str = "custom", observation_note: str = "") -> Dict[str, Any]:
    """Provides high-fidelity simulated PPE audit responses for demonstration mode."""
    now = datetime.now().isoformat()

    if "compliant" in preset_key.lower() or "compliant" in observation_note.lower():
        return {
            "safety_score": 96,
            "overall_status": "Compliant",
            "audit_timestamp": now,
            "workers_detected_count": 4,
            "workers_compliant_count": 4,
            "standards_referenced": [
                "OSHA 29 CFR 1926.100 (Head Protection)",
                "OSHA 29 CFR 1926.201 (Signaling & High-Vis)",
                "IS 2925:1984 (Helmets)",
                "IS 456:2000 (Safety Protocols in Concrete Construction)",
            ],
            "ppe_detection": [
                {
                    "item": "Safety Helmets / Hard Hats",
                    "standard": "OSHA 1926.100 / IS 2925",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "All 4 workers wearing certified Type 1 Class E safety helmets with chinstraps fastened.",
                },
                {
                    "item": "High-Visibility Safety Vests",
                    "standard": "OSHA 1926.201 / IS 15809",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "ANSI Class 3 fluorescent orange reflective vests worn by all personnel.",
                },
                {
                    "item": "Steel-Toe Safety Boots",
                    "standard": "OSHA 1926.96 / IS 15298",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "All personnel equipped with ankle-support steel-toe boots.",
                },
                {
                    "item": "Fall Arrest Harness & Lanyard",
                    "standard": "OSHA 1926.501 / IS 3521",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "Personnel stationed near perimeter secured to static lifeline with full-body harnesses.",
                },
            ],
            "identified_site_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "title": "Minor Concrete Dust Dispersion",
                    "severity": "Low",
                    "location": "Concrete bucket discharge zone",
                    "standard_violated": "OSHA 1926.1153 (Respirable Silica)",
                    "risk_description": "Transient particulate dust cloud during discharge.",
                    "corrective_remedy": "Ensure continuous water misting suppression and maintain N95/FFP2 respirator compliance.",
                    "immediate_stop_work": False,
                }
            ],
            "executive_summary": "EXCELLENT SAFETY COMPLIANCE. Site demonstrates adherence to OSHA 1926 and IS safety guidelines. 100% PPE compliance observed across all active crew members.",
            "recommended_immediate_actions": [
                "Maintain standard daily toolbox talk and hydration intervals.",
                "Verify weekly scaffold inspection tags remain signed and up to date.",
            ],
        }
    elif "scaffold" in preset_key.lower() or "harness" in observation_note.lower():
        return {
            "safety_score": 42,
            "overall_status": "Critical Risk",
            "audit_timestamp": now,
            "workers_detected_count": 3,
            "workers_compliant_count": 1,
            "standards_referenced": [
                "OSHA 29 CFR 1926.501 (Fall Protection)",
                "OSHA 29 CFR 1926.451 (Scaffolds)",
                "IS 13415:1992 (Safety Code for Scaffolds)",
                "IS 2925:1984 (Helmets)",
            ],
            "ppe_detection": [
                {
                    "item": "Safety Helmets / Hard Hats",
                    "standard": "OSHA 1926.100 / IS 2925",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Partial",
                    "compliance_rate": 66,
                    "details": "2 of 3 workers wearing helmets; 1 elevated worker wearing cloth cap.",
                },
                {
                    "item": "High-Visibility Safety Vests",
                    "standard": "OSHA 1926.201 / IS 15809",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Partial",
                    "compliance_rate": 66,
                    "details": "Class 2 retroreflective vest missing on primary scaffold operator.",
                },
                {
                    "item": "Steel-Toe Safety Boots",
                    "standard": "OSHA 1926.96 / IS 15298",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "All personnel equipped with heavy-duty construction safety boots.",
                },
                {
                    "item": "Fall Arrest Harness & Lanyard",
                    "standard": "OSHA 1926.501 / IS 3521",
                    "required": True,
                    "detected": False,
                    "compliance_status": "Non-Compliant",
                    "compliance_rate": 0,
                    "details": "Worker operating on cantilevered scaffold > 4.5m without body harness or tie-off.",
                },
            ],
            "identified_site_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "title": "Unanchored Scaffold Platform without Guardrail",
                    "severity": "Critical",
                    "location": "Upper exterior staging platform",
                    "standard_violated": "OSHA 1926.451(g)(1) & IS 13415 Clause 5.2",
                    "risk_description": "Scaffold deck lacks standard 42-inch top-rail, mid-rail, and toe-board; elevated personnel exposed to fatal fall risk.",
                    "corrective_remedy": "Issue immediate Stop-Work Order on scaffold bay. Install full perimeter guardrails and tether workers to certified 5,000 lbs anchor point via shock-absorbing lanyards.",
                    "immediate_stop_work": True,
                },
                {
                    "hazard_id": "HAZ-002",
                    "title": "Uncapped Vertical Starter Bars (Rebar Impalement Risk)",
                    "severity": "High",
                    "location": "Ground perimeter walkway beneath scaffold",
                    "standard_violated": "OSHA 1926.701(b) & IS 456 Safety Directives",
                    "risk_description": "Protruding steel rebars directly in pedestrian path without protective mushroom caps.",
                    "corrective_remedy": "Install steel-reinforced OSHA impalement caps or wooden trough covers over all exposed vertical bars.",
                    "immediate_stop_work": False,
                },
            ],
            "executive_summary": "CRITICAL NON-COMPLIANCE DETECTED. Immediate fall hazards identified on exterior scaffold platform violating both OSHA Subpart M and IS 13415. Work suspended on this quadrant until guardrails and fall arrest anchorage are commissioned.",
            "recommended_immediate_actions": [
                "Issue immediate red-tag stop-work on upper scaffold staging area.",
                "Mandate full body harnesses with dual self-retracting lifelines (SRLs).",
                "Install protective rebar impalement caps on ground-level starter dowels.",
            ],
        }
    else:
        return {
            "safety_score": 76,
            "overall_status": "Minor Violations",
            "audit_timestamp": now,
            "workers_detected_count": 3,
            "workers_compliant_count": 2,
            "standards_referenced": [
                "OSHA 29 CFR 1926.100",
                "OSHA 29 CFR 1926.201",
                "IS 456:2000 Section 3",
                "IS 2925:1984",
            ],
            "ppe_detection": [
                {
                    "item": "Safety Helmets / Hard Hats",
                    "standard": "OSHA 1926.100 / IS 2925",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "Hard hats present on all visible workers on the active deck.",
                },
                {
                    "item": "High-Visibility Safety Vests",
                    "standard": "OSHA 1926.201 / IS 15809",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Partial",
                    "compliance_rate": 66,
                    "details": "One operative vest unzipped; high visibility compromised.",
                },
                {
                    "item": "Steel-Toe Safety Boots",
                    "standard": "OSHA 1926.96 / IS 15298",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "Approved protective footwear observed.",
                },
                {
                    "item": "Fall Arrest Harness & Lanyard",
                    "standard": "OSHA 1926.501 / IS 3521",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Partial",
                    "compliance_rate": 60,
                    "details": "Harness worn but lanyard not 100% tied off during rebar tying.",
                },
            ],
            "identified_site_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "title": "Loose Timber & Rebar Off-Cuts (Housekeeping)",
                    "severity": "Medium",
                    "location": "Slab reinforcement grid pathway",
                    "standard_violated": "OSHA 1926.25 & IS 456 Guidelines",
                    "risk_description": "Cluttered working surface with binding wire coils and shuttering scrap presenting trip hazards.",
                    "corrective_remedy": "Deploy housekeeping crew to clear scrap material into designated disposal bins.",
                    "immediate_stop_work": False,
                }
            ],
            "executive_summary": "ACCEPTABLE BASELINE WITH MINOR HAZARDS. Fundamental PPE is utilized by workers, but housekeeping along the reinforcement grid and perimeter cable tension require immediate correction.",
            "recommended_immediate_actions": [
                "Enforce mandatory 100% tie-off policy within 2 meters of slab edge.",
                "Execute 15-minute mid-day housekeeping sweep across the active pour bay.",
            ],
        }


def render_safety_audit_tab(client: GeminiMultimodalClient):
    """Renders Tab 1 matching Reference UI layout."""
    render_top_header("SITE SAFETY MONITOR", is_active=client.is_live)

    col_left, col_right = st.columns([1, 1.25], gap="large")

    # LEFT CARD: INPUT DATA
    with col_left:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
                    📄 INPUT DATA
                </div>
            """,
            unsafe_allow_html=True,
        )

        obs_log = st.text_area(
            "Observation Log",
            placeholder="Describe the scene e.g. 'Workers on scaffold without harness near open floor edge...'",
            height=100,
            key="safety_obs_log",
        )

        st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#374151; margin-top:10px;'>Site Photo (Optional or Preset)</div>", unsafe_allow_html=True)
        img_source = st.radio(
            "Source Selection:",
            ["Preset Scenario Photos", "Upload Local Image (JPG/PNG)"],
            horizontal=True,
            label_visibility="collapsed",
            key="safety_source_radio",
        )

        image_to_analyze: Optional[Image.Image] = None
        preset_key = "custom"

        if img_source == "Preset Scenario Photos":
            preset_select = st.selectbox(
                "Choose Inspection Photo:",
                [
                    "🔴 Scaffold High-Elevation (Critical Fall Hazard)",
                    "🟢 Fully Compliant Structural Steel Crew",
                    "🟡 RCC Slab Pouring Deck (Housekeeping)",
                ],
                key="safety_preset_select_box",
            )
            if "Scaffold" in preset_select:
                preset_key = "hazard_scaffold"
                p_path = "assets/sample_scaffold_hazard.jpg"
            elif "Compliant" in preset_select:
                preset_key = "compliant_site"
                p_path = "assets/sample_site_compliant.jpg"
            else:
                preset_key = "custom"
                p_path = "assets/sample_rcc_deck.jpg"

            if os.path.exists(p_path):
                image_to_analyze = Image.open(p_path)
        else:
            uploaded = st.file_uploader(
                "Click to Upload Image",
                type=["jpg", "jpeg", "png"],
                key="safety_uploader_ref",
            )
            if uploaded is not None:
                image_to_analyze = Image.open(uploaded)
                preset_key = "custom"

        if image_to_analyze is not None:
            st.image(image_to_analyze, caption="Selected Site Photo", use_container_width=True)

        analyze_clicked = st.button("ANALYZE HAZARDS", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT CARD: ANALYSIS RESULTS
    with col_right:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:480px;">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    ANALYSIS RESULTS
                </div>
            """,
            unsafe_allow_html=True,
        )

        if analyze_clicked:
            img = image_to_analyze or Image.new("RGB", (600, 400), (40, 50, 60))
            full_prompt = f"{SAFETY_AUDIT_PROMPT}\nObservation Log Notes: {obs_log}"
            with st.spinner("Analyzing site imagery for OSHA/IS 456 compliance..."):
                audit_res, is_live, msg = client.analyze_image_json(
                    image=img,
                    prompt=full_prompt,
                    fallback_handler=get_mock_safety_audit,
                    preset_key=preset_key,
                    observation_note=obs_log,
                )
                st.session_state["safety_audit_res"] = audit_res

        if "safety_audit_res" in st.session_state:
            data = st.session_state["safety_audit_res"]
            score = data.get("safety_score", 0)
            status = data.get("overall_status", "Compliant")
            hazards = data.get("identified_site_hazards", [])
            ppe_list = data.get("ppe_detection", [])

            # Metrics Row
            m1, m2, m3 = st.columns(3)
            with m1:
                render_metric_card("SAFETY SCORE", f"{score}/100", f"Status: {status}", variant="highlight" if score < 80 else "green")
            with m2:
                render_metric_card("WORKERS FOUND", f"{data.get('workers_detected_count', 0)}", f"{data.get('workers_compliant_count', 0)} Compliant", variant="green")
            with m3:
                render_metric_card("SITE HAZARDS", f"{len(hazards)}", "OSHA / IS Standards", variant="highlight" if hazards else "green")

            # Briefing
            st.markdown(
                f"""
                <div style="background:#f9fafb; border-left:4px solid #ff6b00; padding:12px 14px; border-radius:4px; margin:14px 0; font-size:0.88rem; color:#374151;">
                    <strong>Executive Briefing:</strong> {data.get("executive_summary", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # PPE Checklist Matrix
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin:14px 0 8px 0;'>🛡️ PPE Compliance Matrix</div>", unsafe_allow_html=True)
            for ppe in ppe_list:
                p_item = ppe.get("item", "")
                p_stat = ppe.get("compliance_status", "Compliant")
                p_rate = ppe.get("compliance_rate", 100)
                p_pill = get_status_pill(p_stat)
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #f1f2f5; font-size:0.86rem;">
                        <div><strong>{p_item}</strong> <span style="color:#6b7280; font-size:0.78rem;">({p_rate}%)</span></div>
                        <div>{p_pill}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Hazards Matrix
            if hazards:
                st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin:16px 0 8px 0;'>⚠️ Identified Hazards & Corrective Remedies</div>", unsafe_allow_html=True)
                for h in hazards:
                    h_title = h.get("title", "")
                    h_sev = h.get("severity", "Medium")
                    h_rem = h.get("corrective_remedy", "")
                    h_std = h.get("standard_violated", "")
                    st.markdown(
                        f"""
                        <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:6px; padding:10px 14px; margin-bottom:8px; font-size:0.85rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <strong style="color:#9a3412;">{h_title}</strong>
                                <span class="tag-hazard" style="margin:0;">{h_sev}</span>
                            </div>
                            <div style="color:#6b7280; font-size:0.78rem; margin-bottom:4px;">Standard: {h_std}</div>
                            <div style="color:#374151;"><strong>Remedy:</strong> {h_rem}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Export
            st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
            render_download_json(data, "constructai_safety_audit.json", "📥 EXPORT JSON REPORT")

        else:
            st.markdown(
                """
                <div class="empty-state-box">
                    <div>Waiting for input...</div>
                    <div style="font-size:0.82rem; margin-top:6px; color:#adb5bd;">Select a photo or enter observation notes on the left and click 'ANALYZE HAZARDS'.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
