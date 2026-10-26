import os
import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.sync_api import Playwright, sync_playwright, expect
from core.self_healing_engine import SmartCRMPage


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="chrome", headless=False, args=["--ignore-certificate-errors"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    crm = SmartCRMPage(page)
    crm.smart_goto("https://crmdms.inservices.tatamotors.com/siebel/app/showroom")

    # ---------------------
    context.storage_state(path=str(PROJECT_ROOT / "workflows" / "storage" / "tata_crm_session.json"))
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

