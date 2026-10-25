"""
Planning & Real Estate Valuation Module (Epic 3)
Calculates CapEx, market asset valuation in INR, material takeoff metrics (Steel/Cement),
milestone S-curve progress, and 3D architectural rendering via Pollinations AI.
"""

from datetime import datetime
import urllib.parse
from typing import Any, Dict, Tuple
import plotly.graph_objects as go
import streamlit as st

from modules.ui_components import render_download_json, render_metric_card

# Benchmark Construction & Sales Rates per sqft in INR
COST_BENCHMARKS = {
    "Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad)": {
        "Residential High-Rise (G+20)": {"base_const": 3200, "sales_rate": 12500, "land_comp": 6000, "steel_kg": 4.8, "cement_bags": 0.43},
        "Residential Mid-Rise (G+5)": {"base_const": 2600, "sales_rate": 9500, "land_comp": 4500, "steel_kg": 4.0, "cement_bags": 0.40},
        "Luxury Residential Villa (G+2)": {"base_const": 4200, "sales_rate": 16000, "land_comp": 8500, "steel_kg": 4.5, "cement_bags": 0.45},
        "Commercial Grade-A Office Complex": {"base_const": 3800, "sales_rate": 15000, "land_comp": 7000, "steel_kg": 5.2, "cement_bags": 0.46},
        "Industrial Warehouse / PEB Shed": {"base_const": 1900, "sales_rate": 5500, "land_comp": 2500, "steel_kg": 3.4, "cement_bags": 0.28},
        "Mixed-Use Commercial & Retail Mall": {"base_const": 4100, "sales_rate": 18000, "land_comp": 9000, "steel_kg": 5.4, "cement_bags": 0.48},
    },
    "Tier 2 (Ahmedabad, Jaipur, Lucknow, Kochi, Pune)": {
        "Residential High-Rise (G+20)": {"base_const": 2600, "sales_rate": 7800, "land_comp": 3500, "steel_kg": 4.6, "cement_bags": 0.42},
        "Residential Mid-Rise (G+5)": {"base_const": 2100, "sales_rate": 6200, "land_comp": 2800, "steel_kg": 3.8, "cement_bags": 0.39},
        "Luxury Residential Villa (G+2)": {"base_const": 3400, "sales_rate": 10500, "land_comp": 5200, "steel_kg": 4.3, "cement_bags": 0.44},
        "Commercial Grade-A Office Complex": {"base_const": 3100, "sales_rate": 10000, "land_comp": 4500, "steel_kg": 4.9, "cement_bags": 0.44},
        "Industrial Warehouse / PEB Shed": {"base_const": 1600, "sales_rate": 4200, "land_comp": 1800, "steel_kg": 3.2, "cement_bags": 0.26},
        "Mixed-Use Commercial & Retail Mall": {"base_const": 3300, "sales_rate": 12000, "land_comp": 5800, "steel_kg": 5.1, "cement_bags": 0.46},
    },
    "Tier 3 (Developing Cities & Industrial Corridors)": {
        "Residential High-Rise (G+20)": {"base_const": 2100, "sales_rate": 5200, "land_comp": 2000, "steel_kg": 4.4, "cement_bags": 0.40},
        "Residential Mid-Rise (G+5)": {"base_const": 1750, "sales_rate": 4200, "land_comp": 1600, "steel_kg": 3.6, "cement_bags": 0.38},
        "Luxury Residential Villa (G+2)": {"base_const": 2700, "sales_rate": 7000, "land_comp": 3000, "steel_kg": 4.0, "cement_bags": 0.42},
        "Commercial Grade-A Office Complex": {"base_const": 2500, "sales_rate": 6800, "land_comp": 2700, "steel_kg": 4.6, "cement_bags": 0.42},
        "Industrial Warehouse / PEB Shed": {"base_const": 1350, "sales_rate": 3200, "land_comp": 1200, "steel_kg": 3.0, "cement_bags": 0.24},
        "Mixed-Use Commercial & Retail Mall": {"base_const": 2700, "sales_rate": 8200, "land_comp": 3500, "steel_kg": 4.8, "cement_bags": 0.44},
    },
}

