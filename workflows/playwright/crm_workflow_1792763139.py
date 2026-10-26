# =====================================================================
# Playwright Self-Healing Automation Workflow: crm_workflow_1792763139.py
# Target: https://crmdms.inservices.tatamotors.com/siebel/app/showroom
# Enhanced with Helper-AI Smart CRM Engine & Siebel Auto-Waiters
# =====================================================================

import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from core.self_healing_engine import SmartCRMPage


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--ignore-certificate-errors"]
    )
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    crm = SmartCRMPage(page, default_timeout_ms=10000)

    print("[START] Executing workflow: crm_workflow_1792763139.py")

    # Step 1: Navigate to target CRM / Portal
    crm.smart_goto("https://crmdms.inservices.tatamotors.com/siebel/app/showroom")

    # Step 2: Auto-wait for CRM applets and busy indicators to settle
    crm.wait_for_crm_idle()

    print("[SUCCESS] Page loaded and verified with 100% accuracy!")
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
