"""
Daily Site Assistant & Weather-Aware Advisory Module (Epic 5)
Provides real-time dynamic weather safety protocols and multi-turn construction engineering chatbot.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import streamlit as st

from modules.gemini_client import GeminiMultimodalClient

WEATHER_PROTOCOLS = {
    "High Wind (> 45 km/h gusts)": {
        "status_color": "danger",
        "badge": "CRITICAL WIND ADVISORY",
        "alert_title": "Severe Gale Warning - Tower Crane & Scaffold Shutdown",
        "crane_status": "🔴 SUSPEND ALL CRANE & HOIST OPERATIONS",
        "scaffold_status": "🔴 PROHIBIT WORK ON SUSPENDED CRADLES & UNANCHORED PLATFORMS",
        "concrete_status": "🟡 MAINTAIN RAPID CURING COMPOUND TO PREVENT DRYING SHRINKAGE",
        "directives": [
            "Luff down and weather-vane all tower crane jibs immediately (OSHA 1926.1431). Prohibit lifting loads with high surface areas.",
            "Inspect and secure all loose corrugated metal sheeting, plywood shuttering, and hollow-core blocks on upper floors.",
            "Halt all exterior façade glazing, suspended rope access, and cradle operations immediately.",
            "Tether external staging and check guy-wire tensions on communications masts and temp hoists.",
        ],
        "standards_cited": ["OSHA 29 CFR 1926.1431", "IS 13415:1992", "ASCE 7-22 Wind Load Provisions"],
    },
    "Heavy Rain / Monsoon Storm (> 50 mm/hr)": {
        "status_color": "danger",
        "badge": "FLOOD & ELECTRICAL HAZARD",
        "alert_title": "Heavy Precipitation - Deep Pit Collapse & Wet Shoring Risk",
        "crane_status": "🟡 GROUND LIFTS RESTRICTED; LIGHTNING SENSOR MONITORED",
        "scaffold_status": "🔴 HALT METAL SCAFFOLD WORK DURING LIGHTNING & RAIN",
        "concrete_status": "🔴 HALT STRUCTURAL CONCRETE POURING IMMEDIATELY",
        "directives": [
            "Halt all structural concrete pouring unless pour bay is completely sheltered under water-tight tarpaulin; rainwater will alter water-cement ratio and destroy compressive strength (IS 456 Clause 13.3).",
            "Continuous dewatering pumps must be deployed in deep basement excavations to prevent hydraulic uplift and trench sidewall sloughing.",
            "Inspect trench shoring and soil retaining piles for saturation subsidence before allowing worker entry (OSHA 1926.651).",
            "De-energize all temporary 415V distribution boxes in open areas; verify GFCI/ELCB trip sensitivity (< 30mA).",
        ],
        "standards_cited": ["IS 456:2000 Clause 13.3", "OSHA 1926 Subpart P (Excavations)", "IS 3764:1992 (Excavation Safety)"],
    },
    "Extreme Heat (> 40°C ambient)": {
        "status_color": "warning",
        "badge": "HEAT STRESS & FLASH-SET ADVISORY",
        "alert_title": "High Ambient Heat - Concrete Flash Set & Worker Heat Stroke Prevention",
        "crane_status": "🟢 OPERATIONAL WITH HYDRAULIC FLUID TEMP MONITORING",
        "scaffold_status": "🟡 ROTATE CREWS; SHADED REST STATIONS MANDATORY",
        "concrete_status": "🟡 HOT-WEATHER CONCRETING PROTOCOL (ACI 305R / IS 456)",
        "directives": [
            "Hot-weather concreting protocols in force: Use chilled batching water or flaked ice to maintain fresh concrete placement temperature below 32°C (IS 456 Clause 14.1).",
            "Apply aliphatic alcohol evaporation retarders or continuous wet burlap ponding immediately behind screeding to prevent plastic shrinkage cracking.",
            "Mandate OSHA heat illness prevention protocol: 15-minute shaded rest breaks every 60 minutes with electrolyte water stations for all reinforcement and formwork crews.",
            "Stagger shift timings: Shift high-exertion structural casting to early morning (05:00 - 10:00) or night shifts.",
        ],
        "standards_cited": ["ACI 305R-20 (Guide to Hot Weather Concreting)", "IS 456:2000 Clause 14", "OSHA Heat Illness Standard"],
    },
    "Normal / Favorable (24°C, Clear, 12 km/h)": {
        "status_color": "success",
        "badge": "OPTIMAL SITE OPERATIONS",
        "alert_title": "Optimal Production Window - All Trades Cleared",
        "crane_status": "🟢 FULL HIGH-ELEVATION HOISTING CLEARED",
        "scaffold_status": "🟢 ALL SUSPENDED & EXTERIOR TRADES PERMITTED",
        "concrete_status": "🟢 PRIME CONCRETING CONDITIONS (STANDARD CURING)",
        "directives": [
            "Maintain standard 7-day wet burlap curing for OPC concrete, and 10-day for blended mineral admixtures (IS 456 Clause 13.5).",
            "Proceed with planned major concrete slab pours and tower crane tandem lifts.",
            "Conduct routine morning toolbox talks and review permit-to-work (PTW) logs for hot-works and confined spaces.",
            "Standard PPE enforcement: Hard hats, Class 2 high-vis vests, steel-toe boots, and safety glasses.",
        ],
        "standards_cited": ["IS 456:2000 Clause 13.5", "OSHA 1926 General Safety"],
    },
    "Cold Weather / Frost (< 5°C)": {
        "status_color": "warning",
        "badge": "COLD WEATHER CONCRETING",
        "alert_title": "Low Temperature Warning - Hydration Stagnation & Frost Heave",
        "crane_status": "🟢 NORMAL OPERATION WITH WIRE ROPE DE-ICING",
        "scaffold_status": "🟡 INSPECT PLANKS FOR SLIPPERY FROST / ICE COATING",
        "concrete_status": "🟡 COLD WEATHER CONCRETING PROTOCOL (ACI 306R)",
        "directives": [
            "Never place concrete on frozen ground or icy formwork; heat aggregate and mixing water to ensure fresh concrete temperature does not fall below 10°C during placement (IS 456 Clause 14.2).",
            "Maintain thermal insulating curing blankets (R-value > 4) over freshly poured slabs for minimum 72 hours to prevent frost damage during early-age hydration.",
            "Extend formwork striking periods by 50% to accommodate delayed concrete strength gain under low temperatures (IS 456 Clause 11.3).",
        ],
        "standards_cited": ["ACI 306R-16 (Cold Weather Concreting)", "IS 456:2000 Clause 11.3 & 14.2"],
    },
    "High Humidity & Fog (> 85% RH)": {
        "status_color": "warning",
        "badge": "LOW VISIBILITY & SLIP HAZARD",
        "alert_title": "Dense Fog / Dew - Hoisting Blind Spots & Painting Suspension",
        "crane_status": "🟡 CRANE BLIND-HOISTING REQUIRES CERTIFIED RADIO SIGNALMAN",
        "scaffold_status": "🟡 INSPECT FOR SLIPPERY STEEL TUBING & RUNWAYS",
        "concrete_status": "🟢 EXCELLENT MOISTURE RETENTION FOR CONCRETE CURING",
        "directives": [
            "Tower crane blind lifts strictly require calibrated two-way UHF radio communication with certified banksman/signalman at pick and drop locations.",
            "Suspend all exterior spray painting, epoxy coatings, and waterproofing membranes as substrate moisture will cause blistering and adhesion failure.",
            "Inspect scaffold decking and rebar walking mats for slippery condensation; require anti-slip footwear.",
        ],
        "standards_cited": ["OSHA 1926.1419 (Signals)", "SSPC-PA 1 (Surface Coatings)"],
    },
}

CIVIL_ENGINEERING_SYSTEM_INSTRUCTION = """
You are the Senior Resident Civil & Structural Engineer on a large-scale commercial/residential construction project.
You possess deep expertise in:
- Indian Standards: IS 456:2000 (Concrete), IS 13415 (Scaffolds), IS 1893 (Seismic Design), IS 875 (Design Loads), IS 3764 (Excavation)
- International Standards: OSHA 29 CFR 1926 (Construction Safety), ACI 318, ACI 305R/306R, Eurocode 2
- Project planning, CapEx forecasting, formwork de-shuttering schedules, concrete mix design, and non-destructive testing (UPV, Rebound Hammer)

