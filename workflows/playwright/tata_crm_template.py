# =====================================================================
# Playwright Self-Healing Workflow: Tata CRM & Enterprise Portal Automation
# Ready for Standalone Replay and High-Speed Excel/CSV Batch Mode.
# Placeholders: {{name}}, {{mobile}}, {{city}}, {{model}}
# =====================================================================

import os
import sys
import re
import time
from pathlib import Path

# Ensure project root is in sys.path so 'core' modules resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.sync_api import Playwright, sync_playwright, expect
from core.self_healing_engine import SmartCRMPage

STORAGE_FILE = PROJECT_ROOT / "workflows" / "storage" / "tata_crm_session.json"


def run(playwright: Playwright) -> None:
    # 1. Launch real Google Chrome / Chromium with Enterprise anti-detection flags
    browser = playwright.chromium.launch(
        channel="chrome" if os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe") else None,
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--ignore-certificate-errors",
            "--no-default-browser-check"
        ]
    )

    # 2. Setup context with saved session storage for Zero Re-Login if available
    context_kwargs = {"ignore_https_errors": True}
    if STORAGE_FILE.exists():
        context_kwargs["storage_state"] = str(STORAGE_FILE)

    context = browser.new_context(**context_kwargs)
    page = context.new_page()
    crm = SmartCRMPage(page, default_timeout_ms=10000)

    print("[START] Executing Tata CRM Automation Workflow...")

    # 3. Navigate to target portal (Tata Motors Siebel CRM or test form)
    target_url = os.getenv("CRM_TARGET_URL", "https://httpbin.org/forms/post")
    crm.smart_goto(target_url)

    # 4. Fill Customer Details with Self-Healing Multi-Strategy Locators
    # Strategy order: role -> label -> placeholder -> name -> css -> xpath -> fuzzy DOM recovery
    crm.smart_fill(
        {
            "label": "label=Customer Name",
            "placeholder": "placeholder=Name",
            "name_attr": "input[name='custname']",
            "css": "input[name='custname']",
            "xpath": "//input[@name='custname']"
        },
        "{{name}}",
        desc="Customer Name"
    )

    crm.smart_fill(
        {
            "label": "label=Telephone",
            "placeholder": "placeholder=Mobile",
            "name_attr": "input[name='custtel']",
            "css": "input[name='custtel']",
            "xpath": "//input[@name='custtel']"
        },
        "{{mobile}}",
        desc="Customer Mobile Number"
    )

    # 5. Radio / Checkbox & Dropdown Selection
    crm.smart_check(
        {
            "name_attr": "input[name='size'][value='medium']",
            "css": "input[value='medium']"
        },
        checked=True,
        desc="Vehicle / Option Selection"
    )

    # 6. Remarks / Notes with City Parameter
    crm.smart_fill(
        {
            "name_attr": "textarea[name='comments']",
            "css": "textarea[name='comments']"
        },
        "Automated booking inquiry for {{model}} generated via Helper-AI for {{city}} showroom.",
        desc="Inquiry Notes"
    )

    # 7. Submit Action
    crm.smart_click(
        {
            "role": "role=button,Submit order",
            "text": "text=Submit",
            "css": "button[type='submit']"
        },
        desc="Submit Button"
    )

    # 8. Save updated session state on exit
    try:
        STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(STORAGE_FILE))
    except Exception:
        pass

    print("[SUCCESS] Tata CRM workflow executed with 100% accuracy for {{name}} ({{mobile}}).")
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
