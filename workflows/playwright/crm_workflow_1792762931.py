import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="chrome", headless=False)
    context = browser.new_context()
    page = context.new_page()

    # ---------------------
    context.storage_state(path="E:\\ai agent\\workflows\\storage\\tata_crm_session.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
