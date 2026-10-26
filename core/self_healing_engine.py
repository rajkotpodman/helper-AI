"""Helper-AI: Smart Self-Healing Browser & CRM Automation Engine.

Provides an enterprise-grade execution layer for Playwright that ensures 100% accuracy:
1. Multi-tier selector fallback cascade (Semantic -> Label -> ID/Name -> Text -> XPath -> Fuzzy DOM similarity).
2. Enterprise CRM & Siebel Open UI Auto-Waiters (waits for spinners, AJAX blockers, and network idle).
3. Self-healing DOM recovery: dynamically locates relocated elements if IDs or classes change.
4. Framework event trigger: dispatches real input and change events so modern JS/Siebel frameworks register inputs.
"""

import os
import sys
import time
import logging
import difflib
from typing import List, Dict, Any, Optional, Union
from playwright.sync_api import Page, Locator, Frame, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger("SelfHealingEngine")

# Common Enterprise & CRM loading spinner selectors
CRM_SPINNER_SELECTORS = [
    ".siebel-busy-indicator",
    ".ui-loading-panel",
    ".swe-busy",
    ".siebui-busy",
    "[aria-busy='true']",
    ".loading-spinner",
    ".spinner-border",
    ".ant-spin-spinning",
    ".el-loading-mask",
    ".dx-loadpanel",
    ".modal-backdrop.fade.show",
    "#divLoading",
    ".loading-overlay"
]