QUALITY_MULTIPLIERS = {
    "Standard (CPWD Specifications)": 1.0,
    "Premium (Imported Finishes & Smart MEP)": 1.22,
    "Ultra-Luxury (Italian Marble, BMS & IGBC Platinum)": 1.55,
}

MILESTONES = [
    {"stage": "Excavation, Shoring & Piling", "min": 0, "max": 12, "desc": "Subgrade earthwork, retention piles, raft foundation prep."},
    {"stage": "Substructure & Plinth Level", "min": 12, "max": 25, "desc": "Basement retaining walls, waterproofing, plinth tie beams."},
    {"stage": "Superstructure RCC Frame", "min": 25, "max": 60, "desc": "Columns, shear walls, post-tensioned/RCC floor slabs."},
    {"stage": "Masonry, Plaster & MEP Rough-In", "min": 60, "max": 80, "desc": "AAC blockwork, conduit wiring, plumbing stacks, internal plaster."},
    {"stage": "Façade, Flooring & Interior Finishing", "min": 80, "max": 95, "desc": "Curtain walls, vitrified flooring, elevator installation, painting."},
    {"stage": "Commissioning, Snagging & RERA Handover", "min": 95, "max": 100, "desc": "Fire NOC, lift certification, occupancy certificate, final delivery."},
]


def format_inr(amount_inr: float) -> str:
    """Formats amount in Indian Rupees (Crores or Lakhs)."""
    if amount_inr >= 10_000_000:
        cr = amount_inr / 10_000_000
        return f"₹{cr:.2f} Cr"
    elif amount_inr >= 100_000:
        lakh = amount_inr / 100_000
        return f"₹{lakh:.2f} L"
    else:
        return f"₹{amount_inr:,.0f}"


def calculate_project_financials(
    sqft: float,
    structure_type: str,
    tier: str,
    quality: str,
    completion_pct: float,
) -> Dict[str, Any]:
    """Calculates comprehensive CapEx, material quantities, and asset valuation."""
    benchmarks = COST_BENCHMARKS[tier][structure_type]
    quality_mul = QUALITY_MULTIPLIERS[quality]

    # Construction CapEx components
    base_civil_rate = benchmarks["base_const"] * quality_mul
    total_civil_cost = sqft * base_civil_rate
    mep_cost = total_civil_cost * 0.18
    statutory_contingency = total_civil_cost * 0.12
    total_capex = total_civil_cost + mep_cost + statutory_contingency

    # S-curve expenditure profile: f(p) = 3p^2 - 2p^3
    p = completion_pct / 100.0
    s_factor = 3 * (p**2) - 2 * (p**3)
    capex_incurred = total_capex * s_factor
    capex_remaining = max(0.0, total_capex - capex_incurred)

    # Valuation Model
    land_rate = benchmarks["land_comp"]
    land_component_value = sqft * land_rate
    sales_realization_rate = benchmarks["sales_rate"] * quality_mul
    total_completed_market_value = sqft * sales_realization_rate

    # Current Asset Valuation (As-Is): Land + CapEx Incurred + Developer Margin * Completed Proportion
    uncompleted_risk_discount = (1.0 - p) * 0.10  # 10% risk margin on remaining works
    completed_value_share = total_completed_market_value * p * (1.0 - uncompleted_risk_discount)
    current_asset_valuation = (land_component_value * (1.0 - p * 0.5)) + capex_incurred + completed_value_share * 0.65

    # Materials Requirements (CPWD Civil Norms)
    steel_tonnes = (sqft * benchmarks["steel_kg"]) / 1000.0
    cement_bags = sqft * benchmarks["cement_bags"]
    cement_tonnes = (cement_bags * 50) / 1000.0
    coarse_aggregate_cft = sqft * 1.25
    sand_cft = sqft * 0.85
    water_kiloliters = (cement_bags * 135) / 1000.0  # ~135 Liters per bag

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
        "quality_specification": quality,
        "completion_percentage": completion_pct,
        "rate_per_sqft_inr": base_civil_rate,
        "total_capex_budget_inr": total_capex,
        "capex_incurred_inr": capex_incurred,
        "capex_remaining_inr": capex_remaining,
        "land_component_value_inr": land_component_value,
        "current_asset_valuation_inr": current_asset_valuation,
        "completed_market_value_inr": total_completed_market_value,
        "materials": {
            "steel_metric_tonnes": round(steel_tonnes, 1),
            "cement_bags_50kg": int(cement_bags),
            "cement_metric_tonnes": round(cement_tonnes, 1),
            "coarse_aggregate_cft": int(coarse_aggregate_cft),
            "sand_m_sand_cft": int(sand_cft),
            "construction_water_kl": int(water_kiloliters),
        },
        "active_milestone": current_stage,
    }


