"""
Crack Diagnostics & Structural Integrity Module (Epic 2)
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

CRACK_DIAGNOSTICS_PROMPT = """
You are an expert Principal Forensic Structural Engineer certified under IS 456:2000, ACI 224R-01 (Control of Cracking in Concrete Structures), and EN 1504 (Concrete Repair Systems).
Examine the provided image of concrete / masonry / structural wall surface with diagnostic precision.

Classify the defect strictly into one of the following 5 engineering categories:
1. "Hairline Crack" (Plastic/drying shrinkage, crazing, surface micro-cracks)
2. "Settlement Crack" (Differential foundation shifting, diagonal stepping in masonry/concrete)
3. "Structural Shear Crack" (Diagonal 45-degree tensile shear failure under flexural or shear load, critical distress)
4. "Thermal Expansion Crack" (Cyclic temperature movement, missing expansion/control joints)
5. "Spalling & Rebar Delamination" (Carbonation, chloride corrosion, expanding rebar spalling cover concrete)

Measure and calculate:
- Estimated crack width in millimeters (mm)
- Root structural causes
- Recommended engineering repair methods (e.g., epoxy injection ASTM C881, structural re-grouting, CFRP wrap, polymer-modified mortar)
- Urgency level and IS 456:2000 Clause 35.3.2 crack width compliance check

