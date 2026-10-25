# 🏗️ ConstructAI - Multimodal Construction Intelligence Platform
### Skill Wallet Capstone Project 1 • Production-Ready Streamlit Application

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python 3.12](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Standards: OSHA & IS 456](https://img.shields.io/badge/Standards-OSHA%201926%20%7C%20IS%20456%3A2000-orange.svg)](#regulatory-standards--codes-referenced)

**ConstructAI** is a full-stack multimodal AI engineering platform for the construction, structural forensics, and real estate development industries. Featuring a clean, lightweight industrial UI inspired by modern engineering dashboards, it seamlessly integrates Google Gemini vision models, OSHA 29 CFR 1926, IS 456:2000 concrete standards, CapEx S-curve valuation, and 3D architectural rendering via Pollinations AI.

---

## 🎨 UI & Layout Highlights (Reference-Aligned)

1. **Dark Left Navigation Sidebar (`#121316`):**
   - Brand logo: `CONSTRUCTAI` with orange safety helmet accent.
   - Quick navigation modules with active pill highlight.
   - Secure Google Gemini API key configuration (supporting Free Tier `gemini-1.5-flash`, `gemini-2.5-flash`, `gemini-1.5-pro` with zero-error demonstration fallback).
   - Real-time status indicator: `● System Online`.

2. **Clean Light Workspace Canvas (`#F4F5F7`):**
   - Split two-column workflow: **Input Data** (left) and **Analysis Results** (right).
   - Empty state card: Displays `Waiting for input...` prior to execution.
   - Bold safety orange primary action buttons: `ANALYZE HAZARDS`, `RUN DIAGNOSIS`, `GENERATE TODAY'S PLAN`, `CHECK FEASIBILITY`, `CALCULATE VALUE`, `GENERATE PLAN`.
   - Top right badge: `● AI ACTIVE`.

3. **Production Polish:**
   - Zero "TODO", placeholder, or debugging scaffolding.
   - 100% self-contained: zero external database dependencies.
   - Ready for 1-click deployment on Streamlit Community Cloud.

---

## 📋 Kanban Epics Matrix

| Epic | Module Name | Scope & Engineering Implementation | Status |
| :--- | :--- | :--- | :---: |
| **Pre-reqs** | Tech Stack & Setup | Python 3.9+, venv/uv isolation, Streamlit, Pillow, Plotly, Google GenAI SDK | ✅ Completed |
| **Epic 1** | Requirements & Env | Modular architecture, environment variables, theme styling, zero-DB cloud config | ✅ Completed |
| **Epic 2** | Safety Vision & Crack Diagnostics | Worker PPE compliance auditing (OSHA/IS 456), concrete crack morphology & repair protocols | ✅ Completed |
| **Epic 3** | Planning & Real Estate Valuation | Dynamic CapEx budget, S-curve expenditure, Indian Tier 1/2/3 market valuation, 3D Pollinations render | ✅ Completed |
| **Epic 4** | Multimodal AI & JSON Contracts | Structured schema validation, markdown code-fence sanitization, demo fallback engine | ✅ Completed |
| **Epic 5** | Site Chatbot & Weather Advisory | Meteorological hazard engine, multi-turn AI civil engineer chatbot with IS/OSHA knowledge base | ✅ Completed |
| **Epic 6** | Interface, Testing & Deployment | Industrial ConstructAI CSS, unit/interactive AppTest suite, 1-click Streamlit Community Cloud readiness | ✅ Completed |

---

## 🏛️ Module Overview

### 1. Tab 1 – Site Safety & PPE Audit (Epic 2)
- **Input Data Card:** Observation Log textarea + Site Photo uploader / preset selection.
- **Analysis Results Card:** Safety Score (0-100), Worker Compliance rate, OSHA/IS 456 PPE Detection Matrix (helmets, high-vis vests, steel-toe boots, fall arrest harnesses), identified site hazards with severity tags (`CRITICAL`, `HIGH`, `MEDIUM`), and 1-click downloadable JSON audit report.

### 2. Tab 2 – Crack Diagnostics & Structural Integrity (Epic 2)
- **Input Analysis Data Card:** Defect description textarea + concrete surface close-up uploader / defect scenario library.
- **Analysis Results Card:** Defect classification (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling), measured crack width (mm), structural integrity score (0-100), IS 456:2000 Clause 35.3.2 limit state compliance check, root causes, and technical repair protocols (epoxy injection, structural re-grouting, CFRP composite wrap).

### 3. Tab 3 – Planning & Real Estate Valuation (Epic 3)
- **Project Planner View:** Project brief input + 3 clean side-by-side cards:
  - *Material Estimator:* Cement (bags), Sand (tons), Aggregate (tons), Steel (kg), Concrete Volume (m³).
  - *Cost Estimator:* Materials, Labour, Finishing, and Total CapEx (INR Crores/Lakhs) with S-curve disbursement.
  - *Time Schedule:* Milestone tracker across all 5 construction phases.
- **Real Estate Estimator View:** Property Details input (Location, Area sqft, Completion %, Type, Amenities) $\rightarrow$ Estimated Market Asset Valuation & Gross Development Value.
- **Conceptual 3D Architectural Rendering:** Pollinations AI integration generating 8K visualization previews.

### 4. Tab 4 – Daily Site Assistant & Weather Advisory (Epic 5)
- **Daily Site Assistant:** Planned Activity (Concreting, Formwork, Steel, Excavation), Labour Count, Site Condition $\rightarrow$ Today's Tasks, Safety Checks pills, and Risk Alerts.
- **Weather Advisor:** Weather condition selector $\rightarrow$ Feasibility Status (`PROCEED WITH CAUTION`, `HALT CRANE & ELEVATED TRADES`, `OPTIMAL CONDITIONS`), Hazard tags, and Required Precautions.
- **Construction Chatbot:** Multi-turn assistant with chat bubbles, quick prompt chips (`ASK A QUESTION`, `GET A CONSTRUCTION TIP`, `DISCUSS A PROJECT`), and civil engineering codal guidance.
- **Knowledge Assistant:** Direct category queries (`SAFETY`, `TECHNIQUE`, `DOC GEN`).

---

## 🛠️ Local Installation & Running

```bash
# 1. Activate virtual environment
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/macOS

# 2. Run the application
streamlit run app.py
```

The application will launch immediately at `http://localhost:8501`.

---

## 🧪 Automated Testing

```bash
# Run unit & contract tests
python tests/test_platform.py

# Run interactive Streamlit AppTest suite
python tests/test_app_interactive.py
```

---

## 📜 Regulatory Standards & Codes Referenced
- **OSHA 29 CFR 1926:** Safety and Health Regulations for Construction
- **IS 456:2000:** Plain and Reinforced Concrete - Code of Practice (Bureau of Indian Standards)
- **IS 13415:1992:** Code of Safety for Working on Scaffolds
- **IS 2925:1984:** Specification for Industrial Safety Helmets
- **IS 3521:1999:** Industrial Safety Belts and Harnesses
- **ACI 224R-01:** Control of Cracking in Concrete Structures
- **ACI 305R / 306R:** Hot and Cold Weather Concreting Guides
- **CPWD Plinth Area Rates & Civil Norms (2024-2026)**
