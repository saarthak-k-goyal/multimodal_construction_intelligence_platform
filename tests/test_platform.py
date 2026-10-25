"""
Unit & Integration Smoke Tests for Multimodal Construction Intelligence Platform
Validates:
1. Gemini client initialization & JSON cleaning
2. Safety Audit JSON contract & OSHA/IS 456 structures
3. Crack Diagnostics defect classification & IS 456 limits
4. Project Planner CapEx, S-curve, Valuation in INR (Lakhs/Crores), and CPWD material takeoffs
5. Pollinations AI 3D architectural rendering prompt generator
6. Weather advisory rules engine & Chatbot responses
7. Asset generation and image dimensions
"""

import os
import sys
from PIL import Image

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from modules.gemini_client import GeminiMultimodalClient, clean_json_response
from modules.safety_audit import get_mock_safety_audit, SAFETY_AUDIT_PROMPT
from modules.crack_diagnostics import get_mock_crack_diagnostics, CRACK_DIAGNOSTICS_PROMPT
from modules.project_planner import (
    calculate_project_financials,
    format_inr,
    generate_pollinations_prompt,
    COST_BENCHMARKS,
)
from modules.site_assistant import WEATHER_PROTOCOLS, get_demo_chatbot_response
from modules.asset_generator import generate_sample_safety_image, generate_sample_crack_image


def test_json_cleaner():
    print("Testing clean_json_response...")
    # Markdown fence test
    fenced = '```json\n{"safety_score": 88, "overall_status": "Compliant"}\n```'
    parsed = clean_json_response(fenced)
    assert parsed["safety_score"] == 88
    assert parsed["overall_status"] == "Compliant"

    # Messy text test
    messy = 'Here is your inspection:\n{"crack_width": 2.5, "urgency": "High",}\nThanks!'
    parsed2 = clean_json_response(messy)
    assert parsed2["crack_width"] == 2.5
    assert parsed2["urgency"] == "High"
    print("  -> Passed JSON cleaner tests.")


def test_gemini_client_fallback():
    print("Testing GeminiMultimodalClient fallback...")
    client = GeminiMultimodalClient(api_key=None)
    assert not client.is_live

    # Test safety fallback
    test_img = Image.new("RGB", (100, 100), color=(100, 100, 100))
    res, is_live, msg = client.analyze_image_json(
        image=test_img,
        prompt=SAFETY_AUDIT_PROMPT,
        fallback_handler=get_mock_safety_audit,
        preset_key="hazard_scaffold",
    )
    assert not is_live
    assert res["safety_score"] == 42
    assert res["overall_status"] == "Critical Risk"
    assert len(res["ppe_detection"]) >= 4
    assert len(res["identified_site_hazards"]) >= 1
    assert "OSHA" in str(res["standards_referenced"])
    print("  -> Passed Gemini client safety fallback.")

    # Test crack fallback
    res_crack, is_live_crack, msg_crack = client.analyze_image_json(
        image=test_img,
        prompt=CRACK_DIAGNOSTICS_PROMPT,
        fallback_handler=get_mock_crack_diagnostics,
        preset_key="shear",
    )
    assert not is_live_crack
    assert res_crack["defect_type"] == "Structural Shear Crack"
    assert res_crack["estimated_width_mm"] == 3.6
    assert res_crack["is_456_limit_state_violation"] is True
    print("  -> Passed Gemini client crack fallback.")


def test_safety_audit_contract():
    print("Testing Safety Audit contract completeness...")
    presets = ["hazard_scaffold", "compliant_site", "custom"]
    for p in presets:
        audit = get_mock_safety_audit(p)
        assert 0 <= audit["safety_score"] <= 100
        assert audit["overall_status"] in ["Compliant", "Minor Violations", "Critical Risk", "High Risk"]
        assert isinstance(audit["ppe_detection"], list)
        for item in audit["ppe_detection"]:
            assert "item" in item
            assert "compliance_status" in item
            assert "compliance_rate" in item
        for haz in audit["identified_site_hazards"]:
            assert "severity" in haz
            assert "corrective_remedy" in haz
    print("  -> Passed Safety Audit contract tests.")