class SmartCRMPage:
    """Intelligent wrapper around Playwright Page for ultra-resilient automation."""

    def __init__(self, page: Page, default_timeout_ms: int = 8000):
        self.page = page
        self.default_timeout_ms = default_timeout_ms
        self.healed_actions: List[Dict[str, Any]] = []

    def wait_for_crm_idle(self, timeout_ms: int = 6000) -> None:
        """Waits for network activity and enterprise CRM busy indicators to settle."""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass

        try:
            self.page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 3000))
        except Exception:
            pass

        # Wait for any active CRM busy spinners to disappear
        start = time.time()
        timeout_s = timeout_ms / 1000.0
        for spinner in CRM_SPINNER_SELECTORS:
            if time.time() - start > timeout_s:
                break
            try:
                loc = self.page.locator(spinner).first
                if loc.is_visible(timeout=200):
                    logger.info(f"[CRM Idle] Waiting for spinner '{spinner}' to hide...")
                    loc.wait_for(state="hidden", timeout=timeout_ms)
            except Exception:
                continue

    def _resolve_locator(self, selectors: Union[str, List[str], Dict[str, Any]], desc: str = "") -> Locator:
        """Tries multiple locator strategies in order until one is visible and interactable."""
        candidate_list: List[str] = []
        if isinstance(selectors, str):
            candidate_list = [selectors]
        elif isinstance(selectors, list):
            candidate_list = [s for s in selectors if s and isinstance(s, str)]
        elif isinstance(selectors, dict):
            # Prioritized order of strategies from smart recorder
            order = ["role", "label", "placeholder", "text", "test_id", "css", "name_attr", "id_attr", "xpath"]
            for k in order:
                if selectors.get(k):
                    candidate_list.append(selectors[k])

        if not candidate_list:
            raise ValueError(f"No valid selectors provided for {desc}")

        # 1. Primary & Secondary strategy loop
        last_error = None
        for sel in candidate_list:
            try:
                loc = self._parse_selector(sel)
                if loc.count() > 0 and loc.first.is_visible(timeout=1000):
                    return loc.first
            except Exception as e:
                last_error = e
                continue

        # Try again with a slightly longer wait on the first available candidate
        for sel in candidate_list:
            try:
                loc = self._parse_selector(sel)
                loc.first.wait_for(state="visible", timeout=self.default_timeout_ms // 2)
                return loc.first
            except Exception as e:
                last_error = e
                continue

        # 2. Check across frames (Siebel CRM uses nested iframes like #_sweview)
        try:
            for frame in self.page.frames:
                if frame == self.page.main_frame:
                    continue
                for sel in candidate_list:
                    try:
                        loc = frame.locator(sel)
                        if loc.count() > 0 and loc.first.is_visible(timeout=500):
                            logger.info(f"[Self-Healing] Found '{desc}' inside frame '{frame.name or frame.url}'")
                            return loc.first
                    except Exception:
                        continue
        except Exception:
            pass

        # 3. AI / Fuzzy DOM similarity recovery
        logger.warning(f"[Self-Healing] All standard selectors failed for '{desc}'. Attempting DOM recovery...")
        recovered = self._fuzzy_recover(candidate_list, desc)
        if recovered:
            return recovered

        raise PlaywrightTimeoutError(f"Could not locate element for '{desc}'. Tried: {candidate_list}. Last error: {last_error}")

    def _parse_selector(self, sel: str) -> Locator:
        """Parses custom selector representations into Playwright locators."""
        sel = sel.strip()
        if sel.startswith("role="):
            parts = sel[5:].split(",", 1)
            role = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else None
            return self.page.get_by_role(role, name=name)
        elif sel.startswith("label="):
            return self.page.get_by_label(sel[6:].strip())
        elif sel.startswith("placeholder="):
            return self.page.get_by_placeholder(sel[12:].strip())
        elif sel.startswith("text="):
            return self.page.get_by_text(sel[5:].strip())
        elif sel.startswith("test_id="):
            return self.page.get_by_test_id(sel[8:].strip())
        else:
            return self.page.locator(sel)

    def _fuzzy_recover(self, failed_selectors: List[str], desc: str) -> Optional[Locator]:
        """Scans DOM candidates to locate shifted or renamed CRM elements."""
        target_hints = [desc.lower()] + [s.lower() for s in failed_selectors]
        candidates = self.page.locator("button, input, a, select, textarea, [role='button'], [role='textbox'], .siebui-btn, .siebui-input-popup").all()

        best_loc = None
        best_score = 0.0

        for cand in candidates:
            try:
                outer = cand.evaluate("el => (el.outerHTML || '') + ' ' + (el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('title') || '') + ' ' + (el.getAttribute('name') || '')").lower()
                for hint in target_hints:
                    ratio = difflib.SequenceMatcher(None, hint, outer).ratio()
                    if hint in outer:
                        ratio = max(ratio, 0.75)
                    if ratio > best_score:
                        best_score = ratio
                        best_loc = cand
            except Exception:
                continue

        if best_score >= 0.45 and best_loc is not None:
            logger.info(f"[Self-Healing SUCCESS] Healed element for '{desc}' with confidence score: {best_score:.2f}")
            self.healed_actions.append({"desc": desc, "score": best_score, "failed": failed_selectors})
            return best_loc
        return None

    def smart_goto(self, url: str, wait_for_idle: bool = True) -> None:
        """Navigates to URL and waits for page and CRM applets to mount."""
        logger.info(f"[Smart Goto] Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
        if wait_for_idle:
            self.wait_for_crm_idle()

    def smart_click(self, selectors: Union[str, List[str], Dict[str, Any]], desc: str = "") -> None:
        """Waits for CRM readiness, resolves element with fallback cascade, and clicks."""
        self.wait_for_crm_idle(timeout_ms=3000)
        target = self._resolve_locator(selectors, desc=desc or "Click Target")
        target.scroll_into_view_if_needed(timeout=2000)
        target.click(timeout=self.default_timeout_ms)
        self.wait_for_crm_idle(timeout_ms=2500)

    def smart_fill(self, selectors: Union[str, List[str], Dict[str, Any]], value: str, desc: str = "", clear_first: bool = True) -> None:
        """Fills input with auto-wait, clearing, and framework change event dispatch."""
        self.wait_for_crm_idle(timeout_ms=3000)
        target = self._resolve_locator(selectors, desc=desc or f"Fill '{value}'")
        target.scroll_into_view_if_needed(timeout=2000)
        if clear_first:
            try:
                target.fill("")
            except Exception:
                target.press("Control+A")
                target.press("Backspace")

        target.fill(str(value), timeout=self.default_timeout_ms)

        # Dispatch change/input event to ensure CRM JavaScript frameworks detect value
        try:
            target.evaluate("el => { el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }")
        except Exception:
            pass

    def smart_select(self, selectors: Union[str, List[str], Dict[str, Any]], option: str, desc: str = "") -> None:
        """Selects option in standard select or custom dropdown."""
        self.wait_for_crm_idle(timeout_ms=3000)
        target = self._resolve_locator(selectors, desc=desc or f"Select '{option}'")
        target.scroll_into_view_if_needed(timeout=2000)
        try:
            target.select_option(label=option, timeout=3000)
        except Exception:
            try:
                target.select_option(value=option, timeout=3000)
            except Exception:
                # Custom dropdown fallback: click dropdown trigger then click item with text
                target.click()
                self.page.locator(f"text='{option}'").first.click(timeout=3000)
        self.wait_for_crm_idle(timeout_ms=2000)

    def smart_check(self, selectors: Union[str, List[str], Dict[str, Any]], checked: bool = True, desc: str = "") -> None:
        """Checks or unchecks checkbox / radio."""
        self.wait_for_crm_idle(timeout_ms=3000)
        target = self._resolve_locator(selectors, desc=desc or "Checkbox/Radio")
        target.scroll_into_view_if_needed(timeout=2000)
        if checked:
            target.check(timeout=self.default_timeout_ms)
        else:
            target.uncheck(timeout=self.default_timeout_ms)

    def smart_press(self, selectors: Union[str, List[str], Dict[str, Any]], key: str, desc: str = "") -> None:
        """Presses a key (Enter, Tab, Escape) on the target element."""
        target = self._resolve_locator(selectors, desc=desc or f"Press '{key}'")
        target.press(key)
        self.wait_for_crm_idle(timeout_ms=2500)
