"""
Planning & Real Estate Valuation Module (Epic 3)
ConstructAI Lightweight UI Layout matching Reference Images 7 & 8.
"""

from datetime import datetime
import urllib.parse
from typing import Any, Dict, Optional, Tuple
import plotly.graph_objects as go
import streamlit as st

from modules.ui_components import render_download_json, render_metric_card, render_top_header

COST_BENCHMARKS = {
    "Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad)": {
        "Residential High-Rise (G+20)": {"base_const": 3200, "sales_rate": 12500, "land_comp": 6000, "steel_kg": 4.8, "cement_bags": 0.43},
        "Residential Mid-Rise (G+5)": {"base_const": 2600, "sales_rate": 9500, "land_comp": 4500, "steel_kg": 4.0, "cement_bags": 0.40},
        "Luxury Residential Villa (G+2)": {"base_const": 4200, "sales_rate": 16000, "land_comp": 8500, "steel_kg": 4.5, "cement_bags": 0.45},
        "Commercial Grade-A Office Complex": {"base_const": 3800, "sales_rate": 15000, "land_comp": 7000, "steel_kg": 5.2, "cement_bags": 0.46},
        "Industrial Warehouse / PEB Shed": {"base_const": 1900, "sales_rate": 5500, "land_comp": 2500, "steel_kg": 3.4, "cement_bags": 0.28},
    },
    "Tier 2 (Ahmedabad, Jaipur, Lucknow, Kochi, Pune)": {
        "Residential High-Rise (G+20)": {"base_const": 2600, "sales_rate": 7800, "land_comp": 3500, "steel_kg": 4.6, "cement_bags": 0.42},
        "Residential Mid-Rise (G+5)": {"base_const": 2100, "sales_rate": 6200, "land_comp": 2800, "steel_kg": 3.8, "cement_bags": 0.39},
        "Luxury Residential Villa (G+2)": {"base_const": 3400, "sales_rate": 10500, "land_comp": 5200, "steel_kg": 4.3, "cement_bags": 0.44},
        "Commercial Grade-A Office Complex": {"base_const": 3100, "sales_rate": 10000, "land_comp": 4500, "steel_kg": 4.9, "cement_bags": 0.44},
        "Industrial Warehouse / PEB Shed": {"base_const": 1600, "sales_rate": 4200, "land_comp": 1800, "steel_kg": 3.2, "cement_bags": 0.26},
    },
    "Tier 3 (Developing Urban Corridors)": {
        "Residential High-Rise (G+20)": {"base_const": 2100, "sales_rate": 5200, "land_comp": 2000, "steel_kg": 4.4, "cement_bags": 0.40},
        "Residential Mid-Rise (G+5)": {"base_const": 1750, "sales_rate": 4200, "land_comp": 1600, "steel_kg": 3.6, "cement_bags": 0.38},
        "Luxury Residential Villa (G+2)": {"base_const": 2700, "sales_rate": 7000, "land_comp": 3000, "steel_kg": 4.0, "cement_bags": 0.42},
        "Commercial Grade-A Office Complex": {"base_const": 2500, "sales_rate": 6800, "land_comp": 2700, "steel_kg": 4.6, "cement_bags": 0.42},
        "Industrial Warehouse / PEB Shed": {"base_const": 1350, "sales_rate": 3200, "land_comp": 1200, "steel_kg": 3.0, "cement_bags": 0.24},
    },
}

MILESTONES = [
    {"stage": "Excavation & Shoring", "min": 0, "max": 15, "duration": "45 Days"},
    {"stage": "Substructure & Foundation", "min": 15, "max": 30, "duration": "60 Days"},
    {"stage": "Superstructure RCC Frame", "min": 30, "max": 65, "duration": "120 Days"},
    {"stage": "Masonry, Plaster & MEP", "min": 65, "max": 85, "duration": "75 Days"},
    {"stage": "Finishing, Façade & Handover", "min": 85, "max": 100, "duration": "60 Days"},
]


def format_inr(amount_inr: float) -> str:
    """Formats amount in INR Crores or Lakhs."""
    if amount_inr >= 10_000_000:
        return f"₹{amount_inr / 10_000_000:.2f} Cr"
    elif amount_inr >= 100_000:
        return f"₹{amount_inr / 100_000:.2f} L"
    else:
        return f"₹{amount_inr:,.0f}"


