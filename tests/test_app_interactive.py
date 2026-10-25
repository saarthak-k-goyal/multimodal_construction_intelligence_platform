"""
Interactive AppTest Suite for Streamlit Components
Tests end-to-end execution of tabs, buttons, and state mutations.
"""

import os
import sys

from streamlit.testing.v1 import AppTest

def test_full_app_execution():
    print("Executing AppTest on app.py...")
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()
    assert not at.exception, f"App threw exception on load: {at.exception}"
    print("  -> Initial render clean.")

    # Check that tabs are present
    tabs = at.tabs
    assert len(tabs) == 4, f"Expected 4 tabs, got {len(tabs)}"
    print(f"  -> Found {len(tabs)} tabs: {[t.label for t in tabs]}")

    # Check button interactions
    buttons = at.button
    print(f"  -> Found {len(buttons)} interactive buttons across tabs.")

    # Trigger Safety Audit button
    run_safety_btns = [b for b in buttons if "Safety & PPE Audit" in b.label]
    if run_safety_btns:
        print(f"  -> Clicking '{run_safety_btns[0].label}'...")
        run_safety_btns[0].click().run()
        assert not at.exception, f"Exception after safety audit click: {at.exception}"
        print("  -> Safety audit executed successfully without exception.")

    # Trigger Crack Diagnostics button
    run_crack_btns = [b for b in at.button if "Forensic Crack" in b.label]
    if run_crack_btns:
        print(f"  -> Clicking '{run_crack_btns[0].label}'...")
        run_crack_btns[0].click().run()
        assert not at.exception, f"Exception after crack diagnostic click: {at.exception}"
        print("  -> Crack diagnostic executed successfully without exception.")

    # Trigger 3D Render button
    run_render_btns = [b for b in at.button if "Render 3D" in b.label]
    if run_render_btns:
        print(f"  -> Clicking '{run_render_btns[0].label}'...")
        run_render_btns[0].click().run()
        assert not at.exception, f"Exception after 3D render click: {at.exception}"
        print("  -> 3D render executed successfully without exception.")

    print("\n🎉 ALL STREAMLIT APP INTERACTIONS PASSED CLEANLY!")

if __name__ == "__main__":
    test_full_app_execution()
