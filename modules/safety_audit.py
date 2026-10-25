"""
Site Safety & PPE Audit Module (Epic 2)
Analyzes worker PPE compliance and construction hazards under OSHA & IS 456/13415 standards.
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional
from PIL import Image
import streamlit as st

from modules.gemini_client import GeminiMultimodalClient
from modules.ui_components import (
    get_severity_badge,
    get_status_pill,
    render_download_json,
    render_metric_card,
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
   - Eye, Face & Hand Protection (OSHA 1926.102 / 1926.95 / IS 8521)
2. Construction Site Environmental Hazards:
   - Edge protection, guardrails, scaffolding integrity
   - Uncapped vertical rebar dowels (IS 456 impalement hazard)
   - Slip/trip housekeeping, unprotected floor openings, unstable stacking
   - Electrical wiring, wet surfaces, crane swing radiuses

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
      "details": "<observed details on anchorage and harness wear>"
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


def get_mock_safety_audit(preset_key: str = "custom") -> Dict[str, Any]:
    """Provides high-fidelity simulated PPE audit responses for demonstration mode."""
    now = datetime.now().isoformat()

    if preset_key == "hazard_scaffold":
        return {
            "safety_score": 42,
            "overall_status": "Critical Risk",
            "audit_timestamp": now,
            "workers_detected_count": 3,
            "workers_compliant_count": 1,
            "standards_referenced": [
                "OSHA 29 CFR 1926.501 (Fall Protection)",
                "OSHA 29 CFR 1926.451 (Scaffolds)",
                "IS 13415:1992 (Safety Code for Working on Scaffolds)",
                "IS 2925:1984 (Industrial Safety Helmets)",
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
                    "risk_description": "Scaffold working deck lacks standard 42-inch top-rail, mid-rail, and toe-board; elevated personnel exposed to fatal fall risk.",
                    "corrective_remedy": "Issue immediate Stop-Work Order on scaffold bay. Install full perimeter guardrails and ensure workers tether to certified 5,000 lbs anchor point via shock-absorbing lanyards.",
                    "immediate_stop_work": True,
                },
                {
                    "hazard_id": "HAZ-002",
                    "title": "Uncapped Vertical Starter Bars (Rebar Impalement Risk)",
                    "severity": "High",
                    "location": "Ground perimeter walkway beneath scaffold",
                    "standard_violated": "OSHA 1926.701(b) & IS 456:2000 Section 3 Safety Directives",
                    "risk_description": "Protruding steel rebars directly in pedestrian path without protective mushroom caps.",
                    "corrective_remedy": "Install steel-reinforced OSHA impalement caps or wooden trough covers over all exposed vertical bars.",
                    "immediate_stop_work": False,
                },
            ],
            "executive_summary": "CRITICAL NON-COMPLIANCE DETECTED. Immediate fall hazards identified on exterior scaffold platform violating both OSHA Subpart M and IS 13415. Work must be suspended on this quadrant until guardrails and fall arrest anchorage are commissioned.",
            "recommended_immediate_actions": [
                "Issue immediate red-tag stop-work on upper scaffold staging area.",
                "Mandate full body harnesses with dual self-retracting lifelines (SRLs).",
                "Install protective rebar impalement caps on ground-level starter dowels.",
            ],
        }
    elif preset_key == "compliant_site":
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
                    "details": "ANSI Class 3 fluorescent orange and yellow-green reflective vests worn by all personnel.",
                },
                {
                    "item": "Steel-Toe Safety Boots",
                    "standard": "OSHA 1926.96 / IS 15298",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "All personnel equipped with ankle-support steel-toe boots with puncture-resistant soles.",
                },
                {
                    "item": "Fall Arrest Harness & Lanyard",
                    "standard": "OSHA 1926.501 / IS 3521",
                    "required": True,
                    "detected": True,
                    "compliance_status": "Compliant",
                    "compliance_rate": 100,
                    "details": "Personnel stationed near floor perimeter secured to static lifeline with full-body harnesses.",
                },
            ],
            "identified_site_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "title": "Minor Concrete Dust Dispersion",
                    "severity": "Low",
                    "location": "Concrete bucket discharge zone",
                    "standard_violated": "OSHA 1926.1153 (Respirable Crystalline Silica)",
                    "risk_description": "Transient particulate dust cloud during hopper discharge.",
                    "corrective_remedy": "Ensure continuous water misting suppression and maintain N95/FFP2 respirator compliance during discharge.",
                    "immediate_stop_work": False,
                }
            ],
            "executive_summary": "EXCELLENT SAFETY COMPLIANCE. Site demonstrates adherence to OSHA 1926 and IS safety guidelines. 100% PPE compliance observed across all active crew members with certified fall arrest systems deployed.",
            "recommended_immediate_actions": [
                "Maintain standard daily toolbox talk and hydration intervals.",
                "Verify weekly scaffold inspection tags remain signed and up to date.",
            ],
        }
    else:  # Custom upload or moderate violation
        return {
            "safety_score": 78,
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
                    "details": "One operative vest obscured or unzipped; high visibility compromised.",
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
                    "details": "Harness worn but lanyard not 100% tied off during slab edge rebar tying.",
                },
            ],
            "identified_site_hazards": [
                {
                    "hazard_id": "HAZ-001",
                    "title": "Loose Timber & Rebar Off-Cuts (Housekeeping)",
                    "severity": "Medium",
                    "location": "Slab reinforcement grid pathway",
                    "standard_violated": "OSHA 1926.25 & IS 456 Guidelines",
                    "risk_description": "Cluttered working surface with binding wire coils and shuttering scrap presenting puncture and trip hazards.",
                    "corrective_remedy": "Deploy housekeeping crew to clear scrap material and store steel binding wire in dedicated disposal drums.",
                    "immediate_stop_work": False,
                },
                {
                    "hazard_id": "HAZ-002",
                    "title": "Perimeter Safety Cable Sag",
                    "severity": "Medium",
                    "location": "North slab boundary",
                    "standard_violated": "OSHA 1926.502(b)",
                    "risk_description": "Perimeter wire rope guardrail displays deflection exceeding 3 inches under tension test.",
                    "corrective_remedy": "Re-tension perimeter cable with turnbuckle to meet OSHA 200-lb outward force resistance standard.",
                    "immediate_stop_work": False,
                },
            ],
            "executive_summary": "ACCEPTABLE BASELINE WITH MINOR HAZARDS. Fundamental PPE is utilized by workers, but housekeeping along the reinforcement grid and perimeter cable tension require immediate engineering correction before concrete pour approval.",
            "recommended_immediate_actions": [
                "Re-tension slab edge safety wire rope before pour clearance.",
                "Enforce mandatory 100% tie-off policy within 2 meters of slab edge.",
                "Execute 15-minute mid-day housekeeping sweep across the active pour bay.",
            ],
        }


def render_safety_audit_tab(client: GeminiMultimodalClient):
    """Renders Tab 1: Site Safety & PPE Audit."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="color: #ffffff; margin-bottom: 4px;">🦺 Site Safety & Worker PPE Audit (OSHA / IS 456)</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Automated multimodal visual auditing of personal protective equipment, fall arrest compliance, and site hazards under OSHA 1926 & Bureau of Indian Standards (IS 456 / IS 13415 / IS 2925).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_input, col_view = st.columns([1, 1], gap="medium")

    with col_input:
        st.markdown("##### 1. Select Inspection Source")
        input_source = st.radio(
            "Image Input Mode:",
            ["Preset Inspection Scenarios", "Upload Site Photo (JPG/PNG)"],
            horizontal=True,
            key="safety_input_source",
        )

        image_to_analyze: Optional[Image.Image] = None
        preset_key = "custom"

        if input_source == "Preset Inspection Scenarios":
            preset_choice = st.selectbox(
                "Select Pre-configured Inspection Photo:",
                [
                    "🔴 Scenario 1: Scaffold Working at Height (Critical Fall Hazard)",
                    "🟢 Scenario 2: Heavy Steel Erection Crew (Fully Compliant)",
                    "🟡 Scenario 3: RCC Deck Pouring (Housekeeping & Minor Violations)",
                ],
                key="safety_preset_select",
            )
            if "Scenario 1" in preset_choice:
                preset_key = "hazard_scaffold"
                img_path = "assets/sample_scaffold_hazard.jpg"
            elif "Scenario 2" in preset_choice:
                preset_key = "compliant_site"
                img_path = "assets/sample_site_compliant.jpg"
            else:
                preset_key = "custom"
                img_path = "assets/sample_rcc_deck.jpg"

            if os.path.exists(img_path):
                image_to_analyze = Image.open(img_path)
            else:
                # Generate sample fallback image on the fly
                from modules.asset_generator import generate_sample_safety_image
                image_to_analyze = generate_sample_safety_image(preset_key)

        else:
            uploaded_file = st.file_uploader(
                "Upload Construction Site Photo",
                type=["jpg", "jpeg", "png"],
                help="Supported formats: JPG, PNG. Max size 20MB.",
                key="safety_file_uploader",
            )
            if uploaded_file is not None:
                image_to_analyze = Image.open(uploaded_file)
                preset_key = "custom"

        # Additional Audit Metadata
        with st.expander("⚙️ Audit Configuration & Standards", expanded=False):
            st.checkbox("OSHA 29 CFR 1926 Standard Enforcement", value=True, disabled=True)
            st.checkbox("IS 456:2000 & IS 13415 Indian Construction Codes", value=True, disabled=True)
            audit_zone = st.text_input("Site Zone / Block ID:", value="Tower B - Level 14 Slab Grid 3-C")

        run_audit_btn = st.button(
            "🔍 Run Multimodal Safety & PPE Audit",
            type="primary",
            use_container_width=True,
            disabled=(image_to_analyze is None),
        )

    with col_view:
        st.markdown("##### 2. Inspection Preview")
        if image_to_analyze is not None:
            st.image(image_to_analyze, caption="Active Site Inspection Image", use_container_width=True)
        else:
            st.info("👈 Please select a preset scenario or upload a construction site photo.")

    # Execution & Results Section
    if run_audit_btn and image_to_analyze is not None:
        with st.spinner("Analyzing site imagery for OSHA/IS 456 PPE compliance and structural hazards..."):
            audit_result, is_live, msg = client.analyze_image_json(
                image=image_to_analyze,
                prompt=SAFETY_AUDIT_PROMPT,
                fallback_handler=get_mock_safety_audit,
                preset_key=preset_key,
            )
            st.session_state["safety_audit_data"] = audit_result
            st.session_state["safety_audit_is_live"] = is_live
            st.session_state["safety_audit_msg"] = msg

    if "safety_audit_data" in st.session_state:
        data = st.session_state["safety_audit_data"]
        is_live = st.session_state.get("safety_audit_is_live", False)
        msg = st.session_state.get("safety_audit_msg", "")

        st.markdown("---")
        # System banner
        if is_live:
            st.success(f"⚡ {msg}")
        else:
            st.info(f"💡 {msg}")

        # Top Metric Cards
        score = data.get("safety_score", 0)
        status = data.get("overall_status", "Unknown")
        workers_count = data.get("workers_detected_count", 0)
        compliant_count = data.get("workers_compliant_count", 0)
        hazards = data.get("identified_site_hazards", [])
        critical_count = sum(1 for h in hazards if str(h.get("severity")).lower() == "critical")

        score_variant = "green" if score >= 85 else ("gold" if score >= 65 else "red")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Safety Compliance Score", f"{score} / 100", f"Status: {status}", variant=score_variant)
        with m2:
            compliance_pct = int((compliant_count / max(workers_count, 1)) * 100)
            render_metric_card("Worker Compliance", f"{compliant_count} / {workers_count}", f"{compliance_pct}% Adherence", variant="blue")
        with m3:
            hazard_variant = "red" if critical_count > 0 else "gold"
            render_metric_card("Site Hazards Detected", f"{len(hazards)}", f"{critical_count} Critical Violations", variant=hazard_variant)
        with m4:
            st.markdown(
                f"""
                <div class="metric-box blue">
                    <div class="metric-label">Audit Decision</div>
                    <div style="margin-top: 8px;">{get_status_pill(status)}</div>
                    <div class="metric-sub" style="margin-top: 10px;">OSHA & IS Standards</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Executive Summary Box
        st.markdown(
            f"""
            <div class="intel-card" style="border-left: 4px solid #38bdf8; margin-top: 16px;">
                <h4 style="margin: 0 0 8px 0; color: #38bdf8;">📋 Lead Safety Inspector Briefing</h4>
                <p style="margin: 0; color: #cbd5e1; font-size: 0.92rem; line-height: 1.5;">
                    {data.get("executive_summary", "Site inspection completed.")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # PPE Checklist Breakdown
        st.markdown("#### 🛡️ Detailed PPE Detection Matrix")
        ppe_items = data.get("ppe_detection", [])
        if ppe_items:
            for ppe in ppe_items:
                item_name = ppe.get("item", "Item")
                status = ppe.get("compliance_status", "Compliant")
                rate = ppe.get("compliance_rate", 100)
                std = ppe.get("standard", "")
                details = ppe.get("details", "")

                status_html = get_status_pill(status)
                st.markdown(
                    f"""
                    <div class="intel-card" style="padding: 12px 18px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">
                                {item_name} <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 400; margin-left: 8px;">({std})</span>
                            </div>
                            <div>{status_html}</div>
                        </div>
                        <div style="margin-top: 8px; font-size: 0.85rem; color: #94a3b8;">
                            <strong>Observation:</strong> {details} &bull; <span style="color: #38bdf8;">Compliance Rate: {rate}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Identified Site Hazards & Corrective Remedies
        st.markdown("#### ⚠️ Identified Site Hazards & Engineering Remedies")
        if hazards:
            for idx, haz in enumerate(hazards, 1):
                title = haz.get("title", f"Hazard #{idx}")
                sev = haz.get("severity", "Medium")
                location = haz.get("location", "Site Zone")
                violated_std = haz.get("standard_violated", "OSHA / IS Safety Standard")
                risk = haz.get("risk_description", "Potential safety hazard")
                remedy = haz.get("corrective_remedy", "Take corrective action")
                stop_work = haz.get("immediate_stop_work", False)

                border_color = "#ef4444" if sev.lower() == "critical" else ("#f97316" if sev.lower() == "high" else "#eab308")
                stop_work_tag = '<span style="background: #991b1b; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; margin-left: 8px;">STOP-WORK MANDATE</span>' if stop_work else ""

                st.markdown(
                    f"""
                    <div class="intel-card" style="border-left: 5px solid {border_color}; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <div style="font-weight: 700; font-size: 1rem; color: #ffffff;">
                                #{idx} {title} {stop_work_tag}
                            </div>
                            <div>{get_severity_badge(sev)}</div>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 8px;">
                            📍 <strong>Location:</strong> {location} &nbsp;|&nbsp; 📜 <strong>Standard:</strong> {violated_std}
                        </div>
                        <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 8px;">
                            <strong>Risk:</strong> {risk}
                        </div>
                        <div style="font-size: 0.88rem; color: #34d399; background: rgba(16, 185, 129, 0.08); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);">
                            🛠️ <strong>Corrective Remedy:</strong> {remedy}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("No active structural or environmental hazards detected in visual scan.")

        # Download Report & Raw JSON Section
        st.markdown("#### 📦 Audit Deliverables")
        col_dl, col_view_json = st.columns([1, 1])
        with col_dl:
            timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
            render_download_json(
                data=data,
                filename=f"safety_ppe_audit_report_{timestamp_slug}.json",
                button_label="📥 Export OSHA / IS 456 JSON Audit Report",
            )
        with col_view_json:
            with st.expander("🔍 Inspect Raw Structured JSON Schema", expanded=False):
                st.json(data)