def calculate_project_financials(
    sqft: float,
    structure_type: str,
    tier: str,
    completion_pct: float,
    quality: str = "Standard",
) -> Dict[str, Any]:
    """Calculates CapEx, material quantities, and valuation metrics."""
    benchmarks = COST_BENCHMARKS[tier][structure_type]
    q_lower = quality.lower()
    quality_mul = 1.22 if "premium" in q_lower else (1.55 if "luxury" in q_lower else 1.0)
    base_civil_rate = benchmarks["base_const"] * quality_mul
    total_civil_cost = sqft * base_civil_rate
    mep_cost = total_civil_cost * 0.18
    statutory_fees = total_civil_cost * 0.12
    total_capex = total_civil_cost + mep_cost + statutory_fees

    # S-curve expenditure
    p = completion_pct / 100.0
    s_factor = 3 * (p**2) - 2 * (p**3)
    capex_incurred = total_capex * s_factor
    capex_remaining = max(0.0, total_capex - capex_incurred)

    # Cost breakdown
    material_cost = total_capex * 0.58
    labour_cost = total_capex * 0.26
    finishing_cost = total_capex * 0.16

    # Market Valuation
    land_rate = benchmarks["land_comp"]
    land_component_value = sqft * land_rate
    sales_realization_rate = benchmarks["sales_rate"]
    total_completed_market_value = sqft * sales_realization_rate
    uncompleted_risk_discount = (1.0 - p) * 0.10
    completed_value_share = total_completed_market_value * p * (1.0 - uncompleted_risk_discount)
    current_asset_valuation = (land_component_value * (1.0 - p * 0.4)) + capex_incurred + completed_value_share * 0.65

    # Materials
    steel_kg = sqft * benchmarks["steel_kg"]
    cement_bags = sqft * benchmarks["cement_bags"]
    sand_tons = sqft * 0.045
    aggregate_tons = sqft * 0.065
    concrete_vol_m3 = sqft * 0.12

    # Active Milestone
    current_stage = MILESTONES[-1]
    for m in MILESTONES:
        if m["min"] <= completion_pct <= m["max"]:
            current_stage = m
            break

    return {
        "sqft": sqft,
        "structure_type": structure_type,
        "location_tier": tier,
        "completion_percentage": completion_pct,
        "total_capex": total_capex,
        "total_capex_budget_inr": total_capex,
        "capex_incurred": capex_incurred,
        "capex_incurred_inr": capex_incurred,
        "current_asset_valuation": current_asset_valuation,
        "current_asset_valuation_inr": current_asset_valuation,
        "completed_market_value": total_completed_market_value,
        "completed_market_value_inr": total_completed_market_value,
        "breakdown": {
            "materials_inr": material_cost,
            "labour_inr": labour_cost,
            "finishing_inr": finishing_cost,
            "total_inr": total_capex,
        },
        "materials": {
            "cement_bags": int(cement_bags),
            "cement_bags_50kg": int(cement_bags),
            "sand_tons": int(sand_tons),
            "sand_m_sand_cft": int(sand_tons * 22),
            "aggregate_tons": int(aggregate_tons),
            "coarse_aggregate_cft": int(aggregate_tons * 22),
            "steel_kg": int(steel_kg),
            "steel_metric_tonnes": round(steel_kg / 1000.0, 1),
            "concrete_vol_m3": int(concrete_vol_m3),
        },
        "active_milestone": current_stage,
    }


def generate_pollinations_prompt(
    structure_type: str,
    tier: str,
    style: str = "Modern",
    architectural_style: Optional[str] = None,
    lighting_time: str = "Clear Daylight",
    seed: int = 42,
) -> Tuple[str, str]:
    """Generates prompt and Pollinations URL."""
    eff_style = architectural_style or style
    city = "Mumbai / Bengaluru" if "Tier 1" in tier else "Contemporary Indian Urban Hub"
    prompt = f"3D architectural render of {structure_type} in {city}, {eff_style} architecture, during {lighting_time}, ultra-realistic, ArchDaily photography, 8k resolution"
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true&seed={seed}&model=flux"
    return prompt, url


