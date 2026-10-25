"""
Crack Diagnostics & Structural Integrity Module (Epic 2)
Analyzes concrete defects, crack morphology, and recommends structural repairs under IS 456 & ACI 224R.
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
- Defect depth classification
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
  "structural_integrity_score": <integer 0 to 100, where 100 is pristine>,
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
      "material_specification": "<e.g. Solvent-free, high-modulus, low-viscosity epoxy resin system>",
      "urgency_timeframe": "<e.g. Within 7 days / Immediate / Routine maintenance>",
      "estimated_cost_inr": "<e.g. ₹15,000 - ₹35,000 per running meter>",
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


def get_mock_crack_diagnostics(preset_key: str = "shear") -> Dict[str, Any]:
    """Provides high-fidelity simulated structural crack diagnostics for demonstration mode."""
    if preset_key == "shear":
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
                "Principal diagonal tensile stresses exceeding shear capacity of concrete cross-section under excess superimposed dead/live load.",
                "Inadequate stirrup shear reinforcement spacing or curtailment at high-shear zone near column junction (violating IS 456:2000 Clause 26.5.1.6).",
                "Potential micro-settlement at adjacent beam support causing localized rotational torsion.",
            ],
            "recommended_repairs": [
                {
                    "method": "Structural Low-Viscosity Epoxy Resin Pressure Injection",
                    "material_specification": "High-strength, solvent-free epoxy resin conforming to ASTM C881 Type IV Grade 1, compressive strength > 70 N/mm².",
                    "urgency_timeframe": "Immediate (Install emergency propping within 24 hours)",
                    "estimated_cost_inr": "₹45,000 - ₹85,000 (including structural testing)",
                    "execution_steps": [
                        "Erect temporary heavy-duty steel acrow props beneath the beam span to relieve live load.",
                        "V-groove crack surface, clear dust with oil-free pneumatic air, and mount surface injection ports at 150mm centers.",
                        "Seal perimeter with epoxy surface sealer gel; allow 4 hours curing time.",
                        "Pump structural epoxy starting from lowest port until consecutive port exudes resin; plug and increment.",
                        "Post-cure retrofitting: Apply 2 layers of bidirectional Carbon Fiber Reinforced Polymer (CFRP) fabric wrap around beam web for shear capacity enhancement.",
                    ],
                }
            ],
            "monitoring_protocol": "Install calibrated 2D mechanical crack monitor (Avongard) with digital caliper logging at 48-hour intervals; perform ultrasonic pulse velocity (UPV) scan post-injection.",
            "forensic_summary": "CRITICAL STRUCTURAL DEFECT. The 45° diagonal orientation originating near the beam-column interface signifies classic diagonal tension shear distress. Crack width of 3.6mm severely breaches the IS 456 permissible threshold of 0.3mm. Structural capacity is compromised; immediate shoring and high-pressure epoxy composite rehabilitation are mandatory.",
        }
    elif preset_key == "spalling":
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
            "affected_structural_element": "External RCC Column / Cantilever Balcony Beam",
            "root_causes": [
                "Atmospheric carbonation reducing concrete alkaline pH below 9, depassivating steel protective oxide layer.",
                "Inadequate concrete cover depth (< 20mm vs IS 456 specified 40mm for severe environmental exposure).",
                "Moisture ingress causing volumetric expansion of iron oxides (rust expands 4-6x original steel volume), inducing tensile splitting and spalling.",
            ],
            "recommended_repairs": [
                {
                    "method": "Rebar Passivation & Polymer-Modified Structural Mortar (PMM) Patching",
                    "material_specification": "Zinc-rich epoxy primer (ASTM D520) + Two-component polymer-modified fibre-reinforced repair mortar conforming to EN 1504 Class R4.",
                    "urgency_timeframe": "Within 10 - 14 days to prevent rebar section loss",
                    "estimated_cost_inr": "₹28,000 - ₹50,000 per bay",
                    "execution_steps": [
                        "Delaminate and break back unsound concrete 25mm behind all exposed corroded reinforcement bars using light mechanical chisel.",
                        "Grit-blast or mechanically wire-brush steel rebar to Sa 2.5 cleanliness standard.",
                        "Apply active zinc-rich anti-corrosion primer coating to rebar within 4 hours.",
                        "Apply epoxy bonding agent (ASTM C881 Type II) to concrete substrate.",
                        "Build up polymer-modified structural repair mortar in 25mm layers; finish with elastomeric carbonation-resistant coating.",
                    ],
                }
            ],
            "monitoring_protocol": "Perform half-cell potential electrical survey (ASTM C876) across adjacent column spans to map hidden corrosion activity.",
            "forensic_summary": "SEVERE DURABILITY DEGRADATION. Concrete delamination has exposed the longitudinal reinforcement rebars to direct environmental attack. Cross-sectional steel area has suffered initial pitting corrosion. Rehabilitation with rebar passivation and EN 1504 R4 structural mortar must be executed before structural section loss escalates.",
        }
    elif preset_key == "settlement":
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
                "Differential geotechnical settlement of corner footing due to localized soil moisture variation or uncompacted sub-base fill.",
                "Inadequate stiffness of foundation plinth beam unable to bridge localized subgrade settlement.",
            ],
            "recommended_repairs": [
                {
                    "method": "Helical Stitching & Non-Shrink Micro-Concrete Re-Grouting",
                    "material_specification": "Austenitic stainless steel 316 helical reinforcement ties with thixotropic cementitious bonding grout + Polyurethane soil compaction grouting.",
                    "urgency_timeframe": "Within 21 days following geotechnical stabilization",
                    "estimated_cost_inr": "₹60,000 - ₹1,20,000",
                    "execution_steps": [
                        "Conduct geotechnical core sampling to confirm whether ground movement has stabilized.",
                        "Rake out bed joints horizontally across crack line at 450mm vertical spacings.",
                        "Insert high-tensile stainless steel helical ties bedded into high-strength non-shrink grout.",
                        "Pressure inject flexible cementitious grout into the core crack void.",
                    ],
                }
            ],
            "monitoring_protocol": "Affix digital crack displacement sensors with weekly data logger readings to ensure settlement has plateaued prior to permanent masonry stitching.",
            "forensic_summary": "DIFFERENTIAL SUBSIDENCE DETECTED. Stepped diagonal cracking extending through mortar bed joints and masonry units indicates active differential movement of the building's south-west quadrant. Soil stabilization and structural helical ties are required.",
        }
    elif preset_key == "thermal":
        return {
            "defect_type": "Thermal Expansion Crack",
            "confidence_score": 0.88,
            "estimated_width_mm": 1.8,
            "depth_classification": "Sub-surface (5-20mm)",
            "structural_risk_level": "Medium",
            "structural_integrity_score": 72,
            "urgency": "Medium",
            "is_456_limit_state_violation": True,
            "is_456_permissible_limit_mm": 0.3,
            "affected_structural_element": "Roof Parapet Wall & Terrace Slab Interface",
            "root_causes": [
                "Cyclic diurnal thermal differential between unprotected rooftop slab and shaded parapet wall.",
                "Absence of elastomeric expansion/movement joint at 30-meter structural interval (violating IS 3414 code of practice for design of joints in buildings).",
            ],
            "recommended_repairs": [
                {
                    "method": "Elastomeric Polysulphide Joint Sealing & Control Joint Induction",
                    "material_specification": "High-movement multi-component polysulphide sealant conforming to BS 4254 / ASTM C920 Class 25.",
                    "urgency_timeframe": "Within 30 days prior to next monsoon onset",
                    "estimated_cost_inr": "₹18,000 - ₹30,000",
                    "execution_steps": [
                        "Saw-cut a straight uniform 15mm wide x 20mm deep relief joint along the thermal crack line.",
                        "Clean joint thoroughly and install closed-cell polyethylene foam backer rod at 1:1 depth-to-width ratio.",
                        "Prime joint edges with polyurethane primer.",
                        "Gun-apply polysulphide elastomeric sealant flush with surface to absorb seasonal thermal expansion.",
                    ],
                }
            ],
            "monitoring_protocol": "Monitor joint movement through seasonal peak summer and winter cycles.",
            "forensic_summary": "NON-STRUCTURAL THERMAL STRAIN. Crack morphology is typical of thermal restraint stresses on long slab runs. While not an immediate collapse hazard, water ingress through this void will accelerate rebar corrosion if left unsealed.",
        }
    else:  # Hairline
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
                    "material_specification": "Flexible acrylic-based crack-bridging paint with > 300% elongation capacity conforming to ASTM C1305.",
                    "urgency_timeframe": "Routine cosmetic maintenance during painting cycle",
                    "estimated_cost_inr": "₹5,000 - ₹12,000",
                    "execution_steps": [
                        "Wash surface to remove efflorescence and loose plaster dust.",
                        "Apply penetrating acrylic primer.",
                        "Apply two coats of elastomeric crack-bridging exterior finish.",
                    ],
                }
            ],
            "monitoring_protocol": "Visual inspection during annual building maintenance audit.",
            "forensic_summary": "COSMETIC SUPERFICIAL CRACKING. Crack width of 0.18mm is well within the IS 456:2000 Clause 35.3.2 allowable threshold of 0.30mm for moderate environmental exposure. Structural load capacity is 100% unimpaired.",
        }


def render_crack_diagnostics_tab(client: GeminiMultimodalClient):
    """Renders Tab 2: Crack Diagnostics & Structural Integrity."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="color: #ffffff; margin-bottom: 4px;">🔬 AI Structural Crack Diagnostics & Forensic Pathology</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Defect classification (Hairline, Settlement, Structural Shear, Thermal, Spalling), width estimation (mm), root cause forensics, and engineering repair protocols under IS 456:2000 & ACI 224R.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_input, col_view = st.columns([1, 1], gap="medium")

    with col_input:
        st.markdown("##### 1. Select Inspection Surface")
        input_source = st.radio(
            "Defect Source:",
            ["Pre-calibrated Defect Library", "Upload Concrete Surface (JPG/PNG)"],
            horizontal=True,
            key="crack_input_source",
        )

        image_to_analyze: Optional[Image.Image] = None
        preset_key = "shear"

        if input_source == "Pre-calibrated Defect Library":
            defect_choice = st.selectbox(
                "Select Surface Pathology Case:",
                [
                    "🔴 45° Structural Shear Crack (RC Beam - Critical Distress)",
                    "🟠 Concrete Spalling with Exposed Corroded Rebar (Durability Failure)",
                    "🟠 Differential Settlement Stepped Crack (Masonry & Foundation)",
                    "🟡 Thermal Expansion & Movement Joint Failure (Terrace Slab)",
                    "🟢 Fine Hairline Plastic Shrinkage Crack (Plaster / Superstructure)",
                ],
                key="crack_preset_select",
            )
            if "Shear" in defect_choice:
                preset_key = "shear"
                img_path = "assets/sample_crack_shear.jpg"
            elif "Spalling" in defect_choice:
                preset_key = "spalling"
                img_path = "assets/sample_crack_spalling.jpg"
            elif "Settlement" in defect_choice:
                preset_key = "settlement"
                img_path = "assets/sample_crack_settlement.jpg"
            elif "Thermal" in defect_choice:
                preset_key = "thermal"
                img_path = "assets/sample_crack_thermal.jpg"
            else:
                preset_key = "hairline"
                img_path = "assets/sample_crack_hairline.jpg"

            if os.path.exists(img_path):
                image_to_analyze = Image.open(img_path)
            else:
                from modules.asset_generator import generate_sample_crack_image
                image_to_analyze = generate_sample_crack_image(preset_key)

        else:
            uploaded_file = st.file_uploader(
                "Upload Concrete / Wall Defect Photo",
                type=["jpg", "jpeg", "png"],
                help="High-resolution close-up photo with scale or reference surface recommended.",
                key="crack_file_uploader",
            )
            if uploaded_file is not None:
                image_to_analyze = Image.open(uploaded_file)
                preset_key = "shear"  # default fallback if demo

        # Engineering Parameters
        with st.expander("📐 Structural Member & Environment Setup", expanded=False):
            structural_element = st.selectbox(
                "Structural Member Type:",
                ["RC Beam (Flexural / Shear)", "RC Column (Axial)", "Suspended RC Slab", "Basement Retaining Wall", "Brick Masonry Wall"],
            )
            environmental_exposure = st.selectbox(
                "IS 456 Environmental Exposure Class:",
                ["Mild (Completely sheltered)", "Moderate (Sheltered from severe rain)", "Severe (Direct rain / Alternate wetting)", "Very Severe (Sea spray / Aggressive chemicals)"],
            )

        run_diag_btn = st.button(
            "🔬 Run Forensic Crack & Integrity Diagnostics",
            type="primary",
            use_container_width=True,
            disabled=(image_to_analyze is None),
        )

    with col_view:
        st.markdown("##### 2. Concrete Surface Preview")
        if image_to_analyze is not None:
            st.image(image_to_analyze, caption="Concrete Inspection Image", use_container_width=True)
        else:
            st.info("👈 Please select a pre-calibrated defect case or upload a concrete surface photo.")

    # Execution & Results Section
    if run_diag_btn and image_to_analyze is not None:
        with st.spinner("Executing computer vision crack width calibration & structural pathology analysis..."):
            diag_result, is_live, msg = client.analyze_image_json(
                image=image_to_analyze,
                prompt=CRACK_DIAGNOSTICS_PROMPT,
                fallback_handler=get_mock_crack_diagnostics,
                preset_key=preset_key,
            )
            st.session_state["crack_diag_data"] = diag_result
            st.session_state["crack_diag_is_live"] = is_live
            st.session_state["crack_diag_msg"] = msg

    if "crack_diag_data" in st.session_state:
        data = st.session_state["crack_diag_data"]
        is_live = st.session_state.get("crack_diag_is_live", False)
        msg = st.session_state.get("crack_diag_msg", "")

        st.markdown("---")
        if is_live:
            st.success(f"⚡ {msg}")
        else:
            st.info(f"💡 {msg}")

        # Metrics
        defect_type = data.get("defect_type", "Unknown")
        width_mm = data.get("estimated_width_mm", 0.0)
        integrity_score = data.get("structural_integrity_score", 100)
        urgency = data.get("urgency", "Low")
        risk_level = data.get("structural_risk_level", "Low")
        violation = data.get("is_456_limit_state_violation", False)

        int_variant = "green" if integrity_score >= 80 else ("gold" if integrity_score >= 50 else "red")
        width_variant = "red" if width_mm > 1.0 else ("gold" if width_mm > 0.3 else "green")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Classified Pathology", defect_type, f"Risk: {risk_level}", variant="blue")
        with m2:
            render_metric_card("Estimated Crack Width", f"{width_mm:.2f} mm", f"IS 456 Limit: 0.30 mm", variant=width_variant)
        with m3:
            render_metric_card("Structural Integrity Index", f"{integrity_score} / 100", f"Element Health", variant=int_variant)
        with m4:
            st.markdown(
                f"""
                <div class="metric-box red" style="border-left: 4px solid {'#ef4444' if 'crit' in urgency.lower() else ('#f97316' if 'high' in urgency.lower() else '#10b981')};">
                    <div class="metric-label">Repair Urgency</div>
                    <div style="margin-top: 8px;">{get_status_pill(urgency)}</div>
                    <div class="metric-sub" style="margin-top: 10px;">{'⚠️ Limit State Breached' if violation else '✅ Within IS 456 Limits'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # IS 456 Limit State Status Banner
        if violation:
            st.markdown(
                f"""
                <div class="weather-alert-card danger">
                    <h4 style="margin: 0 0 6px 0; color: #f87171;">⚠️ IS 456:2000 Clause 35.3.2 Limit State of Serviceability Violation</h4>
                    <p style="margin: 0; color: #fecaca; font-size: 0.88rem;">
                        Measured surface width of <strong>{width_mm:.2f} mm</strong> exceeds the maximum permissible limit of <strong>0.30 mm</strong> for concrete durability. Immediate remedial structural intervention is advised to avoid ingress of moisture, accelerated carbonation, and loss of flexural shear capacity.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Forensic Engineering Briefing
        st.markdown(
            f"""
            <div class="intel-card" style="border-left: 4px solid #f59e0b; margin-top: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #f59e0b;">🔍 Forensic Structural Pathology Findings</h4>
                <p style="margin: 0; color: #cbd5e1; font-size: 0.92rem; line-height: 1.55;">
                    {data.get("forensic_summary", "Diagnostic completed.")}
                </p>
                <div style="margin-top: 12px; font-size: 0.85rem; color: #94a3b8;">
                    <strong>Monitoring Protocol:</strong> {data.get("monitoring_protocol", "Standard visual observation")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Root Causes Analysis
        st.markdown("#### 🔬 Root Cause Engineering Breakdown")
        root_causes = data.get("root_causes", [])
        if root_causes:
            for idx, cause in enumerate(root_causes, 1):
                st.markdown(
                    f"""
                    <div class="intel-card" style="padding: 12px 18px; margin-bottom: 8px; border-left: 3px solid #38bdf8;">
                        <span style="color: #38bdf8; font-weight: 700; margin-right: 8px;">Cause #{idx}:</span>
                        <span style="color: #e2e8f0; font-size: 0.9rem;">{cause}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Recommended Engineering Repairs
        st.markdown("#### 🛠️ Recommended Engineering Repair & Retrofitting Protocol")
        repairs = data.get("recommended_repairs", [])
        if repairs:
            for idx, rep in enumerate(repairs, 1):
                method = rep.get("method", "Standard Repair")
                spec = rep.get("material_specification", "Industry standard materials")
                urgency_time = rep.get("urgency_timeframe", "Immediate")
                cost = rep.get("estimated_cost_inr", "Consult estimator")
                steps = rep.get("execution_steps", [])

                st.markdown(
                    f"""
                    <div class="intel-card" style="border-left: 5px solid #10b981; margin-bottom: 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #34d399;">#{idx} {method}</h4>
                            <span style="font-size: 0.82rem; font-weight: 700; color: #fbbf24; background: rgba(245, 158, 11, 0.15); padding: 4px 10px; border-radius: 6px;">
                                ⏱️ {urgency_time}
                            </span>
                        </div>
                        <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 8px;">
                            <strong>Material Specification:</strong> {spec}
                        </div>
                        <div style="font-size: 0.88rem; color: #38bdf8; margin-bottom: 12px;">
                            <strong>Estimated Repair Cost Range:</strong> {cost}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if steps:
                    with st.expander(f"📋 Step-by-Step Execution Sequence for {method}", expanded=True):
                        for s_idx, step in enumerate(steps, 1):
                            st.markdown(f"**Step {s_idx}:** {step}")

        # Download & JSON Inspect
        st.markdown("#### 📦 Inspection Certificate & Data")
        col_dl, col_view_json = st.columns([1, 1])
        with col_dl:
            timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
            render_download_json(
                data=data,
                filename=f"structural_crack_diagnostic_{timestamp_slug}.json",
                button_label="📥 Export Structural Diagnostic Report (JSON)",
            )
        with col_view_json:
            with st.expander("🔍 Inspect Full Diagnostic JSON Contract", expanded=False):
                st.json(data)