def generate_pollinations_prompt(
    structure_type: str,
    tier: str,
    architectural_style: str,
    lighting_time: str,
    seed: int = 42,
) -> Tuple[str, str]:
    """Generates an architectural rendering prompt and corresponding Pollinations AI image URL."""
    city = "Bengaluru"
    if "Tier 1" in tier:
        city = "Modern metropolitan Mumbai / Bengaluru"
    elif "Tier 2" in tier:
        city = "Contemporary Ahmedabad / Kochi"
    else:
        city = "Emerging Smart City"

    prompt = (
        f"Hyperrealistic 3D architectural rendering of a {structure_type} in {city}, "
        f"{architectural_style} style, during {lighting_time}. "
        f"Lush landscaping, detailed structural facades, volumetric lighting, photorealistic textures, "
        f"ultra-wide angle architectural photography, 8k resolution, Unreal Engine 5 render, ArchDaily award winner"
    )

    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed={seed}&model=flux"
    return prompt, image_url


def render_project_planner_tab():
    """Renders Tab 3: Planning, Real Estate Valuation & 3D Pollinations Render."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="color: #ffffff; margin-bottom: 4px;">📊 Project Planning, Real Estate Valuation & 3D Render (Epic 3)</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Dynamic CapEx estimation, S-curve expenditure tracking, market asset valuation in INR (Lakhs & Crores), structural material takeoff, and 3D architectural rendering via Pollinations AI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Input Controls Section
    with st.container():
        st.markdown("##### 🏗️ Project Configuration Parameters")
        c1, c2 = st.columns([1, 1])

        with c1:
            tier_options = list(COST_BENCHMARKS.keys())
            selected_tier = st.selectbox(
                "Geographic Location Tier (Indian Urban Markets):",
                tier_options,
                index=0,
                key="plan_tier",
            )
            structure_options = list(COST_BENCHMARKS[selected_tier].keys())
            selected_structure = st.selectbox(
                "Structural Typology:",
                structure_options,
                index=0,
                key="plan_structure",
            )
            built_up_sqft = st.number_input(
                "Total Built-Up Area (sq. ft.):",
                min_value=1000,
                max_value=2_000_000,
                value=85_000,
                step=5000,
                help="Enter total gross built-up area for the construction project.",
                key="plan_sqft",
            )

        with c2:
            quality_options = list(QUALITY_MULTIPLIERS.keys())
            selected_quality = st.selectbox(
                "Construction Specification & Quality Grade:",
                quality_options,
                index=1,
                key="plan_quality",
            )
            completion_pct = st.slider(
                "Current Construction Completion Progress (%):",
                min_value=0,
                max_value=100,
                value=45,
                step=1,
                format="%d%%",
                help="Slide to simulate financial expenditure along the project lifecycle S-curve.",
                key="plan_completion",
            )

            # Active Milestone Badge
            results = calculate_project_financials(
                sqft=built_up_sqft,
                structure_type=selected_structure,
                tier=selected_tier,
                quality=selected_quality,
                completion_pct=completion_pct,
            )
            active_stage = results["active_milestone"]
            st.markdown(
                f"""
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 10px 14px; margin-top: 10px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #38bdf8; font-weight: 700;">Active Milestone ({completion_pct}%)</div>
                    <div style="font-size: 0.92rem; font-weight: 700; color: #ffffff;">{active_stage['stage']}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">{active_stage['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Financial Metric Cards
    st.markdown("#### 💰 Financial Valuation & CapEx Incurred (INR)")
    f1, f2, f3, f4 = st.columns(4)

    total_capex = results["total_capex_budget_inr"]
    capex_incurred = results["capex_incurred_inr"]
    current_valuation = results["current_asset_valuation_inr"]
    completed_valuation = results["completed_market_value_inr"]

    with f1:
        render_metric_card(
            "Total Project CapEx Budget",
            format_inr(total_capex),
            f"Base: ₹{results['rate_per_sqft_inr']:,.0f} / sqft",
            variant="gold",
        )
    with f2:
        incurred_pct = int((capex_incurred / total_capex) * 100) if total_capex > 0 else 0
        render_metric_card(
            "Incurred CapEx (S-Curve)",
            format_inr(capex_incurred),
            f"{incurred_pct}% of Budget Disbursed",
            variant="blue",
        )
    with f3:
        render_metric_card(
            "Current Asset Valuation",
            format_inr(current_valuation),
            f"As-Is Market Value @ {completion_pct}%",
            variant="green",
        )
    with f4:
        render_metric_card(
            "Completed Asset Valuation",
            format_inr(completed_valuation),
            "Exit Gross Development Value",
            variant="gold",
        )

    # S-Curve Visual Chart & Milestone Tracker
    st.markdown("#### 📈 Construction S-Curve & Milestone Expenditure Schedule")
    chart_col, details_col = st.columns([1.6, 1], gap="medium")

    with chart_col:
        # Generate S-curve points
        pct_steps = list(range(0, 101, 5))
        planned_capex = [total_capex * (3 * ((p / 100.0) ** 2) - 2 * ((p / 100.0) ** 3)) / 10_000_000 for p in pct_steps]
        current_y = (capex_incurred) / 10_000_000

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=pct_steps,
                y=planned_capex,
                mode="lines",
                name="Planned CapEx S-Curve (₹ Cr)",
                line=dict(color="#38bdf8", width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[completion_pct],
                y=[current_y],
                mode="markers+text",
                name="Current Progress",
                text=[f"₹{current_y:.2f} Cr ({completion_pct}%)"],
                textposition="top left",
                marker=dict(color="#f59e0b", size=14, symbol="diamond"),
            )
        )
        fig.update_layout(
            paper_bgcolor="#151e32",
            plot_bgcolor="#111827",
            font=dict(color="#94a3b8"),
            xaxis=dict(title="Project Progress (%)", gridcolor="#1f293d", zeroline=False),
            yaxis=dict(title="CapEx Spent (₹ Crores)", gridcolor="#1f293d", zeroline=False),
            margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    with details_col:
        st.markdown(
            f"""
            <div class="intel-card" style="height: 320px; overflow-y: auto;">
                <h5 style="color: #f8fafc; margin-top: 0;">📋 Milestone Stage Ledger</h5>
                <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 12px;">
                    Progress tracked against Indian Construction Standard Milestones:
                </div>
            """,
            unsafe_allow_html=True,
        )
        for m in MILESTONES:
            is_active = m["min"] <= completion_pct <= m["max"]
            is_done = completion_pct > m["max"]
            color = "#10b981" if is_done else ("#f59e0b" if is_active else "#64748b")
            icon = "✅" if is_done else ("🔄" if is_active else "⏳")
            st.markdown(
                f"""
                <div style="border-left: 3px solid {color}; padding: 6px 10px; margin-bottom: 8px; background: rgba(255,255,255,0.02); border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 700; color: #ffffff;">
                        <span>{icon} {m['stage']}</span>
                        <span style="color: {color};">{m['min']}-{m['max']}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Material Takeoff Metrics (CPWD / IS 456 Structural Norms)
    st.markdown("#### 🏗️ Civil Engineering Material Takeoff Estimates (IS 456 / CPWD Norms)")
    mats = results["materials"]
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

    with m_col1:
        render_metric_card("Structural TMT Steel", f"{mats['steel_metric_tonnes']:,} MT", "Fe500D Rebars", variant="gold")
    with m_col2:
        render_metric_card("Cement Consumption", f"{mats['cement_bags_50kg']:,}", f"{mats['cement_metric_tonnes']:,} MT Total", variant="blue")
    with m_col3:
        render_metric_card("Coarse Aggregate", f"{mats['coarse_aggregate_cft']:,} cft", "20mm & 10mm Mix", variant="gold")
    with m_col4:
        render_metric_card("Manufactured Sand", f"{mats['sand_m_sand_cft']:,} cft", "Zone II Concrete Sand", variant="blue")
    with m_col5:
        render_metric_card("Curing Water", f"{mats['construction_water_kl']:,} KL", "Potable Batching Water", variant="green")

    st.markdown("---")

    # 3D Conceptual Architectural Rendering via Pollinations AI
    st.markdown("#### 🎨 Conceptual 3D Architectural Rendering (Pollinations AI Integration)")
    st.markdown(
        """
        <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 12px;">
            Generate high-fidelity architectural visualizations dynamically keyed to the structural typology, urban climate, and design aesthetics using Pollinations AI generative models.
        </p>
        """,
        unsafe_allow_html=True,
    )

    r_col1, r_col2 = st.columns([1, 1], gap="medium")

    with r_col1:
        arch_style = st.selectbox(
            "Architectural Design Style:",
            [
                "Biophilic Contemporary with Hanging Gardens",
                "Futuristic Parametric Glass & Titanium Curtain Wall",
                "Sleek Brutalist Minimalism with Exposed Formwork",
                "Indo-Modern Tropical High-Rise with Solar Louvers",
                "Industrial Modern Steel & Clearspan Glass",
            ],
            key="render_style",
        )
        lighting = st.selectbox(
            "Atmospheric Lighting & Environment:",
            [
                "Dramatic Golden Hour Sunset with Volumetric Sunlight",
                "Crisp Clear Midday Sky with Sharp Shadows",
                "Blue Hour Twilight with Illuminated Interiors",
                "Monsoon Overcast with Reflective Wet Pavement",
            ],
            key="render_light",
        )
        custom_seed = st.number_input("Generative Seed (Variation Control):", min_value=1, max_value=999999, value=108, step=1, key="render_seed")

        prompt_str, pollinations_url = generate_pollinations_prompt(
            structure_type=selected_structure,
            tier=selected_tier,
            architectural_style=arch_style,
            lighting_time=lighting,
            seed=custom_seed,
        )

        with st.expander("📝 Inspect Architectural Prompt & API Endpoint", expanded=False):
            st.code(prompt_str, language="text")
            st.code(pollinations_url, language="text")

        generate_render_btn = st.button("🖼️ Render 3D Architectural Concept", type="primary", use_container_width=True)

    with r_col2:
        if generate_render_btn or "render_url" in st.session_state:
            if generate_render_btn:
                st.session_state["render_url"] = pollinations_url
                st.session_state["render_prompt"] = prompt_str

            display_url = st.session_state.get("render_url", pollinations_url)
            st.image(
                display_url,
                caption=f"Conceptual 3D Visualization: {selected_structure}",
                use_container_width=True,
            )
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 8px;">
                    <a href="{display_url}" target="_blank" style="color: #38bdf8; font-size: 0.85rem; text-decoration: none; font-weight: 600;">
                        🔗 Open Full-Resolution 8K Image in New Tab
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Click 'Render 3D Architectural Concept' to generate photorealistic visualization via Pollinations AI.")

    # Export Financial & Project Plan JSON
    st.markdown("#### 📦 Export Planning & Valuation Ledger")
    c_dl, c_json = st.columns([1, 1])
    with c_dl:
        timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        render_download_json(
            data=results,
            filename=f"project_planning_valuation_{timestamp_slug}.json",
            button_label="📥 Export Full Project Valuation & Material Takeoff JSON",
        )
    with c_json:
        with st.expander("🔍 Inspect Financial Model JSON Ledger", expanded=False):
            st.json(results)
