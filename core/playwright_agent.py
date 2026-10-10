"""Playwright Vision & Advanced Browser Agent for Helper-AI.

Connects to the persistent live Chrome browser via Chrome DevTools Protocol (CDP on port 9222)
to provide fast visual screenshots, accessibility tree inspection, DOM element interaction,
and JavaScript execution.
"""
import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger("PlaywrightVisionAgent")


class PlaywrightVisionAgent:
    """Controls browser with Playwright over CDP."""
    _instance: Optional["PlaywrightVisionAgent"] = None

    @classmethod
    def get_instance(cls) -> "PlaywrightVisionAgent":
        if cls._instance is None:
            cls._instance = PlaywrightVisionAgent()
        return cls._instance

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222"):
        self.cdp_url = cdp_url

    async def _get_active_page(self, p) -> Page:
        browser = await p.chromium.connect_over_cdp(self.cdp_url)
        contexts = browser.contexts
        if not contexts:
            context = await browser.new_context()
            return await context.new_page()
        context = contexts[0]
        pages = context.pages
        if not pages:
            return await context.new_page()
        return pages[-1]

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to URL and waits for page load."""
        async with async_playwright() as p:
            page = await self._get_active_page(p)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1.0)
            title = await page.title()
            current_url = page.url
            return {
                "success": True,
                "url": current_url,
                "title": title,
                "output": f"Navigated to '{current_url}' (Title: '{title}')."
            }

    async def get_interactive_elements(self) -> Dict[str, Any]:
        """Scans page for interactive buttons, links, inputs, and form controls."""
        async with async_playwright() as p:
            page = await self._get_active_page(p)
            title = await page.title()
            url = page.url

            # Extract visible interactive elements
            elements = await page.evaluate("""() => {
                const results = [];
                const query = 'button, a, input, textarea, select, [role="button"], [role="link"], [role="tab"]';
                document.querySelectorAll(query).forEach((el) => {
                    const rect = el.getBoundingClientRect();
                    const isVisible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                    if (isVisible) {
                        const tag = el.tagName.toLowerCase();
                        const text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim().slice(0, 60);
                        if (text) {
                            results.push({
                                tag: tag,
                                role: el.getAttribute('role') || tag,
                                text: text,
                                id: el.id || null
                            });
                        }
                    }
                });
                return results.slice(0, 50);
            }""")

            buttons = [e["text"] for e in elements if e["tag"] in ["button", "input"] or e["role"] == "button"]
            links = [e["text"] for e in elements if e["tag"] == "a" or e["role"] == "link"]

            return {
                "success": True,
                "title": title,
                "url": url,
                "buttons": buttons[:15],
                "links": links[:15],
                "total_interactive": len(elements),
                "output": f"Page: '{title}' ({url})\nInteractive buttons visible: {buttons[:10]}\nLinks visible: {links[:10]}"
            }

    async def click(self, target: str) -> Dict[str, Any]:
        """Clicks an element by visible text, aria-label, role, or CSS selector."""
        async with async_playwright() as p:
            page = await self._get_active_page(p)
            clicked = False

            # Try by text locator first
            locators = [
                page.get_by_role("button", name=target, exact=False),
                page.get_by_text(target, exact=False),
                page.locator(f"text={target}"),
                page.locator(target)
            ]

            for loc in locators:
                try:
                    if await loc.count() > 0:
                        await loc.first.click(timeout=3000)
                        clicked = True
                        break
                except Exception:
                    continue

            if not clicked:
                # Fallback to JS click
                clicked = await page.evaluate("""(targetText) => {
                    const all = document.querySelectorAll('button, a, input, [role="button"], div, span');
                    for (const el of all) {
                        if (el.innerText && el.innerText.trim().toLowerCase() === targetText.toLowerCase()) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }""", target)

            await asyncio.sleep(1.0)
            title = await page.title()
            url = page.url

            return {
                "success": bool(clicked),
                "target": target,
                "title": title,
                "url": url,
                "output": f"Clicked '{target}' on page. New URL: {url}" if clicked else f"Could not find clickable element matching '{target}'."
            }

    async def type_text(self, target: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Types text into an input or textarea identified by placeholder, label, or selector."""
        async with async_playwright() as p:
            page = await self._get_active_page(p)
            typed = False

            locators = [
                page.get_by_placeholder(target, exact=False),
                page.get_by_label(target, exact=False),
                page.locator(f"input[name='{target}'], textarea[name='{target}']"),
                page.locator(target),
                page.locator("input:visible, textarea:visible")
            ]

            for loc in locators:
                try:
                    if await loc.count() > 0:
                        await loc.first.fill(text, timeout=3000)
                        if press_enter:
                            await loc.first.press("Enter")
                        typed = True
                        break
                except Exception:
                    continue

            return {
                "success": typed,
                "target": target,
                "text": text,
                "output": f"Entered text into '{target}'." if typed else f"Could not locate input field matching '{target}'."
            }

    async def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Captures a screenshot of the live browser viewport."""
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        fn = filename or f"browser_{int(time.time())}.png"
        out_path = screenshots_dir / fn

        async with async_playwright() as p:
            page = await self._get_active_page(p)
            await page.screenshot(path=str(out_path))
            title = await page.title()
            url = page.url

            return {
                "success": True,
                "file_path": str(out_path.resolve()),
                "title": title,
                "url": url,
                "output": f"Captured live browser screenshot of '{title}' to '{out_path.name}'."
            }
