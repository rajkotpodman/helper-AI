# Playwright Workflow Template: Tata CRM Lead Entry Automation
# Generated with Playwright Codegen
# Variables like {{name}}, {{mobile}}, {{city}}, {{model}} will be auto-replaced when run in Batch Mode with Excel/CSV.

import re
from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 1. Navigate to target portal (e.g. Tata CRM or sample form)
    page.goto("https://httpbin.org/forms/post")

    # 2. Fill Customer Name & Mobile
    # For Tata CRM, replace selectors with the ones captured via Playwright Codegen
    page.locator("input[name=\"custname\"]").click()
    page.locator("input[name=\"custname\"]").fill("{{name}}")

    page.locator("input[name=\"custtel\"]").click()
    page.locator("input[name=\"custtel\"]").fill("{{mobile}}")

    # 3. Select Dropdowns
    # e.g. Model / Size / Branch
    page.locator("input[name=\"size\"][value=\"medium\"]").check()

    # 4. Fill Comments / Notes
    page.locator("textarea[name=\"comments\"]").fill("Lead generated automatically via Helper-AI Playwright for {{city}} branch.")

    # 5. Submit Form
    page.get_by_role("button", name="Submit order").click()

    # 6. Verify Submission Confirmation
    expect(page.locator("body")).to_contain_text("custname")
    print("[SUCCESS] Form submitted successfully for {{name}} ({{mobile}})")

    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