def test_crack_diagnostics_contract():
    print("Testing Crack Diagnostics contract completeness...")
    defects = ["shear", "spalling", "settlement", "thermal", "hairline"]
    for d in defects:
        diag = get_mock_crack_diagnostics(d)
        assert diag["defect_type"] in [
            "Structural Shear Crack",
            "Spalling & Rebar Delamination",
            "Settlement Crack",
            "Thermal Expansion Crack",
            "Hairline Crack",
        ]
        assert diag["estimated_width_mm"] > 0
        assert 0 <= diag["structural_integrity_score"] <= 100
        assert len(diag["recommended_repairs"]) >= 1
        assert "execution_steps" in diag["recommended_repairs"][0]
    print("  -> Passed Crack Diagnostics contract tests.")


def test_project_planner_and_valuation():
    print("Testing Planning & Real Estate Valuation calculations...")
    tier = "Tier 1 (Mumbai, Bengaluru, Delhi-NCR, Hyderabad)"
    structure = "Residential High-Rise (G+20)"
    quality = "Premium (Imported Finishes & Smart MEP)"
    sqft = 100_000
    completion = 50.0

    fin = calculate_project_financials(
        sqft=sqft,
        structure_type=structure,
        tier=tier,
        quality=quality,
        completion_pct=completion,
    )

    # Validate CapEx calculations
    assert fin["total_capex_budget_inr"] > 0
    assert 0 < fin["capex_incurred_inr"] < fin["total_capex_budget_inr"]
    assert fin["current_asset_valuation_inr"] > 0
    assert fin["completed_market_value_inr"] > fin["total_capex_budget_inr"]

    # Validate materials calculations (CPWD norms)
    mats = fin["materials"]
    assert mats["steel_metric_tonnes"] > 0
    assert mats["cement_bags_50kg"] > 0
    assert mats["coarse_aggregate_cft"] > 0
    assert mats["sand_m_sand_cft"] > 0

    # Currency formatting
    assert "Cr" in format_inr(fin["total_capex_budget_inr"])
    assert "Cr" in format_inr(fin["current_asset_valuation_inr"])
    print(f"  -> Total CapEx: {format_inr(fin['total_capex_budget_inr'])}, Current Valuation: {format_inr(fin['current_asset_valuation_inr'])}")
    print(f"  -> Steel: {mats['steel_metric_tonnes']} MT, Cement: {mats['cement_bags_50kg']} Bags")

    # Pollinations AI Prompt & URL
    prompt, url = generate_pollinations_prompt(
        structure_type=structure,
        tier=tier,
        architectural_style="Contemporary Biophilic",
        lighting_time="Golden Hour Sunset",
        seed=123,
    )
    assert "https://image.pollinations.ai/prompt/" in url
    assert "width=1280" in url
    assert "seed=123" in url
    print("  -> Passed Planning, Valuation & Pollinations tests.")


def test_weather_and_chatbot():
    print("Testing Weather protocols and Chatbot response engine...")
    for w_name, w_proto in WEATHER_PROTOCOLS.items():
        assert "alert_title" in w_proto
        assert "directives" in w_proto
        assert len(w_proto["directives"]) >= 3
        assert "crane_status" in w_proto

    # Chatbot test queries
    resp_curing = get_demo_chatbot_response("What is the minimum curing period for OPC concrete under IS 456?", "Extreme Heat (> 40°C ambient)")
    assert "IS 456:2000, Clause 13.5" in resp_curing
    assert "7 days" in resp_curing

    resp_crane = get_demo_chatbot_response("Under what wind speed must tower crane operations be halted?", "High Wind (> 45 km/h gusts)")
    assert "OSHA 29 CFR 1926.1431" in resp_crane
    assert "weather-vaning" in resp_crane

    resp_power = get_demo_chatbot_response("What are OSHA electrical clearance rules for scaffolding near overhead lines?", "Normal / Favorable")
    assert "10 feet" in resp_power
    print("  -> Passed Weather & Chatbot engine tests.")


def test_asset_generation():
    print("Testing Asset Generation...")
    safety_img = generate_sample_safety_image("hazard_scaffold")
    assert safety_img.size == (800, 500)

    crack_img = generate_sample_crack_image("shear")
    assert crack_img.size == (800, 500)
    print("  -> Passed Asset Generation tests.")


if __name__ == "__main__":
    test_json_cleaner()
    test_gemini_client_fallback()
    test_safety_audit_contract()
    test_crack_diagnostics_contract()
    test_project_planner_and_valuation()
    test_weather_and_chatbot()
    test_asset_generation()
    print("\n🎉 ALL UNIT AND INTEGRATION SMOKE TESTS PASSED SUCCESSFULLY!")