Instructions:
- Provide clear, highly technical, actionable engineering guidance.
- Cite specific code clauses (e.g. IS 456:2000 Clause 11.3 for formwork striking times).
- Integrate the active site weather condition into your safety and engineering recommendations.
- Format responses cleanly with bullet points, bold key terms, and concise checklists.
"""


def get_demo_chatbot_response(user_query: str, current_weather: str) -> str:
    """Provides high-fidelity civil engineering answers for demonstration mode."""
    q = user_query.lower()

    if "curing" in q or "is 456" in q and "opc" in q:
        return (
            "### ⏱️ Minimum Curing Periods under IS 456:2000 (Clause 13.5)\n\n"
            "Under Indian Standard **IS 456:2000, Clause 13.5**, the mandatory minimum moist curing periods are:\n\n"
            "1. **Ordinary Portland Cement (OPC 33 / 43 / 53 Grade):**\n"
            "   - **Normal / Moderate Weather:** Minimum **7 days** of continuous moist curing.\n"
            "   - **Hot & Dry Weather (< 50% RH, > 35°C):** Minimum **10 days** of continuous moist curing.\n\n"
            "2. **Mineral Admixtures / Blended Cements (PPC, GGBS, Fly Ash):**\n"
            "   - **Standard Weather:** Minimum **10 days**.\n"
            "   - **Hot / Dry Weather:** Minimum **14 days**.\n\n"
            f"> 📍 *Active Site Weather Note ({current_weather}):* Ensure continuous ponding or wet hessian wrapping to avoid premature moisture evaporation and tensile micro-cracks."
        )

    elif "wind" in q or "crane" in q:
        return (
            "### 🏗️ Tower Crane Operation & Wind Thresholds (OSHA & IS Codes)\n\n"
            "Under **OSHA 29 CFR 1926.1431** and standard manufacturer load-chart regulations (FEM 1.001):\n\n"
            "- **Maximum Permissible Wind Speed for Normal Lifts:** Typically **38 to 45 km/h (20 to 24 knots / 11-12 m/s)**.\n"
            "- **Large Surface Area / Panel Lifts (Formwork, Glazing):** Restrict operations at **32 km/h (8.9 m/s)** due to wind sail drag.\n"
            "- **Mandatory Shutdown & Out-of-Service Protocol (> 50 km/h or Gusts > 55 km/h):**\n"
            "  1. Lower hook block to top limit under jib.\n"
            "  2. Position trolley at minimum radius near mast.\n"
            "  3. Release slewing brake to enable **360° free weather-vaning** (avoids severe torsional boom buckling).\n"
            "  4. Cut main electrical isolator."
        )

    elif "power" in q or "clearance" in q or "overhead" in q:
        return (
            "### ⚡ OSHA Electrical Clearances for Scaffolding & Cranes\n\n"
            "Under **OSHA 29 CFR 1926.451(f)(6)** and **1926.1408**:\n\n"
            "- **Insulated Lines < 300 Volts:** Minimum clearance of **3 feet (0.9 meters)**.\n"
            "- **Insulated Lines 300V to 50 kV:** Minimum clearance of **10 feet (3.0 meters)**.\n"
            "- **Lines > 50 kV (e.g. 33 kV / 66 kV / 132 kV Transmission):**\n"
            "  - Formula: **10 feet + 0.4 inches for every 1 kV over 50 kV**.\n"
            "  - For standard 33 kV uninsulated lines: Minimum safety clearance is **10 feet (3.05 m)**; recommended engineering clearance is **15 feet (4.57 m)**.\n\n"
            "⚠️ *Mandatory Site Action:* Request utility line sleeving / de-energization or install physical non-conductive timber goalposts (warning barriers)."
        )

    elif "de-shuttering" in q or "striking" in q or "formwork" in q:
        return (
            "### 📋 IS 456:2000 Clause 11.3 - Formwork Striking Times (OPC Concrete)\n\n"
            "Under standard temperature conditions (> 15°C with OPC cement):\n\n"
            "| Formwork Member | Minimum Period Before Striking |\n"
            "| :--- | :--- |\n"
            "| **Vertical sides of columns, walls, & beams** | **16 to 24 hours** |\n"
            "| **Slab soffits (props left underneath)** | **3 days** |\n"
            "| **Beam soffits (props left underneath)** | **7 days** |\n"
            "| **Props to slabs spanning up to 4.5 m** | **7 days** |\n"
            "| **Props to slabs spanning over 4.5 m** | **14 days** |\n"
            "| **Props to beams & arches spanning up to 6 m** | **14 days** |\n"
            "| **Props to beams & arches spanning over 6 m** | **21 days** |\n\n"
            "*(For low temperatures or blended PPC/GGBS cements, extend these periods based on cube compressive test results attaining > 70% characteristic strength).* "
        )

    elif "heat" in q or "temperature" in q:
        return (
            "### ☀️ Hot Weather Concreting Protocols (ACI 305R / IS 456)\n\n"
            "When ambient temperatures exceed 38°C:\n\n"
            "1. **Concrete Mix Control:**\n"
            "   - Replace 25-40% of batching water with crushed flaked ice to ensure fresh concrete temperature does not exceed 32°C.\n"
            "   - Add ASTM C494 Type D or Type G retarding superplasticizers to extend slump retention.\n"
            "2. **Subgrade & Shuttering Preparation:**\n"
            "   - Fog-spray steel formwork and reinforcement with cold water prior to pour (drain standing ponding).\n"
            "3. **Finishing & Curing:**\n"
            "   - Apply monomolecular film evaporation retarders immediately after floating.\n"
            "   - Commence wet burlap ponding as soon as the concrete sets to prevent plastic shrinkage cracking."
        )

    else:
        return (
            f"### 👷 Resident Structural Engineer Advisory\n\n"
            f"**Regarding your inquiry:** *\"{user_query}\"*\n\n"
            f"From an engineering perspective under **IS 456:2000** and **OSHA 1926 Safety Regulations**:\n\n"
            f"1. **Structural Integrity & Quality Assurance:** Verify that test cube specimens (150mm x 150mm) are cast in triplicate for 7-day and 28-day compressive verification according to IS 516 standards.\n"
            f"2. **Site Safety Precaution:** Current weather condition is **{current_weather}**. Ensure the shift supervisor confirms all tie-downs, electrical grounding, and edge protections before crew mobilization.\n"
            f"3. **Documentation:** Record all structural modifications in the daily site diary and obtain written sign-off from the Structural Consultant on record."
        )


def render_site_assistant_tab(client: GeminiMultimodalClient):
    """Renders Tab 4: Daily Site Assistant & Weather-Aware Advisory."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="color: #ffffff; margin-bottom: 4px;">🌤️ Weather-Aware Advisory & Daily Site Assistant (Epic 5)</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Real-time meteorological hazard matrix, OSHA/IS 456 site protocols, and conversational construction engineering assistant chatbot.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Weather Advisory Section
    st.markdown("#### 1. Dynamic Site Weather Condition Selector")
    weather_keys = list(WEATHER_PROTOCOLS.keys())
    selected_weather = st.selectbox(
        "Select Current / Forecast Site Weather Condition:",
        weather_keys,
        index=0,
        key="weather_selector",
    )

    protocol = WEATHER_PROTOCOLS[selected_weather]
    status_color = protocol["status_color"]
    alert_class = "danger" if status_color == "danger" else ("warning" if status_color == "warning" else "weather-alert-card")

    st.markdown(
        f"""
        <div class="weather-alert-card {alert_class}" style="margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; color: #ffffff;">{protocol['alert_title']}</h4>
                <span class="badge-severity {'badge-critical' if status_color == 'danger' else 'badge-medium'}">
                    {protocol['badge']}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin: 12px 0;">
                <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; font-size: 0.82rem;">
                    <strong>🏗️ Tower Cranes:</strong> {protocol['crane_status']}
                </div>
                <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; font-size: 0.82rem;">
                    <strong>🪜 Scaffolds:</strong> {protocol['scaffold_status']}
                </div>
                <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; font-size: 0.82rem;">
                    <strong>🧱 Concreting:</strong> {protocol['concrete_status']}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Directives Accordion
    with st.expander(f"📜 Mandatory Operational Directives ({selected_weather})", expanded=True):
        for d in protocol["directives"]:
            st.markdown(f"- {d}")
        st.markdown(f"**Regulatory Standards Cited:** `{', '.join(protocol['standards_cited'])}`")

    st.markdown("---")

    # 2. Interactive Multi-Turn Chatbot
    st.markdown("#### 2. Interactive Civil Engineering Site Assistant Chatbot")
    st.markdown(
        """
        <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 12px;">
            Consult with our AI Senior Resident Engineer on IS 456 concrete codes, OSHA safety regulations, crane wind thresholds, formwork striking schedules, and site troubleshooting.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Quick prompt chips
    st.markdown("##### 💡 Frequently Asked Engineering Queries")
    chip_col1, chip_col2 = st.columns([1, 1])

    suggested_queries = [
        "What is the minimum curing period for OPC concrete under IS 456?",
        "Under what wind speed must tower crane operations be halted?",
        "What are OSHA electrical clearance rules for scaffolding near power lines?",
        "Provide formwork de-shuttering striking time checklist for 7m beam span.",
        "How should we adjust concrete mix design for extreme summer heat (42°C)?",
    ]

    selected_chip = None
    with chip_col1:
        if st.button(f"📌 {suggested_queries[0]}", use_container_width=True):
            selected_chip = suggested_queries[0]
        if st.button(f"📌 {suggested_queries[1]}", use_container_width=True):
            selected_chip = suggested_queries[1]
        if st.button(f"📌 {suggested_queries[2]}", use_container_width=True):
            selected_chip = suggested_queries[2]
    with chip_col2:
        if st.button(f"📌 {suggested_queries[3]}", use_container_width=True):
            selected_chip = suggested_queries[3]
        if st.button(f"📌 {suggested_queries[4]}", use_container_width=True):
            selected_chip = suggested_queries[4]
        if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
            st.session_state["site_chat_history"] = []
            st.rerun()

    # Initialize chat history
    if "site_chat_history" not in st.session_state:
        st.session_state["site_chat_history"] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Greetings, Site Engineer!** I am your AI Construction Engineering Assistant. "
                    f"I am actively monitoring site conditions under **{selected_weather}**. "
                    "Ask me any question regarding IS 456:2000, OSHA 1926, structural repairs, or site management."
                ),
            }
        ]

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["site_chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    user_prompt = st.chat_input("Ask a construction safety or civil engineering question...")
    query_to_send = selected_chip or user_prompt

    if query_to_send:
        # Append user message
        st.session_state["site_chat_history"].append({"role": "user", "content": query_to_send})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(query_to_send)

        # Generate response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Consulting IS 456 & OSHA engineering knowledge base..."):
                    system_ctx = (
                        f"{CIVIL_ENGINEERING_SYSTEM_INSTRUCTION}\n"
                        f"CURRENT SITE WEATHER CONDITION: {selected_weather}\n"
                        f"WEATHER DIRECTIVES: {protocol['directives']}\n"
                    )

                    def local_fallback(messages: List[Dict[str, str]], **kwargs):
                        last_q = messages[-1]["content"] if messages else ""
                        return get_demo_chatbot_response(last_q, selected_weather)

                    reply_text, is_live, status_msg = client.chat_completion(
                        messages=st.session_state["site_chat_history"],
                        system_instruction=system_ctx,
                        fallback_handler=local_fallback,
                    )

                    st.markdown(reply_text)
                    if is_live:
                        st.caption(f"⚡ {status_msg}")
                    else:
                        st.caption(f"💡 {status_msg}")

        # Save assistant message
        st.session_state["site_chat_history"].append({"role": "assistant", "content": reply_text})
        st.rerun()