Return STRICT JSON ONLY conforming exactly to this structure without markdown fences:
{
  "defect_type": "<Hairline Crack | Settlement Crack | Structural Shear Crack | Thermal Expansion Crack | Spalling & Rebar Delamination>",
  "confidence_score": <float between 0.0 and 1.0>,
  "estimated_width_mm": <float in mm, e.g. 0.25 or 3.8>,
  "depth_classification": "<Superficial (<5mm) | Sub-surface (5-20mm) | Deep / Through-Slab (>20mm)>",
  "structural_risk_level": "<Low | Medium | High | Critical>",
  "structural_integrity_score": <integer 0 to 100>,
  "urgency": "<Low | Medium | High | Critical>",
  "is_456_limit_state_violation": <true | false>,
  "is_456_permissible_limit_mm": 0.3,
  "affected_structural_element": "<Beam | Column | Slab | Retaining Wall | Masonry Shear Wall | Foundation Plinth>",
  "root_causes": [
    "<Primary root cause with geotechnical/structural mechanics>",
    "<Secondary contributing factor>"
  ],
  "recommended_repairs": [
    {
      "method": "<e.g. Low-Viscosity Epoxy Resin Pressure Injection (ASTM C881 Type IV)>",
      "material_specification": "<e.g. Solvent-free, high-modulus epoxy resin system>",
      "urgency_timeframe": "<e.g. Within 7 days / Immediate>",
      "estimated_cost_inr": "<e.g. ₹15,000 - ₹35,000>",
      "execution_steps": [
        "<Step 1: Clean crack surface using oil-free compressed air>",
        "<Step 2: Install injection ports at intervals equal to crack depth>",
        "<Step 3: Seal surface with fast-curing epoxy putty>",
        "<Step 4: Inject resin from lowest port until adjacent port discharges>"
      ]
    }
  ],
  "monitoring_protocol": "<Monitoring recommendation e.g. Avongard calibrated crack tell-tale gauge installation>",
  "forensic_summary": "<Professional structural diagnostic narrative for engineering records>"
}
"""


def get_mock_crack_diagnostics(preset_key: str = "shear", description_note: str = "") -> Dict[str, Any]:
    """Provides high-fidelity simulated structural crack diagnostics for demonstration mode."""
    d_lower = (preset_key + " " + description_note).lower()

    if "spalling" in d_lower or "rebar" in d_lower:
        return {
            "defect_type": "Spalling & Rebar Delamination",
            "confidence_score": 0.92,
            "estimated_width_mm": 8.5,
            "depth_classification": "Deep / Through-Slab (>20mm)",
            "structural_risk_level": "High",
            "structural_integrity_score": 48,
            "urgency": "High",
            "is_456_limit_state_violation": True,
            "is_456_permissible_limit_mm": 0.3,
            "affected_structural_element": "External RCC Column / Cantilever Beam",
            "root_causes": [
                "Atmospheric carbonation reducing concrete alkaline pH below 9, depassivating steel protective oxide layer.",
                "Inadequate concrete cover depth (< 20mm vs IS 456 specified 40mm for severe environmental exposure).",
                "Moisture ingress causing volumetric expansion of iron oxides, inducing tensile splitting and spalling.",
            ],
            "recommended_repairs": [
                {
                    "method": "Rebar Passivation & Polymer-Modified Structural Mortar (PMM) Patching",
                    "material_specification": "Zinc-rich epoxy primer (ASTM D520) + EN 1504 Class R4 repair mortar.",
                    "urgency_timeframe": "Within 14 days",
                    "estimated_cost_inr": "₹28,000 - ₹50,000",
                    "execution_steps": [
                        "Delaminate unsound concrete 25mm behind all exposed corroded reinforcement bars.",
                        "Mechanically wire-brush steel rebar to Sa 2.5 cleanliness standard.",
                        "Apply active zinc-rich anti-corrosion primer coating to rebar.",
                        "Apply epoxy bonding agent (ASTM C881 Type II) to concrete substrate.",
                        "Build up polymer-modified structural repair mortar in 25mm layers.",
                    ],
                }
            ],
            "monitoring_protocol": "Perform half-cell potential electrical survey (ASTM C876) across adjacent column spans.",
            "forensic_summary": "SEVERE DURABILITY DEGRADATION. Concrete delamination has exposed the longitudinal reinforcement rebars to direct environmental attack. Immediate rehabilitation with rebar passivation and EN 1504 R4 mortar required.",
        }
    elif "settlement" in d_lower or "foundation" in d_lower:
        return {
            "defect_type": "Settlement Crack",
            "confidence_score": 0.89,
            "estimated_width_mm": 4.8,
            "depth_classification": "Sub-surface (5-20mm)",
            "structural_risk_level": "High",
            "structural_integrity_score": 54,
            "urgency": "High",
            "is_456_limit_state_violation": True,
            "is_456_permissible_limit_mm": 0.3,
            "affected_structural_element": "Load-Bearing Brickwork & Plinth Tie Beam",
            "root_causes": [
                "Differential geotechnical settlement of corner footing due to localized soil moisture variation.",
                "Inadequate stiffness of foundation plinth beam unable to bridge localized subgrade settlement.",
            ],
            "recommended_repairs": [
                {
                    "method": "Helical Stitching & Non-Shrink Micro-Concrete Re-Grouting",
                    "material_specification": "Stainless steel 316 helical reinforcement ties with thixotropic cementitious bonding grout.",
                    "urgency_timeframe": "Within 21 days following geotechnical stabilization",
                    "estimated_cost_inr": "₹60,000 - ₹1,20,000",
                    "execution_steps": [
                        "Confirm geotechnical stabilization via soil core testing.",
                        "Rake out bed joints horizontally across crack line at 450mm vertical spacings.",
                        "Insert high-tensile helical ties bedded into high-strength non-shrink grout.",
                        "Pressure inject flexible cementitious grout into the core crack void.",
                    ],
                }
            ],
            "monitoring_protocol": "Affix digital crack displacement sensors with weekly data logger readings.",
            "forensic_summary": "DIFFERENTIAL SUBSIDENCE DETECTED. Stepped diagonal cracking extending through masonry joints indicates active differential movement. Soil stabilization and structural helical ties required.",
        }
    elif "hairline" in d_lower or "plaster" in d_lower:
        return {
            "defect_type": "Hairline Crack",
            "confidence_score": 0.95,
            "estimated_width_mm": 0.18,
            "depth_classification": "Superficial (<5mm)",
            "structural_risk_level": "Low",
            "structural_integrity_score": 92,
            "urgency": "Low",
            "is_456_limit_state_violation": False,
            "is_456_permissible_limit_mm": 0.3,
            "affected_structural_element": "Internal Wall Plaster / Suspended Slab Surface",
            "root_causes": [
                "Plastic shrinkage during early-stage curing due to rapid surface water evaporation.",
                "Rich cement-to-sand plaster ratio causing differential curing contraction.",
            ],
            "recommended_repairs": [
                {
                    "method": "Elastomeric Micro-Crack Bridging Coating",
                    "material_specification": "Flexible acrylic-based crack-bridging paint (> 300% elongation, ASTM C1305).",
                    "urgency_timeframe": "Routine cosmetic maintenance",
                    "estimated_cost_inr": "₹5,000 - ₹12,000",
                    "execution_steps": [
                        "Wash surface to remove loose plaster dust.",
                        "Apply penetrating acrylic primer.",
                        "Apply two coats of elastomeric crack-bridging exterior finish.",
                    ],
                }
            ],
            "monitoring_protocol": "Visual inspection during annual building maintenance audit.",
            "forensic_summary": "COSMETIC SUPERFICIAL CRACKING. Crack width of 0.18mm is well within the IS 456:2000 Clause 35.3.2 allowable threshold of 0.30mm for moderate exposure. Structural load capacity is 100% unimpaired.",
        }
    else:  # Structural shear crack
        return {
            "defect_type": "Structural Shear Crack",
            "confidence_score": 0.94,
            "estimated_width_mm": 3.6,
            "depth_classification": "Deep / Through-Slab (>20mm)",
            "structural_risk_level": "Critical",
            "structural_integrity_score": 38,
            "urgency": "Critical",
            "is_456_limit_state_violation": True,
            "is_456_permissible_limit_mm": 0.3,
            "affected_structural_element": "Reinforced Concrete Primary Transfer Beam",
            "root_causes": [
                "Principal diagonal tensile stresses exceeding shear capacity of concrete cross-section under excess superimposed load.",
                "Inadequate stirrup shear reinforcement spacing at high-shear zone near column junction (violating IS 456:2000 Clause 26.5.1.6).",
            ],
            "recommended_repairs": [
                {
                    "method": "Structural Low-Viscosity Epoxy Resin Pressure Injection & CFRP Wrap",
                    "material_specification": "ASTM C881 Type IV Grade 1 epoxy resin (> 70 N/mm² strength) + Bidirectional Carbon Fiber Fabric.",
                    "urgency_timeframe": "Immediate (Install emergency propping within 24 hours)",
                    "estimated_cost_inr": "₹45,000 - ₹85,000",
                    "execution_steps": [
                        "Erect temporary heavy-duty steel acrow props beneath beam span.",
                        "Mount surface injection ports at 150mm centers along crack line.",
                        "Seal perimeter with epoxy surface sealer gel; allow 4 hours curing time.",
                        "Pump structural epoxy starting from lowest port until consecutive port exudes resin.",
                        "Apply 2 layers of bidirectional CFRP composite fabric wrap around beam web.",
                    ],
                }
            ],
            "monitoring_protocol": "Install calibrated 2D mechanical crack monitor with digital caliper logging at 48-hour intervals.",
            "forensic_summary": "CRITICAL STRUCTURAL DEFECT. The 45° diagonal orientation originating near the beam-column interface signifies diagonal tension shear distress. Crack width of 3.6mm severely breaches the IS 456 limit of 0.3mm. Immediate shoring and high-pressure epoxy composite rehabilitation are mandatory.",
        }


def render_crack_diagnostics_tab(client: GeminiMultimodalClient):
    """Renders Tab 2 matching Reference UI layout."""
    render_top_header("STRUCTURAL CRACK DIAGNOSIS", is_active=client.is_live)

    col_left, col_right = st.columns([1, 1.25], gap="large")

    # LEFT CARD: INPUT ANALYSIS DATA
    with col_left:
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    INPUT ANALYSIS DATA
                </div>
            """,
            unsafe_allow_html=True,
        )

        desc_input = st.text_area(
            "Description",
            placeholder="Describe the crack location and pattern...",
            height=100,
            key="crack_desc_input",
        )

        st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#374151; margin-top:10px;'>Crack Image</div>", unsafe_allow_html=True)
        img_source = st.radio(
            "Image Source Selection:",
            ["Defect Scenario Library", "Upload Concrete Close-up"],
            horizontal=True,
            label_visibility="collapsed",
            key="crack_source_radio",
        )

        image_to_analyze: Optional[Image.Image] = None
        preset_key = "shear"

        if img_source == "Defect Scenario Library":
            preset_select = st.selectbox(
                "Choose Concrete Defect Case:",
                [
                    "🔴 45° Diagonal Structural Shear Crack (RC Beam)",
                    "🟠 Concrete Spalling & Corroded Rebar Delamination",
                    "🟠 Stepped Foundation Settlement Crack (Masonry)",
                    "🟢 Superficial Hairline Shrinkage Plaster Crack",
                ],
                key="crack_preset_select_box",
            )
            if "Shear" in preset_select:
                preset_key = "shear"
                p_path = "assets/sample_crack_shear.jpg"
            elif "Spalling" in preset_select:
                preset_key = "spalling"
                p_path = "assets/sample_crack_spalling.jpg"
            elif "Settlement" in preset_select:
                preset_key = "settlement"
                p_path = "assets/sample_crack_settlement.jpg"
            else:
                preset_key = "hairline"
                p_path = "assets/sample_crack_hairline.jpg"

            if os.path.exists(p_path):
                image_to_analyze = Image.open(p_path)
        else:
            uploaded = st.file_uploader(
                "Upload Close-up",
                type=["jpg", "jpeg", "png"],
                key="crack_uploader_ref",
            )
            if uploaded is not None:
                image_to_analyze = Image.open(uploaded)
                preset_key = "shear"

        if image_to_analyze is not None:
            st.image(image_to_analyze, caption="Concrete Surface", use_container_width=True)

        run_diag_clicked = st.button("RUN DIAGNOSIS", type="primary", use_container_width=True)
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

        if run_diag_clicked:
            img = image_to_analyze or Image.new("RGB", (600, 400), (140, 140, 140))
            full_prompt = f"{CRACK_DIAGNOSTICS_PROMPT}\nInspector Description: {desc_input}"
            with st.spinner("Analyzing concrete crack pathology and structural integrity..."):
                diag_res, is_live, msg = client.analyze_image_json(
                    image=img,
                    prompt=full_prompt,
                    fallback_handler=get_mock_crack_diagnostics,
                    preset_key=preset_key,
                    description_note=desc_input,
                )
                st.session_state["crack_diag_res"] = diag_res

        if "crack_diag_res" in st.session_state:
            data = st.session_state["crack_diag_res"]
            d_type = data.get("defect_type", "Defect")
            w_mm = data.get("estimated_width_mm", 0.0)
            score = data.get("structural_integrity_score", 100)
            urgency = data.get("urgency", "Low")
            violation = data.get("is_456_limit_state_violation", False)

            m1, m2, m3 = st.columns(3)
            with m1:
                render_metric_card("CLASSIFIED DEFECT", d_type, f"Urgency: {urgency}", variant="highlight")
            with m2:
                render_metric_card("ESTIMATED WIDTH", f"{w_mm:.2f} mm", "IS 456 Limit: 0.30 mm", variant="highlight" if w_mm > 0.3 else "green")
            with m3:
                render_metric_card("INTEGRITY SCORE", f"{score}/100", "Structural Health", variant="green" if score > 75 else "highlight")

            # IS 456 Alert
            if violation:
                st.markdown(
                    f"""
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px 14px; margin:12px 0; color:#991b1b; font-size:0.85rem;">
                        ⚠️ <strong>IS 456:2000 Clause 35.3.2 Limit State of Serviceability Violation:</strong> Crack width ({w_mm:.2f} mm) exceeds the maximum permissible limit of 0.30 mm for concrete durability.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Forensic Summary
            st.markdown(
                f"""
                <div style="background:#f9fafb; border-left:4px solid #ff6b00; padding:12px 14px; border-radius:4px; margin:12px 0; font-size:0.86rem; color:#374151;">
                    <strong>Diagnostic Findings:</strong> {data.get("forensic_summary", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Root Causes
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin:14px 0 6px 0;'>🔬 Root Causes</div>", unsafe_allow_html=True)
            for rc in data.get("root_causes", []):
                st.markdown(f"- <span style='font-size:0.85rem; color:#4b5563;'>{rc}</span>", unsafe_allow_html=True)

            # Recommended Engineering Repairs
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin:16px 0 8px 0;'>🛠️ Recommended Engineering Repairs</div>", unsafe_allow_html=True)
            for rep in data.get("recommended_repairs", []):
                method = rep.get("method", "")
                spec = rep.get("material_specification", "")
                cost = rep.get("estimated_cost_inr", "")
                st.markdown(
                    f"""
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:12px 14px; margin-bottom:8px; font-size:0.85rem;">
                        <strong style="color:#166534; font-size:0.92rem;">{method}</strong>
                        <div style="color:#4b5563; margin-top:4px;"><strong>Material:</strong> {spec}</div>
                        <div style="color:#15803d; margin-top:4px;"><strong>Est. Cost:</strong> {cost}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
            render_download_json(data, "constructai_structural_diagnostic.json", "📥 EXPORT DIAGNOSTIC REPORT")

        else:
            st.markdown(
                """
                <div class="empty-state-box">
                    <div>Waiting for input...</div>
                    <div style="font-size:0.82rem; margin-top:6px; color:#adb5bd;">Upload concrete surface or select a preset, then click 'RUN DIAGNOSIS'.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)
