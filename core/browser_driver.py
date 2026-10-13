"""Dedicated Persistent Project Browser Engine for Helper-AI.

Controls a real, visible Chromium browser instance with persistent user data,
allowing the AI to navigate, click buttons, type text, and maintain logged-in sessions.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("ProjectBrowser")

# Persistent profile folder in project workspace
PROJECT_ROOT = Path(__file__).parent.parent
BROWSER_PROFILE_DIR = PROJECT_ROOT / "browser_data"
LOCAL_DRIVER_PATH = PROJECT_ROOT / "drivers" / "chromedriver.exe"


class ProjectBrowser:
    """Singleton Controller for managing a persistent, live Chrome browser."""
    _instance: Optional["ProjectBrowser"] = None
    _driver: Optional[webdriver.Chrome] = None

    @classmethod
    def get_instance(cls) -> "ProjectBrowser":
        if cls._instance is None:
            cls._instance = ProjectBrowser()
        return cls._instance

    def __init__(self):
        BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    def is_alive(self) -> bool:
        if self._driver is None:
            return False
        try:
            handles = self._driver.window_handles
            if not handles:
                self._driver = None
                return False
            try:
                _ = self._driver.title
            except Exception:
                # If current window was closed (e.g. popup closed), switch to remaining valid handle
                self._driver.switch_to.window(handles[-1])
                _ = self._driver.title
            return True
        except Exception:
            self._driver = None
            return False

    def _is_port_open(self, port: int = 9222) -> bool:
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                return s.connect_ex(('127.0.0.1', port)) == 0
        except Exception:
            return False

    def check_connection(self) -> Dict[str, Any]:
        """Checks browser remote debugging and driver session connection health."""
        port_9222 = self._is_port_open(9222)
        alive = self.is_alive()
        return {
            "is_alive": alive,
            "port_9222_open": port_9222,
            "status": "connected" if alive else ("ready_on_port_9222" if port_9222 else "standby")
        }

    def launch_desktop_chrome(self) -> None:
        """Launches Google Chrome on the user's interactive Windows desktop."""
        if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
            logger.info("CI environment detected; skipping desktop Chrome launcher.")
            return

        import subprocess
        logger.info("Attempting to launch interactive desktop Chrome...")
        try:
            # 1. Try launching through scheduled task (runs on user's interactive desktop)
            subprocess.run(["schtasks", "/run", "/tn", "HelperAI_Chrome"], capture_output=True, timeout=5)
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Scheduled task run failed: {e}")

        # If not started, try running launch_chrome.bat directly
        if not self._is_port_open(9222):
            try:
                bat_path = r"C:\Users\DELL\launch_chrome.bat"
                if os.path.exists(bat_path):
                    subprocess.Popen([bat_path], shell=True)
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Direct bat launch failed: {e}")

    def get_driver(self) -> webdriver.Chrome:
        """Returns active driver or connects to visible desktop Chrome."""
        if self.is_alive():
            return self._driver

        is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

        # Local ChromeDriver
        service = None
        if LOCAL_DRIVER_PATH.exists():
            service = Service(executable_path=str(LOCAL_DRIVER_PATH.resolve()))
        else:
            cache_candidates = list((Path.home() / ".cache" / "selenium" / "chromedriver").glob("**/chromedriver.exe"))
            if cache_candidates:
                service = Service(executable_path=str(cache_candidates[0].resolve()))

        # 1. Check if desktop Chrome is running on 9222, or launch it (skip in CI)
        if not is_ci and not self._is_port_open(9222):
            self.launch_desktop_chrome()

        if not is_ci and self._is_port_open(9222):
            opts = Options()
            opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            try:
                if service:
                    self._driver = webdriver.Chrome(service=service, options=opts)
                else:
                    self._driver = webdriver.Chrome(options=opts)
                logger.info("Successfully attached to live desktop Chrome on port 9222.")
                return self._driver
            except Exception as e:
                logger.warning(f"Could not attach to port 9222: {e}")

        # Fallback to starting a fresh instance
        opts = Options()
        if is_ci:
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
        opts.add_argument(f"--user-data-dir={BROWSER_PROFILE_DIR.resolve()}")
        opts.add_argument("--remote-debugging-port=9225")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-default-browser-check")
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        try:
            if service:
                self._driver = webdriver.Chrome(service=service, options=opts)
            else:
                self._driver = webdriver.Chrome(options=opts)
            
            # Mask automation flags
            try:
                self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception:
                pass

            self.bring_to_front()
            return self._driver
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}")
            raise RuntimeError(f"Could not launch project browser: {str(e)}")

    def bring_to_front(self) -> None:
        """Forces the Chrome window to appear in the foreground on Windows."""
        try:
            import win32gui, win32process, win32con, ctypes
            fore_hwnd = win32gui.GetForegroundWindow()
            fore_thread = win32process.GetWindowThreadProcessId(fore_hwnd)[0] if fore_hwnd else 0

            def enum_cb(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Chrome" in title or "Blogger" in title or "Google" in title:
                        app_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                        try:
                            if fore_thread and fore_thread != app_thread:
                                ctypes.windll.user32.AttachThreadInput(fore_thread, app_thread, True)
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(hwnd)
                                ctypes.windll.user32.AttachThreadInput(fore_thread, app_thread, False)
                            else:
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                win32gui.SetForegroundWindow(hwnd)
                        except Exception:
                            pass
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass

    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to the specified URL and brings the window to the front."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        
        driver = self.get_driver()
        driver.get(url)
        time.sleep(1.5)
        self.bring_to_front()
        return self.get_page_summary()

    def click(self, target: str) -> Dict[str, Any]:
        """
        Clicks an element by visible text, aria-label, ID, or CSS selector.
        Automatically handles modern SPAs (Facebook, Twitter, Blogger) with nested spans,
        resolves click interception with JavaScript and ActionChains, and auto-confirms modals.
        """
        driver = self.get_driver()
        initial_handles = list(driver.window_handles)
        before_url = driver.current_url or ""
        target_lower = target.lower().strip()
        import re
        target_clean = re.sub(r"[?!.,:;]+$", "", target_lower).strip()

        # Prioritize exact aria-label, role='button', and button elements using descendant text (.)
        xpath_candidates = [
            f"//*[@role='dialog']//*[@role='button' or self::button][translate(normalize-space(@aria-label), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{target_clean}' or translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{target_clean}']",
            f"//*[@role='button' or self::button][translate(normalize-space(@aria-label), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{target_clean}' or translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{target_clean}']",
            f"//*[@role='dialog']//*[@role='button'][@aria-label and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@role='dialog']//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@role='button'][@aria-label and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@aria-label and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@data-identifier and contains(translate(@data-identifier, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@data-email and contains(translate(@data-email, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//li[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//input[@type='submit' or @type='button'][contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]"
        ]

        element = None
        for xpath in xpath_candidates:
            try:
                found = driver.find_elements(By.XPATH, xpath)
                valid_found = []
                for el in found:
                    try:
                        if el.tag_name.lower() in ["html", "body", "head"]:
                            continue
                        if el.is_displayed():
                            valid_found.append(el)
                    except Exception:
                        continue

                if not valid_found:
                    continue

                # Sort: prioritize exact matches, in-dialog elements, interactive tags, and non-disabled elements
                def score_el(e):
                    try:
                        t = (e.text or "").strip().lower()
                        aria = (e.get_attribute("aria-label") or "").strip().lower()
                        is_interactive = e.tag_name.lower() in ["button", "a", "input"] or e.get_attribute("role") == "button"
                        is_disabled = bool(e.get_attribute("disabled") or e.get_attribute("aria-disabled") == "true")
                        is_exact = (t == target_clean or aria == target_clean)
                        is_in_dialog = driver.execute_script("return arguments[0].closest('[role=\"dialog\"]') !== null;", e)

                        prio = 50 if is_disabled else 0
                        if not is_interactive:
                            prio += 10
                        if is_in_dialog:
                            prio -= 10
                        if is_exact:
                            prio -= 25
                        return (prio, len(t) if t else 9999)
                    except Exception:
                        return (100, 9999)

                valid_found.sort(key=score_el)
                best = valid_found[0]

                # Resolve clickable ancestor if best is span/p/i/div
                try:
                    anc = driver.execute_script("""
                        let el = arguments[0];
                        while (el && el !== document.body) {
                            if (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || el.tagName === 'A') {
                                return el;
                            }
                            el = el.parentElement;
                        }
                        return arguments[0];
                    """, best)
                    element = anc or best
                except Exception:
                    element = best
                break
            except Exception:
                continue

        # Try CSS selector if not found by text
        if not element:
            try:
                el = driver.find_element(By.CSS_SELECTOR, target)
                if el.is_displayed():
                    element = el
            except Exception:
                pass

        # Try JavaScript fuzzy DOM search across interactive buttons and spans
        if not element:
            try:
                js_find = """
                    const query = arguments[0];
                    const elements = Array.from(document.querySelectorAll('button, [role="button"], a, [role="textbox"], span, div'));
                    for (const el of elements) {
                        if (el.offsetParent === null) continue;
                        const txt = (el.innerText || '').toLowerCase();
                        const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                        if (txt.includes(query) || aria.includes(query)) {
                            return el.closest('[role="button"]') || el.closest('button') || el;
                        }
                    }
                    return null;
                """
                element = driver.execute_script(js_find, target_clean)
            except Exception:
                pass

        if not element:
            return {
                "success": False,
                "output": f"Could not find clickable element matching '{target}' on the current page."
            }

        # Scroll into view and click with multi-tier fallback for intercepted clicks
        clicked = False
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            clicked = True
        except Exception as e1:
            # Tier 2: JS Click & Focus
            try:
                driver.execute_script("arguments[0].focus(); arguments[0].click();", element)
                clicked = True
            except Exception:
                # Tier 3: ActionChains move and click
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(driver).move_to_element(element).click().perform()
                    clicked = True
                except Exception as e3:
                    return {
                        "success": False,
                        "output": f"Found '{target}' but click failed: {str(e1)} | {str(e3)}"
                    }

        # If opening new post, wait for editor/composer to load
        if any(k in target_lower for k in ["new post", "create post", "create new post", "what's on your mind", "mind"]):
            for _ in range(8):
                time.sleep(0.5)
                if (
                    "/post/edit/" in (driver.current_url or "")
                    or driver.find_elements(By.XPATH, "//input[@aria-label='Title']")
                    or driver.find_elements(By.XPATH, "//*[@role='dialog']//*[@role='textbox'] | //*[@contenteditable='true']")
                ):
                    break

        # If clicking Publish, auto-confirm any confirmation modal (e.g. Blogger "Publish post? CONFIRM")
        if "publish" in target_lower:
            time.sleep(1.2)
            try:
                confirm_xpath = "//*[@role='dialog']//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirm')] | //*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirm') and @role='button'] | //button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirm')]"
                confirm_btns = [btn for btn in driver.find_elements(By.XPATH, confirm_xpath) if btn.is_displayed()]
                if confirm_btns:
                    driver.execute_script("arguments[0].click();", confirm_btns[0])
                    time.sleep(2.0)
                    return {
                        "success": True,
                        "output": f"Clicked 'Publish' and automatically clicked 'CONFIRM'. Post is officially published!",
                        "page": self.get_page_summary()
                    }
            except Exception:
                pass

        # Check if click opened a new popup/tab (e.g. Google Sign-In or OAuth flow)
        try:
            current_handles = list(driver.window_handles)
            if len(current_handles) > len(initial_handles):
                new_h = [h for h in current_handles if h not in initial_handles]
                target_handle = new_h[-1] if new_h else current_handles[-1]
                driver.switch_to.window(target_handle)
                self.bring_to_front()
                time.sleep(1.2)
        except Exception:
            pass

        # If clicked element was an <a> tag and URL did not change, follow href directly
        try:
            if element and element.tag_name.lower() == "a":
                href = element.get_attribute("href")
                if href and href.startswith("http") and (driver.current_url or "") == before_url:
                    driver.get(href)
                    time.sleep(1.2)
        except Exception:
            pass

        time.sleep(1.0)
        return {
            "success": True,
            "output": f"Clicked element '{target}' successfully.",
            "page": self.get_page_summary()
        }

    def type_text(self, target: str, text: str, press_enter: bool = False, clear: bool = True) -> Dict[str, Any]:
        """
        Types text into an input, textarea, or contenteditable field.
        Robustly supports modern rich editors (Lexical, Draft.js, ProseMirror, Blogger iframes).
        """
        driver = self.get_driver()
        current_url = driver.current_url or ""
        if "accounts.google.com" in current_url:
            self.bring_to_front()
            return {
                "success": False,
                "output": (
                    "⚠️ USER ACTION REQUIRED: Google Sign-In is open in your Project Browser window! "
                    "Google strictly blocks automated typing and requires you to sign in manually. "
                    "Please click the Chrome window on your screen and log in. Once logged in, your session is saved permanently."
                )
            }

        target_lower = target.lower().strip()
        import re
        target_clean = re.sub(r"[?!.,:;]+$", "", target_lower).strip()

        # 1. If targeting body/content in Blogger, prioritize rich text iframe
        if any(k in target_lower for k in ["body", "content", "post body", "editor", "article"]) and "blogger.com" in current_url:
            for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
                try:
                    driver.switch_to.frame(iframe)
                    body_candidates = driver.find_elements(By.XPATH, "//*[@contenteditable='true'] | //body")
                    for b_el in body_candidates:
                        if b_el.is_displayed():
                            b_el.click()
                            if clear:
                                try:
                                    b_el.clear()
                                except Exception:
                                    pass
                            b_el.send_keys(text)
                            driver.switch_to.default_content()
                            return {
                                "success": True,
                                "output": f"Typed '{text[:80]}...' into blog post editor successfully."
                            }
                except Exception:
                    pass
                finally:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

        # 2. If targeting Title, prioritize Title input
        if "title" in target_lower:
            title_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Title' or @placeholder='Title' or contains(@class, 'title')]")
            for t_in in title_inputs:
                if t_in.is_displayed():
                    try:
                        t_in.click()
                        if clear:
                            t_in.clear()
                        t_in.send_keys(text)
                        return {
                            "success": True,
                            "output": f"Typed '{text}' into 'Title' successfully."
                        }
                    except Exception:
                        pass

        # 3. Try XPath for specific placeholder, name, label, textbox, contenteditable
        xpath_candidates = [
            f"//div[contains(@class, 'tiptap') or contains(@class, 'ProseMirror')]",
            f"//*[@role='textbox'][contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@role='textbox'][contains(translate(@aria-placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//p[contains(@class, 'is-editor-empty')]/..",
            f"//input[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//textarea[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//textarea[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_clean}')]",
            f"//*[@role='dialog']//*[@role='textbox' or @contenteditable='true']",
            f"//*[@contenteditable='true']",
            f"//*[@role='textbox']"
        ]

        element = None
        for xpath in xpath_candidates:
            try:
                found = driver.find_elements(By.XPATH, xpath)
                for el in found:
                    if el.is_displayed():
                        element = el
                        break
                if element:
                    break
            except Exception:
                continue

        # Try CSS selector
        if not element:
            try:
                el = driver.find_element(By.CSS_SELECTOR, target)
                if el.is_displayed():
                    element = el
            except Exception:
                pass

        # 4. Fallback: check iframes only if explicitly on Blogger or rich editor iframe
        if not element and ("blogger.com" in current_url or "blog" in current_url):
            for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
                try:
                    driver.switch_to.frame(iframe)
                    body_candidates = driver.find_elements(By.XPATH, "//*[@contenteditable='true'] | //body")
                    for b_el in body_candidates:
                        if b_el.is_displayed():
                            b_el.click()
                            if clear:
                                try:
                                    b_el.clear()
                                except Exception:
                                    pass
                            b_el.send_keys(text)
                            driver.switch_to.default_content()
                            return {
                                "success": True,
                                "output": f"Typed text into rich text editor inside iframe successfully."
                            }
                except Exception:
                    pass
                finally:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

        if not element:
            return {
                "success": False,
                "output": f"Could not find input field matching '{target}' to type text."
            }

        # Multi-tier typing handling
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.2)
            # Focus and click (safely catching intercept issues)
            try:
                element.click()
            except Exception:
                try:
                    driver.execute_script("arguments[0].focus(); arguments[0].click();", element)
                except Exception:
                    pass

            is_contenteditable = (
                element.get_attribute("contenteditable") == "true"
                or element.get_attribute("role") == "textbox"
                or element.tag_name in ["div", "span", "p"]
            )

            if clear:
                if is_contenteditable:
                    try:
                        element.send_keys(Keys.CONTROL + "a")
                        element.send_keys(Keys.BACKSPACE)
                    except Exception:
                        try:
                            driver.execute_script("arguments[0].innerText = '';", element)
                        except Exception:
                            pass
                else:
                    try:
                        element.clear()
                    except Exception:
                        pass

            # Type text: Tier 1 send_keys
            typed = False
            try:
                element.send_keys(text)
                typed = True
            except Exception:
                # Tier 2 ActionChains
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(driver).move_to_element(element).click().send_keys(text).perform()
                    typed = True
                except Exception:
                    # Tier 3 document.execCommand for Lexical / contenteditable
                    try:
                        driver.execute_script("""
                            const el = arguments[0];
                            const val = arguments[1];
                            el.focus();
                            document.execCommand('selectAll', false, null);
                            document.execCommand('insertText', false, val);
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        """, element, text)
                        typed = True
                    except Exception as e3:
                        return {
                            "success": False,
                            "output": f"Failed to type into '{target}': {str(e3)}"
                        }

            if press_enter:
                try:
                    element.send_keys(Keys.RETURN)
                except Exception:
                    pass

            time.sleep(0.5)
            return {
                "success": True,
                "output": f"Typed '{text[:80]}...' into '{target}' successfully."
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Failed to type into '{target}': {str(e)}"
            }

    def get_page_summary(self) -> Dict[str, Any]:
        """Extracts current URL, title, and interactive buttons/inputs on screen (including role=button and contenteditable)."""
        try:
            driver = self.get_driver()
        except Exception:
            return {"title": "No Browser Open", "url": "", "buttons": [], "inputs": []}

        driver = self._driver
        title = driver.title or ""
        url = driver.current_url or ""

        def _clean(val: str) -> str:
            if not val:
                return ""
            # Strip non-ASCII or private-use icon glyphs
            cleaned = "".join(c for c in val if ord(c) < 128 or c.isprintable() and not (0xE000 <= ord(c) <= 0xF8FF)).strip()
            import re
            return re.sub(r"\s+", " ", cleaned).strip()

        # Extract visible buttons: <button> AND [role='button']
        buttons = []
        found_btns = driver.find_elements(By.XPATH, "//button | //*[@role='button'] | //input[@type='submit' or @type='button']")
        for btn in found_btns[:30]:
            try:
                if btn.is_displayed():
                    txt = _clean(btn.text)
                    aria = _clean(btn.get_attribute("aria-label") or "")
                    candidate = txt or aria
                    if candidate and len(candidate) < 60 and candidate not in buttons:
                        buttons.append(candidate)
            except Exception:
                pass

        # Extract visible links with text
        links = []
        for a in driver.find_elements(By.TAG_NAME, "a")[:20]:
            try:
                if a.is_displayed() and a.text.strip() and len(a.text.strip()) < 30:
                    txt = _clean(a.text)
                    if txt and txt not in links:
                        links.append(txt)
            except Exception:
                pass

        # Extract visible inputs: input, textarea, role=textbox, contenteditable
        inputs = []
        found_inputs = driver.find_elements(By.XPATH, "//input | //textarea | //*[@role='textbox'] | //*[@contenteditable='true']")
        for inp in found_inputs[:15]:
            try:
                if inp.is_displayed():
                    ph = (
                        inp.get_attribute("aria-placeholder")
                        or inp.get_attribute("placeholder")
                        or inp.get_attribute("aria-label")
                        or inp.get_attribute("name")
                        or inp.get_attribute("type")
                        or "textbox"
                    )
                    txt = _clean(ph)
                    if txt and txt not in inputs:
                        inputs.append(txt)
            except Exception:
                pass

        # Full body text extraction
        body_text = ""
        if "accounts.google.com" in url or "signin" in url.lower():
            self.bring_to_front()
            body_text = "⚠️ [GOOGLE SIGN-IN ACTIVE]: Waiting for the user to sign into their Google Account directly in the browser window. Do not submit automated credentials."
        else:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body_raw = body.text or ""
                # Preserve paragraph structure while cleaning excessive whitespace
                lines = [l.strip() for l in body_raw.splitlines() if l.strip()]
                body_text = "\n".join(lines[:120])  # Up to 120 readable lines
            except Exception:
                pass

        return {
            "title": _clean(title),
            "url": url,
            "buttons": buttons[:20],
            "links": links[:15],
            "inputs": inputs[:15],
            "snippet": body_text[:3000]
        }

    def get_full_page_content(self, max_chars: int = 25000) -> Dict[str, Any]:
        """Extracts complete readable webpage content including text, headings, links, and forms."""
        driver = self.get_driver()
        title = driver.title or ""
        url = driver.current_url or ""

        # Extract headings, links, and text via JavaScript
        data = driver.execute_script("""
            const headings = Array.from(document.querySelectorAll('h1, h2, h3'))
                .map(h => (h.innerText || '').trim())
                .filter(h => h.length > 0 && h.length < 120);

            const links = Array.from(document.querySelectorAll('a[href]'))
                .map(a => ({text: (a.innerText || '').trim(), href: a.href}))
                .filter(l => l.text.length > 1 && l.text.length < 80 && !l.href.startsWith('javascript:'))
                .slice(0, 30);

            const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'))
                .map(b => (b.innerText || b.getAttribute('aria-label') || '').trim())
                .filter(b => b.length > 0 && b.length < 60)
                .slice(0, 30);

            const inputs = Array.from(document.querySelectorAll('input, textarea, select'))
                .map(i => ({
                    tag: i.tagName.toLowerCase(),
                    type: i.type || 'text',
                    name: i.name || '',
                    placeholder: i.placeholder || i.getAttribute('aria-label') || '',
                    value: i.value || ''
                }))
                .slice(0, 20);

            // Get clean body text
            let bodyText = document.body ? document.body.innerText : '';
            return {
                headings: headings,
                links: links,
                buttons: buttons,
                inputs: inputs,
                bodyText: bodyText
            };
        """)

        body_text = data.get("bodyText", "")
        # Clean blank lines
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]
        clean_text = "\n".join(lines)
        if max_chars and len(clean_text) > max_chars:
            trimmed_text = clean_text[:max_chars] + f"\n\n... [Content truncated at {max_chars} characters. Total page length: {len(clean_text)} characters]"
        else:
            trimmed_text = clean_text

        return {
            "title": title,
            "url": url,
            "total_characters": len(clean_text),
            "headings": data.get("headings", [])[:15],
            "links": data.get("links", [])[:25],
            "buttons": data.get("buttons", [])[:25],
            "inputs": data.get("inputs", [])[:15],
            "content": trimmed_text
        }

    def scroll(self, direction: str = "down", pixels: int = 800) -> Dict[str, Any]:
        """Scrolls the current webpage down or up."""
        driver = self.get_driver()
        dy = pixels if direction.lower() in ["down", "bottom"] else -pixels
        if direction.lower() == "bottom":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif direction.lower() == "top":
            driver.execute_script("window.scrollTo(0, 0);")
        else:
            driver.execute_script(f"window.scrollBy(0, {dy});")
        time.sleep(1.0)
        return {
            "success": True,
            "output": f"Scrolled page {direction} by {pixels} pixels."
        }

    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Takes a screenshot of the current browser tab and saves it."""
        from pathlib import Path
        driver = self.get_driver()
        sc_dir = Path("screenshots")
        sc_dir.mkdir(parents=True, exist_ok=True)
        fn = filename or f"browser_{int(time.time())}.png"
        out_path = sc_dir / fn
        driver.save_screenshot(str(out_path))
        return {
            "success": True,
            "output": f"Browser screenshot saved to '{out_path.resolve()}'.",
            "file_path": str(out_path.resolve())
        }

    def select_dropdown_option(self, target: str, option_text: str) -> Dict[str, Any]:
        """Selects an option from a dropdown or <select> element."""
        driver = self.get_driver()
        res = driver.execute_script("""
            const target = arguments[0].toLowerCase();
            const optionText = arguments[1].toLowerCase();
            
            const selects = Array.from(document.querySelectorAll('select'));
            let found = null;
            for (let s of selects) {
                const name = (s.name || '').toLowerCase();
                const id = (s.id || '').toLowerCase();
                const aria = (s.getAttribute('aria-label') || '').toLowerCase();
                if (name.includes(target) || id.includes(target) || aria.includes(target)) {
                    found = s;
                    break;
                }
            }
            if (!found && selects.length > 0) found = selects[0];
            if (!found) return {success: false, error: 'No matching <select> element found'};

            for (let i = 0; i < found.options.length; i++) {
                const opt = found.options[i];
                if ((opt.text || '').toLowerCase().includes(optionText) || (opt.value || '').toLowerCase().includes(optionText)) {
                    found.selectedIndex = i;
                    found.dispatchEvent(new Event('change', { bubbles: true }));
                    found.dispatchEvent(new Event('input', { bubbles: true }));
                    return {success: true, selected: opt.text};
                }
            }
            return {success: false, error: 'Option not found in dropdown'};
        """, target, option_text)
        return res

    def list_tabs(self) -> Dict[str, Any]:
        """Lists all open browser tabs and windows."""
        driver = self.get_driver()
        handles = list(driver.window_handles)
        current_handle = driver.current_window_handle
        tabs = []
        for i, h in enumerate(handles):
            try:
                driver.switch_to.window(h)
                tabs.append({
                    "index": i,
                    "title": driver.title,
                    "url": driver.current_url,
                    "is_current": (h == current_handle)
                })
            except Exception:
                pass
        try:
            driver.switch_to.window(current_handle)
        except Exception:
            if handles:
                driver.switch_to.window(handles[-1])

        summary = "\n".join(f"Tab {t['index']}: '{t['title']}' ({t['url']}){' [ACTIVE]' if t['is_current'] else ''}" for t in tabs)
        return {
            "success": True,
            "tabs": tabs,
            "total_tabs": len(tabs),
            "output": f"Found {len(tabs)} open browser tab(s):\n{summary}"
        }

    def switch_tab(self, target: Any) -> Dict[str, Any]:
        """Switches to a browser tab by numeric index (0, 1, 2) or title/URL keyword."""
        driver = self.get_driver()
        handles = list(driver.window_handles)
        if not handles:
            return {"success": False, "output": "No open browser tabs found."}

        target_str = str(target).lower().strip()
        matched_handle = None

        if target_str.isdigit():
            idx = int(target_str)
            if 0 <= idx < len(handles):
                matched_handle = handles[idx]

        if not matched_handle:
            for h in handles:
                try:
                    driver.switch_to.window(h)
                    if target_str in driver.title.lower() or target_str in driver.current_url.lower():
                        matched_handle = h
                        break
                except Exception:
                    pass

        if matched_handle:
            driver.switch_to.window(matched_handle)
            self.bring_to_front()
            time.sleep(0.5)
            return {
                "success": True,
                "output": f"Switched to tab '{driver.title}' ({driver.current_url}).",
                "page": self.get_page_summary()
            }

        return {
            "success": False,
            "output": f"Could not find any tab matching '{target}'."
        }

    def close_tab(self, target: Optional[Any] = None) -> Dict[str, Any]:
        """Closes a specific tab or the current tab."""
        driver = self.get_driver()
        handles = list(driver.window_handles)
        if len(handles) <= 1:
            return {"success": False, "output": "Cannot close the only open tab."}

        if target:
            self.switch_tab(target)

        closed_title = driver.title
        driver.close()
        time.sleep(0.5)
        rem = driver.window_handles
        if rem:
            driver.switch_to.window(rem[-1])
        return {
            "success": True,
            "output": f"Closed tab '{closed_title}'. Switched back to '{driver.title}'.",
            "page": self.get_page_summary()
        }

    def close(self) -> None:
        """Closes browser window."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