def render_project_planner_tab():
    """Renders Tab 3 matching Reference Images 7 & 8."""
    render_top_header("CONSTRUCTION PROJECT PLANNER & REAL ESTATE VALUATION")

    sub_nav = st.radio(
        "Module View:",
        ["📋 Construction Project Planner (Materials & CapEx)", "🏢 Real Estate Estimator (Market Valuation)"],
        horizontal=True,
        key="planner_sub_nav",
    )

    if "Project Planner" in sub_nav:
        # PROJECT BRIEF CARD (Reference Image 8)
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:20px;">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:12px;">
                    PROJECT BRIEF
                </div>
            """,
            unsafe_allow_html=True,
        )

        b_col1, b_col2 = st.columns([3, 1], gap="medium")
        with b_col1:
            project_brief_text = st.text_input(
                "Project Scope / Description",
                value="Create structural plan and material takeoff for G+20 High-Rise in Bengaluru",
                label_visibility="collapsed",
                key="planner_brief_text",
            )
        with b_col2:
            gen_plan_clicked = st.button("GENERATE PLAN", type="primary", use_container_width=True)

        # Configuration Expandable parameters
        with st.expander("⚙️ Structure Type & Built-up Dimensions", expanded=True):
            p1, p2, p3 = st.columns(3)
            with p1:
                tier_keys = list(COST_BENCHMARKS.keys())
                sel_tier = st.selectbox("Location Tier:", tier_keys, index=0, key="plan_tier_box")
            with p2:
                struct_keys = list(COST_BENCHMARKS[sel_tier].keys())
                sel_struct = st.selectbox("Structure Type:", struct_keys, index=0, key="plan_struct_box")
            with p3:
                sqft_val = st.number_input("Built-up Area (sq ft):", min_value=1000, max_value=1_000_000, value=75000, step=5000, key="plan_sqft_box")

            comp_slider = st.slider("Construction Completion Progress (%):", min_value=0, max_value=100, value=45, format="%d%%", key="plan_comp_slider")

        st.markdown("</div>", unsafe_allow_html=True)

        fin_data = calculate_project_financials(sqft=sqft_val, structure_type=sel_struct, tier=sel_tier, completion_pct=comp_slider)

        # 3 Side-by-Side Cards matching Reference Image 8: Material Estimator, Cost Estimator, Time Schedule
        c_mat, c_cost, c_sched = st.columns(3, gap="medium")

        # CARD 1: MATERIAL ESTIMATOR
        with c_mat:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:360px;">
                    <div style="font-size:0.92rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:12px;">
                        MATERIAL ESTIMATOR
                    </div>
                """,
                unsafe_allow_html=True,
            )
            m = fin_data["materials"]
            st.markdown(
                f"""
                <table class="clean-table">
                    <thead><tr><th>ITEM</th><th>QTY</th></tr></thead>
                    <tbody>
                        <tr><td>Cement</td><td>{m['cement_bags']:,} bags</td></tr>
                        <tr><td>Sand</td><td>{m['sand_tons']:,} tons</td></tr>
                        <tr><td>Aggregate</td><td>{m['aggregate_tons']:,} tons</td></tr>
                        <tr><td>Steel</td><td>{m['steel_kg']:,} kg</td></tr>
                        <tr><td>Concrete Vol</td><td>{m['concrete_vol_m3']:,} m³</td></tr>
                    </tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # CARD 2: COST ESTIMATOR
        with c_cost:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:360px;">
                    <div style="font-size:0.92rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:12px;">
                        COST ESTIMATOR
                    </div>
                """,
                unsafe_allow_html=True,
            )
            b = fin_data["breakdown"]
            st.markdown(
                f"""
                <table class="clean-table">
                    <thead><tr><th>CATEGORY</th><th>COST</th></tr></thead>
                    <tbody>
                        <tr><td>Materials</td><td>{format_inr(b['materials_inr'])}</td></tr>
                        <tr><td>Labour</td><td>{format_inr(b['labour_inr'])}</td></tr>
                        <tr><td>Finishing & MEP</td><td>{format_inr(b['finishing_inr'])}</td></tr>
                        <tr class="total-row"><td>TOTAL CAPEX</td><td>{format_inr(b['total_inr'])}</td></tr>
                    </tbody>
                </table>
                <div style="margin-top:14px; font-size:0.82rem; color:#6b7280;">
                    Incurred @ {comp_slider}%: <strong style="color:#ff6b00;">{format_inr(fin_data['capex_incurred'])}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # CARD 3: TIME SCHEDULE
        with c_sched:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:360px;">
                    <div style="font-size:0.92rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:12px;">
                        TIME SCHEDULE
                    </div>
                """,
                unsafe_allow_html=True,
            )
            for m_item in MILESTONES:
                is_curr = m_item["min"] <= comp_slider <= m_item["max"]
                is_done = comp_slider > m_item["max"]
                dot = "🟢" if is_done else ("🟠" if is_curr else "⚪")
                st.markdown(
                    f"""
                    <div style="padding:6px 0; border-bottom:1px solid #f3f4f6; font-size:0.82rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span>{dot} <strong>{m_item['stage']}</strong></span>
                            <span style="color:#6b7280; font-size:0.75rem;">{m_item['duration']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # 3D Conceptual Render Section via Pollinations AI
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    🎨 CONCEPTUAL 3D ARCHITECTURAL RENDERING (POLLINATIONS AI)
                </div>
            """,
            unsafe_allow_html=True,
        )

        r_col1, r_col2 = st.columns([1, 1], gap="medium")
        with r_col1:
            render_style = st.selectbox(
                "Aesthetic Style:",
                ["Modern Biophilic Glass & Terraces", "Futuristic Minimalist Curtain Wall", "Contemporary Tropical Villa"],
                key="plan_render_style",
            )
            render_seed = st.number_input("Variation Seed:", value=108, step=1, key="plan_render_seed")
            prompt_str, render_url = generate_pollinations_prompt(sel_struct, sel_tier, render_style, seed=render_seed)
            gen_render_btn = st.button("RENDER 3D CONCEPT", type="primary", use_container_width=True)

        with r_col2:
            if gen_render_btn or "saved_render_url" in st.session_state:
                if gen_render_btn:
                    st.session_state["saved_render_url"] = render_url
                st.image(st.session_state.get("saved_render_url", render_url), caption=f"3D Concept: {sel_struct}", use_container_width=True)
            else:
                st.info("Click 'RENDER 3D CONCEPT' to generate visualization via Pollinations AI.")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # REAL ESTATE ESTIMATOR VIEW (Reference Image 7)
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:22px; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:20px;">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    PROPERTY DETAILS
                </div>
            """,
            unsafe_allow_html=True,
        )

        r_prop1, r_prop2 = st.columns([1, 1], gap="large")
        with r_prop1:
            loc_input = st.selectbox(
                "Location",
                list(COST_BENCHMARKS.keys()),
                key="re_loc_box",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                area_sqft = st.number_input("Area (sq ft)", value=25000, step=1000, key="re_area_box")
            with col_b:
                prop_age = st.number_input("Age / Completion %", value=100, min_value=0, max_value=100, key="re_age_box")

            prop_type = st.selectbox(
                "Type",
                list(COST_BENCHMARKS[loc_input].keys()),
                key="re_type_box",
            )
            amenities = st.text_input(
                "Amenities",
                value="Pool, Gym, Parking, Clubhouse, 24/7 Power Backup",
                placeholder="Pool, Gym, Parking...",
                key="re_amenities_box",
            )
            calc_val_btn = st.button("CALCULATE VALUE", type="primary", use_container_width=True)

        with r_prop2:
            st.markdown("<div style='font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;'>VALUATION SUMMARY</div>", unsafe_allow_html=True)
            val_data = calculate_project_financials(
                sqft=area_sqft,
                structure_type=prop_type,
                tier=loc_input,
                completion_pct=prop_age,
            )

            st.markdown(
                f"""
                <div style="background:#f9fafb; border:1px solid #e5e7eb; border-radius:6px; padding:18px;">
                    <div style="font-size:0.8rem; font-weight:700; color:#6b7280; text-transform:uppercase;">Estimated Market Asset Valuation</div>
                    <div style="font-size:2rem; font-weight:900; color:#ff6b00; margin:6px 0;">{format_inr(val_data['current_asset_valuation'])}</div>
                    <div style="font-size:0.82rem; color:#4b5563;">Gross Development Value (Completed): <strong>{format_inr(val_data['completed_market_value'])}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            render_metric_card("TOTAL CONSTRUCTION CAPEX", format_inr(val_data["total_capex"]), f"₹{COST_BENCHMARKS[loc_input][prop_type]['base_const']} / sqft base")

        st.markdown("</div>", unsafe_allow_html=True)

    # Export Report
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    all_data = calculate_project_financials(75000, "Residential High-Rise (G+20)", list(COST_BENCHMARKS.keys())[0], 50)
    render_download_json(all_data, "constructai_planning_valuation.json", "📥 EXPORT VALUATION LEDGER (JSON)")
