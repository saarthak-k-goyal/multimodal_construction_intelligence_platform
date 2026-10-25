"""
Daily Site Assistant & Weather-Aware Advisory Module (Epic 5)
ConstructAI Lightweight UI Layout matching Reference Images 3, 4, 5, 6, & 9.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import streamlit as st

from modules.gemini_client import GeminiMultimodalClient
from modules.ui_components import render_top_header

WEATHER_ADVISORIES = {
    "Cloudy / Overcast": {
        "status": "PROCEED WITH CAUTION",
        "alert_title": "PROCEED WITH CAUTION",
        "narrative": "Proceed with planned activities, but maintain heightened vigilance for sudden precipitation and prepare contingency weather sheeting.",
        "hazards": ["REDUCED VISIBILITY", "POTENTIAL SCATTERED SHOWERS", "INCREASED RISK OF SLIPPERY SURFACES"],
        "precautions": [
            "Ensure proper auxiliary task lighting on internal floors.",
            "Verify all temporary dewatering pumps are primed in basement pits.",
            "Keep waterproof tarpaulins staged immediately adjacent to active concrete bays.",
        ],
        "directives": [
            "Ensure proper auxiliary task lighting on internal floors.",
            "Verify all temporary dewatering pumps are primed in basement pits.",
            "Keep waterproof tarpaulins staged immediately adjacent to active concrete bays.",
        ],
        "crane_status": "🟡 Monitor wind and cloud ceiling; keep radio contact.",
    },
    "High Wind (> 45 km/h gusts)": {
        "status": "HALT CRANE & ELEVATED TRADES",
        "alert_title": "HALT CRANE & ELEVATED TRADES",
        "narrative": "High gust velocities exceed safe aerodynamic lifting limits. All tower crane jibs must be weather-vaned immediately.",
        "hazards": ["CRANE JIB TORSION OVERLOAD", "UNANCHORED FORMWORK DISLODGEMENT", "FALL FROM HEIGHT DISORIENTATION"],
        "precautions": [
            "Luff down and weather-vane all tower cranes (OSHA 1926.1431). Prohibit large sail-area panel hoisting.",
            "Inspect and secure all loose plywood, safety nets, and corrugated metal sheets on upper decks.",
            "Halt all exterior suspended cradle, glazing, and rope access trades.",
        ],
        "directives": [
            "Luff down and weather-vane all tower cranes (OSHA 1926.1431). Prohibit large sail-area panel hoisting.",
            "Inspect and secure all loose plywood, safety nets, and corrugated metal sheets on upper decks.",
            "Halt all exterior suspended cradle, glazing, and rope access trades.",
        ],
        "crane_status": "🔴 HALT ALL CRANE & HOIST OPERATIONS IMMEDIATELY",
    },
    "Heavy Rain / Monsoon Storm (> 50 mm/hr)": {
        "status": "HALT STRUCTURAL CONCRETE & EXCAVATIONS",
        "alert_title": "HALT STRUCTURAL CONCRETE & EXCAVATIONS",
        "narrative": "Severe precipitation alters the water-cement ratio, risking severe compressive strength failure. Deep trenches risk catastrophic sidewall collapse.",
        "hazards": ["CONCRETE WATER-CEMENT CONTAMINATION", "DEEP TRENCH LIQUEFACTION & COLLAPSE", "ELECTRICAL GROUND SHOCK FAULTS"],
        "precautions": [
            "Halt all un-sheltered structural concrete pouring immediately (IS 456 Clause 13.3).",
            "Continuous dewatering pumps must run in basement excavations to avoid hydraulic uplift.",
            "De-energize all outdoor 415V temporary power distribution panels; inspect GFCI trip threshold (< 30mA).",
        ],
        "directives": [
            "Halt all un-sheltered structural concrete pouring immediately (IS 456 Clause 13.3).",
            "Continuous dewatering pumps must run in basement excavations to avoid hydraulic uplift.",
            "De-energize all outdoor 415V temporary power distribution panels; inspect GFCI trip threshold (< 30mA).",
        ],
        "crane_status": "🔴 GROUND RESTRICTED; LIGHTNING SENSOR MONITORED",
    },
    "Extreme Heat (> 40°C ambient)": {
        "status": "HOT-WEATHER CONCRETING & WORKER ROTATION",
        "alert_title": "HOT-WEATHER CONCRETING & WORKER ROTATION",
        "narrative": "High temperatures accelerate moisture evaporation causing rapid slump loss and severe plastic shrinkage cracks.",
        "hazards": ["CONCRETE FLASH SETTING", "PLASTIC SHRINKAGE TENSILE CRACKING", "WORKER HEAT EXHAUSTION & STROKE"],
        "precautions": [
            "Use chilled batching water or crushed ice to keep concrete placement temperature below 32°C (ACI 305R / IS 456).",
            "Apply continuous wet burlap ponding or aliphatic alcohol evaporation retarders immediately after finishing.",
            "Mandate OSHA heat illness shifts: 15-minute shaded rest breaks every 60 minutes with electrolyte stations.",
        ],
        "directives": [
            "Use chilled batching water or crushed ice to keep concrete placement temperature below 32°C (ACI 305R / IS 456).",
            "Apply continuous wet burlap ponding or aliphatic alcohol evaporation retarders immediately after finishing.",
            "Mandate OSHA heat illness shifts: 15-minute shaded rest breaks every 60 minutes with electrolyte stations.",
        ],
        "crane_status": "🟢 OPERATIONAL WITH HYDRAULIC FLUID TEMP MONITORING",
    },
    "Normal / Favorable (24°C, Clear)": {
        "status": "OPTIMAL CONDITIONS - PROCEED ALL TRADES",
        "alert_title": "OPTIMAL CONDITIONS - PROCEED ALL TRADES",
        "narrative": "Weather conditions are fully within optimal engineering ranges. All scheduled structural and MEP trades are cleared for full production.",
        "hazards": ["STANDARD SITE OPERATIONAL RISKS", "HEAVY PLANT MOBILITY"],
        "precautions": [
            "Maintain standard 7-day moist curing for OPC concrete (IS 456 Clause 13.5).",
            "Conduct standard morning toolbox safety briefings.",
            "Verify all floor edge perimeter cables and rebar safety caps are secure.",
        ],
        "directives": [
            "Maintain standard 7-day moist curing for OPC concrete (IS 456 Clause 13.5).",
            "Conduct standard morning toolbox safety briefings.",
            "Verify all floor edge perimeter cables and rebar safety caps are secure.",
        ],
        "crane_status": "🟢 FULL HIGH-ELEVATION HOISTING CLEARED",
    },
}
WEATHER_PROTOCOLS = WEATHER_ADVISORIES

EXECUTION_PLANS = {
    "Concreting": {
        "tasks": [
            "Inspect shuttering alignment, prop verticality, and cover blocks before pour clearance.",
            "Conduct safety checks on transit mixers, concrete pump pipelines, and vibrators.",
            "Verify slump test (75-100 mm) and cast 6 compressive test cubes per 100 m³ (IS 516).",
            "Pour and vibrate concrete systematically in 300mm horizontal layers.",
            "Finish surface with wooden float; commence wet burlap curing as soon as initial set occurs.",
        ],
        "safety_checks": [
            "HARD HAT AND SAFETY VEST USAGE",
            "STEEL-TOED BOOTS AND HEAVY RUBBER GLOVES",
            "EYE PROTECTION AND DUST MASKS",
            "REGULAR INSPECTION OF PUMP PIPELINE CLAMPS",
        ],
        "risk_alerts": [
            "Risk of concrete segregation in high-drop pours without tremie pipe.",
            "Risk of formwork blowout under excess hydraulic concrete pressure.",
            "Risk of pump pipeline blockage or gasket rupture under high pumping pressure.",
        ],
    },
    "Formwork & Shuttering": {
        "tasks": [
            "Survey grid benchmarks and verify soffit levels with auto-level instrument.",
            "Erect heavy-duty steel props with base plates firmly bedded on unyielding subgrade.",
            "Fit plywood shuttering with tight joints to prevent slurry leakage during vibration.",
            "Apply approved mould release shuttering oil evenly across contact surfaces.",
        ],
        "safety_checks": [
            "100% FALL PROTECTION TETHERING ABOVE 1.8M",
            "SCAFFOLD STAGING PERIMETER GUARDRAILS",
            "CLEAN HOUSEKEEPING FREE OF NAILS AND TIMBER SCRAP",
            "CERTIFIED HOIST TACKLE FOR FLYING TABLE FORMS",
        ],
        "risk_alerts": [
            "Risk of prop buckling if bracing tubes are omitted.",
            "Risk of worker falls during shuttering placement at exterior slab boundaries.",
        ],
    },
    "Steel Reinforcement (Rebar)": {
        "tasks": [
            "Verify rebar mill test certificates (Fe500D TMT conforming to IS 1786).",
            "Cut, bend, and tie reinforcement bars per approved Bar Bending Schedule (BBS).",
            "Tie rebars securely with 16-gauge annealed GI binding wire at intersections.",
            "Place certified concrete cover blocks (40mm columns, 25mm beams, 20mm slabs) at 1-meter centers.",
        ],
        "safety_checks": [
            "CUT-RESISTANT LEATHER GLOVES",
            "PROTECTIVE MUSHROOM CAPS ON ALL VERTICAL DOWELS",
            "STABLE TIMBER WALKING RUNWAYS OVER REBAR GRIDS",
            "SAFETY GLASSES FOR REBAR CUTTING & BENDING TEAMS",
        ],
        "risk_alerts": [
            "Risk of impalement on uncapped starter dowels.",
            "Risk of pinch and crush injuries during heavy rebar bundle hoisting.",
        ],
    },
    "Deep Excavation & Shoring": {
        "tasks": [
            "Survey buried utilities (electric, water, gas) prior to mechanical excavator digging.",
            "Excavate in stepped benches conforming to soil angle of repose (OSHA 1926.652).",
            "Install soldier piles, timber lagging, or shotcrete with pre-stressed soil nails.",
            "Monitor piezometers and groundwater level in perimeter collection sumps.",
        ],
        "safety_checks": [
            "CONTINUOUS MONITORING OF PIT SHORING DEFLECTION",
            "DIVERSE SAFE EGRESS LADDERS EVERY 25 FEET",
            "TESTING FOR CONFINED SPACE HAZARDOUS GASES",
            "DEWATERING PUMP ELECTRICAL GROUNDING VERIFICATION",
        ],
        "risk_alerts": [
            "Risk of sudden trench wall sloughing or liquefaction after rain.",
            "Risk of excavator rollover near trench edge without stop-logs.",
        ],
    },
}


def get_demo_chatbot_response(user_query: str, current_weather: str = "Normal") -> str:
    """Answers construction queries with exact code clauses."""
    q = user_query.lower()
    if "curing" in q or "is 456" in q:
        return (
            "Under **IS 456:2000, Clause 13.5**:\n"
            "- **OPC Concrete:** Minimum moist curing period is **7 days** (10 days in dry/hot weather).\n"
            "- **Blended Cement (PPC/GGBS/Fly Ash):** Minimum **10 days** (14 days in hot weather).\n"
            "Ensure continuous ponding or wet burlap wrapping to prevent shrinkage micro-cracking."
        )
    elif "crane" in q or "wind" in q:
        return (
            "Under **OSHA 29 CFR 1926.1431**:\n"
            "- **Normal Lifts:** Permissible up to **38 - 45 km/h**.\n"
            "- **Large Surface Area Panels:** Restrict at **32 km/h**.\n"
            "- **Shutdown (> 50 km/h):** Lower hook block, position trolley at minimum radius, and release slewing brake for **360° free weather-vaning**."
        )
    elif "formwork" in q or "striking" in q:
        return (
            "Under **IS 456:2000, Clause 11.3 (Formwork Striking Times for OPC)**:\n"
            "- Vertical walls, columns, beam sides: **16 - 24 hours**\n"
            "- Slab soffits (props left underneath): **3 days**\n"
            "- Beam soffits (props left underneath): **7 days**\n"
            "- Props to slabs up to 4.5m span: **7 days** (over 4.5m: **14 days**)\n"
            "- Props to beams up to 6m span: **14 days** (over 6m: **21 days**)"
        )
    elif "power" in q or "overhead" in q or "clearance" in q:
        return (
            "Under **OSHA 29 CFR 1926.451(f)(6)** and **1926.1408**:\n"
            "- For uninsulated overhead power lines up to 50 kV: Minimum safety clearance is **10 feet (3.05 m)**.\n"
            "- For lines > 50 kV: Minimum clearance is 10 feet plus 0.4 inches for every 1 kV over 50 kV."
        )
    else:
        return (
            f"**Senior Site Engineer Advisory:**\n"
            f"For inquiry *\"{user_query}\"*:\n"
            "Ensure adherence to IS 456:2000 concrete quality standards and OSHA 1926 safety regulations. "
            "Verify all test cubes are cast in triplicate and recorded in the daily site engineering register."
        )


def render_site_assistant_tab(client: GeminiMultimodalClient):
    """Renders Tab 4 matching Reference Images 3, 4, 5, 6, & 9."""
    render_top_header("DAILY SITE ASSISTANT & WEATHER ADVISORY")

    view_choice = st.radio(
        "Select Tool:",
        [
            "📝 Daily Site Assistant (Execution Plan)",
            "⛅ Weather Advisor (Feasibility & Hazards)",
            "💬 Construction Chatbot",
            "📖 Knowledge Assistant",
        ],
        horizontal=True,
        key="site_view_radio",
    )

    if "Daily Site Assistant" in view_choice:
        # REFERENCE IMAGE 4: DAILY SITE ASSISTANT
        col_input, col_plan = st.columns([1, 1.25], gap="large")

        with col_input:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                        SITE INPUT
                    </div>
                """,
                unsafe_allow_html=True,
            )

            plan_act = st.selectbox(
                "Planned Activity",
                ["Concreting", "Formwork & Shuttering", "Steel Reinforcement (Rebar)", "Deep Excavation & Shoring"],
                key="daily_plan_act",
            )
            labour_cnt = st.number_input("Labour Count", value=18, min_value=1, max_value=500, key="daily_labour_cnt")
            site_cond = st.selectbox(
                "Site Condition",
                ["Normal", "High Wind", "Rainy / Damp", "Extreme Heat"],
                key="daily_site_cond",
            )

            gen_plan_btn = st.button("GENERATE TODAY'S PLAN", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_plan:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:450px;">
                    <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                        TODAY'S EXECUTION PLAN
                    </div>
                """,
                unsafe_allow_html=True,
            )

            p_data = EXECUTION_PLANS.get(plan_act, EXECUTION_PLANS["Concreting"])

            # TASKS
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#ff6b00; margin-bottom:8px;'>🔑 TASKS</div>", unsafe_allow_html=True)
            for t in p_data["tasks"]:
                st.markdown(f"- <span style='font-size:0.85rem; color:#374151;'>{t}</span>", unsafe_allow_html=True)

            # SAFETY CHECKS
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#0284c7; margin:16px 0 8px 0;'>🛡️ SAFETY CHECKS</div>", unsafe_allow_html=True)
            check_html = "".join([f'<span class="tag-check">{chk}</span>' for chk in p_data["safety_checks"]])
            st.markdown(f"<div>{check_html}</div>", unsafe_allow_html=True)

            # RISK ALERTS
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#dc2626; margin:16px 0 8px 0;'>⚠️ RISK ALERTS</div>", unsafe_allow_html=True)
            for r in p_data["risk_alerts"]:
                st.markdown(f"- <span style='font-size:0.85rem; color:#b91c1c;'>{r}</span>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    elif "Weather Advisor" in view_choice:
        # REFERENCE IMAGES 5 & 6: WEATHER ADVISOR
        col_w_in, col_w_res = st.columns([1, 1.25], gap="large")

        with col_w_in:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                        CHECK WEATHER IMPACT
                    </div>
                """,
                unsafe_allow_html=True,
            )

            w_act = st.text_input("Planned Activity", value="Slab Concrete Pouring", key="w_act_input")
            w_cond = st.selectbox(
                "Current/Forecast Weather",
                list(WEATHER_ADVISORIES.keys()),
                index=0,
                key="w_cond_select",
            )
            chk_feas_btn = st.button("CHECK FEASIBILITY", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_w_res:
            st.markdown(
                """
                <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:20px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:450px;">
                """,
                unsafe_allow_html=True,
            )
            adv = WEATHER_ADVISORIES[w_cond]
            status_color = "#ff6b00" if "CAUTION" in adv["status"] else ("#dc2626" if "HALT" in adv["status"] else "#16a34a")

            st.markdown(
                f"""
                <div style="font-size:1.45rem; font-weight:900; color:{status_color}; text-transform:uppercase; margin-bottom:8px;">
                    {adv['status']}
                </div>
                <div style="font-size:0.88rem; color:#4b5563; margin-bottom:16px;">
                    {adv['narrative']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # HAZARDS
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin-bottom:8px;'>HAZARDS</div>", unsafe_allow_html=True)
            haz_html = "".join([f'<span class="tag-hazard">{h}</span>' for h in adv["hazards"]])
            st.markdown(f"<div>{haz_html}</div>", unsafe_allow_html=True)

            # REQUIRED PRECAUTIONS
            st.markdown("<div style='font-weight:800; font-size:0.88rem; text-transform:uppercase; color:#111827; margin:16px 0 8px 0;'>REQUIRED PRECAUTIONS</div>", unsafe_allow_html=True)
            for pr in adv["precautions"]:
                st.markdown(f"- <span style='font-size:0.85rem; color:#374151;'>{pr}</span>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    elif "Chatbot" in view_choice:
        # REFERENCE IMAGE 3: CONSTRUCTION CHATBOT
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:22px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:500px;">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    CONSTRUCTION CHATBOT
                </div>
            """,
            unsafe_allow_html=True,
        )

        if "chatbot_messages" not in st.session_state:
            st.session_state["chatbot_messages"] = [
                {"role": "assistant", "content": "Hello! How can I assist you with your construction query today?"}
            ]

        # Chip Buttons matching Reference Image 3
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        with chip_col1:
            if st.button("ASK A QUESTION", use_container_width=True, key="chip_ask"):
                st.session_state["chip_query"] = "What is the minimum curing period for OPC concrete under IS 456:2000?"
        with chip_col2:
            if st.button("GET A CONSTRUCTION TIP", use_container_width=True, key="chip_tip"):
                st.session_state["chip_query"] = "Under what wind speed must tower crane operations be halted?"
        with chip_col3:
            if st.button("DISCUSS A PROJECT", use_container_width=True, key="chip_proj"):
                st.session_state["chip_query"] = "Provide checklist for slab shuttering de-staging and prop removal."

        # Display history
        for msg in st.session_state["chatbot_messages"]:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:flex-end; margin:10px 0;">
                        <div style="background:#ff6b00; color:#ffffff; padding:10px 16px; border-radius:18px 18px 4px 18px; font-size:0.88rem; max-width:75%;">
                            {msg['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:flex-start; margin:10px 0;">
                        <div style="background:#f3f4f6; color:#111827; padding:12px 18px; border-radius:18px 18px 18px 4px; font-size:0.88rem; max-width:80%; border:1px solid #e5e7eb;">
                            {msg['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        chat_input = st.chat_input("Type your question...", key="chat_user_input")
        send_query = st.session_state.pop("chip_query", None) or chat_input

        if send_query:
            st.session_state["chatbot_messages"].append({"role": "user", "content": send_query})

            def fallback_fn(messages, **kwargs):
                return get_demo_chatbot_response(send_query)

            reply, is_live, msg = client.chat_completion(
                messages=st.session_state["chatbot_messages"],
                system_instruction="You are an expert Senior Resident Construction & Structural Engineer certified in IS 456:2000 and OSHA 1926.",
                fallback_handler=fallback_fn,
            )
            st.session_state["chatbot_messages"].append({"role": "assistant", "content": reply})
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # REFERENCE IMAGE 9: KNOWLEDGE ASSISTANT
        st.markdown(
            """
            <div style="background:#ffffff; border:1px solid #e2e4e8; border-radius:6px; padding:22px; box-shadow:0 1px 3px rgba(0,0,0,0.04); min-height:480px;">
                <div style="font-size:0.95rem; font-weight:800; text-transform:uppercase; color:#111827; margin-bottom:14px;">
                    KNOWLEDGE ASSISTANT
                </div>
            """,
            unsafe_allow_html=True,
        )

        k_tag = st.radio("Category Tag:", ["SAFETY", "TECHNIQUE", "DOC GEN"], horizontal=True, key="k_tag_radio")
        k_query = st.text_area(
            "Knowledge Inquiry",
            value="e.g. Steps for scaffolding erection and tie-off under IS 13415",
            height=90,
            key="k_inquiry_text",
        )
        ask_expert_btn = st.button("ASK EXPERT", type="primary", use_container_width=True)

        if ask_expert_btn:
            with st.spinner("Retrieving civil engineering codal standards..."):
                resp = get_demo_chatbot_response(k_query)
                st.markdown(
                    f"""
                    <div style="background:#f9fafb; border-left:4px solid #ff6b00; padding:14px 18px; border-radius:4px; margin-top:16px; font-size:0.88rem; color:#1f2937;">
                        {resp}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)
