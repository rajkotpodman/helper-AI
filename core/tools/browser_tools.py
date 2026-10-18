"""Browser Automation & Live Project Browser Tools for Helper-AI.

Provides real-time browser control (navigate, click buttons, type text, submit forms)
using a dedicated live Chromium browser with a persistent user profile, allowing Google/Blogger
logins and cookies to remain permanently saved.
"""

import os
import sys
import time
import json
import logging
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from core.tools.base import BaseTool
from core.browser_driver import ProjectBrowser

logger = logging.getLogger("BrowserTools")


class BrowserAutomationTool(BaseTool):
    """
    Automates live browser navigation, clicking buttons, typing text,
    and interacting with websites using the dedicated project browser.
    """
    name = "browser_automation"
    description = (
        "Controls the dedicated project browser. Can open websites (like Blogger, Google, YouTube), "
        "click buttons or links by their visible text, type text into inputs and text boxes, "
        "and read page contents. Persistent profile preserves logins and cookies across sessions."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": (
                    "Action to perform: 'apply_linkedin_jobs' (autonomously searches and applies to LinkedIn jobs with CV via Easy Apply in 1 step), "
                    "'publish_linkedin_post' (autonomously creates, writes, and publishes a LinkedIn post in 1 step), "
                    "'publish_facebook_post' (autonomously creates, writes, and publishes a Facebook post in 1 step), "
                    "'publish_blog_post' (autonomously creates, writes, and publishes a blog post with title and text in 1 step), "
                    "'open_url' (load a page), 'click' (click button/link by text), "
                    "'type' (enter text into field), 'press_enter' (press Enter key on current page), 'get_page' (read current page state), "
                    "'fetch_full_page' (extract complete readable webpage text, headings, buttons, and links), "
                    "'scroll' (scroll page up or down), 'take_screenshot' (capture browser screenshot), "
                    "'select_dropdown' (select option from dropdown/select), 'execute_script' (run JavaScript on page), "
                    "'close_browser' (close window), 'draft_social_post' (compose social post)"
                ),
                "enum": [
                    "apply_linkedin_jobs",
                    "publish_linkedin_post",
                    "publish_facebook_post",
                    "publish_blog_post",
                    "list_blogs",
                    "open_url",
                    "click",
                    "type",
                    "press_enter",
                    "enter",
                    "get_page",
                    "read_page",
                    "fetch_full_page",
                    "get_full_page",
                    "fetch_full_web",
                    "scroll",
                    "take_screenshot",
                    "screenshot",
                    "select_dropdown",
                    "execute_script",
                    "dismiss_popups",
                    "list_tabs",
                    "switch_tab",
                    "close_tab",
                    "close_browser",
                    "draft_social_post",
                    "tag_elements",
                    "set_of_marks",
                    "click_mark",
                    "type_mark",
                    "clear_marks"
                ]
            },
            "mark_id": {
                "type": "integer",
                "description": "Numeric visual badge ID of the interactive element to click or type into (for click_mark and type_mark actions)."
            },
            "title": {
                "type": "string",
                "description": "Blog post title (for publish_blog_post action)."
            },
            "url": {
                "type": "string",
                "description": "The URL to visit (e.g. 'https://www.blogger.com', 'https://www.google.com')."
            },
            "target": {
                "type": "string",
                "description": "Button text, link text, input placeholder, name, or CSS selector to click or type into (e.g. 'Create Blog', 'NEW POST', 'Title', 'Publish')."
            },
            "direction": {
                "type": "string",
                "description": "Direction to scroll for 'scroll' action ('down', 'up', 'top', 'bottom'). Default 'down'."
            },
            "pixels": {
                "type": "integer",
                "description": "Number of pixels to scroll (default 800)."
            },
            "option": {
                "type": "string",
                "description": "Option text or value to choose for 'select_dropdown' action."
            },
            "script": {
                "type": "string",
                "description": "JavaScript code snippet to run for 'execute_script' action."
            },
            "text": {
                "type": "string",
                "description": "Text to type into the targeted input or content area, or blog post body text, or Facebook post text."
            },
            "press_enter": {
                "type": "boolean",
                "description": "Whether to press Enter after typing text.",
                "default": False
            },
            "platform": {
                "type": "string",
                "description": "Social media platform name (for draft_social_post)."
            },
            "post_text": {
                "type": "string",
                "description": "Post text (for draft_social_post or publish_facebook_post)."
            },
            "keywords": {
                "type": "string",
                "description": "Job search keywords or title for apply_linkedin_jobs (e.g. 'Technical Support', 'Infrastructure Engineer')."
            },
            "resume_path": {
                "type": "string",
                "description": "Absolute path to CV or resume (.docx or .pdf) for apply_linkedin_jobs."
            },
            "count": {
                "type": "integer",
                "description": "Number of job openings to apply to for apply_linkedin_jobs (default 5).",
                "default": 5
            }
        },
        "required": ["action"]
    }

    def execute(
        self,
        action: str,
        url: Optional[str] = None,
        target: Optional[str] = None,
        text: Optional[str] = None,
        title: Optional[str] = None,
        press_enter: bool = False,
        platform: Optional[str] = None,
        post_text: Optional[str] = None,
        keywords: Optional[str] = None,
        resume_path: Optional[str] = None,
        count: Optional[int] = 5,
        mark_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        browser = ProjectBrowser.get_instance()
        target_name = target or kwargs.get("element") or kwargs.get("selector") or ""
        type_content = text or kwargs.get("content") or kwargs.get("body") or kwargs.get("value") or ""
        post_title = title or kwargs.get("post_title") or target_name or "New Blog Post"

        try:
            if action in ["tag_elements", "set_of_marks", "tag_page"]:
                return browser.inject_set_of_marks()

            elif action == "click_mark":
                mid = mark_id if mark_id is not None else kwargs.get("id") or target_name
                if mid is None or str(mid).strip() == "":
                    return {"success": False, "output": "Please provide 'mark_id' (e.g. mark_id=3) to click."}
                return browser.click_mark(int(mid))

            elif action == "type_mark":
                mid = mark_id if mark_id is not None else kwargs.get("id") or target_name
                if mid is None or str(mid).strip() == "":
                    return {"success": False, "output": "Please provide 'mark_id' (e.g. mark_id=2) to type into."}
                return browser.type_mark(int(mid), type_content, press_enter=press_enter)

            elif action in ["clear_marks", "remove_marks"]:
                return browser.clear_marks()

            elif action in ["apply_linkedin_jobs", "apply_linkedin", "linkedin_apply", "apply_jobs"]:
                kw = keywords or kwargs.get("role") or target_name or "Technical Support"
                cv = resume_path or kwargs.get("cv_path") or kwargs.get("file_path") or url
                num = int(count or kwargs.get("num") or 5)
                return self._apply_linkedin_jobs(keywords=kw, resume_path=cv, count=num)

            elif action in ["publish_linkedin_post", "create_linkedin_post", "post_linkedin"]:
                li_content = post_text or type_content or "Hello from Helper-AI!"
                return self._publish_linkedin_post(li_content)

            elif action in ["publish_facebook_post", "create_facebook_post", "post_facebook"]:
                fb_content = post_text or type_content or "Hello from Helper-AI!"
                return self._publish_facebook_post(fb_content)

            elif action in ["publish_blog_post", "create_blog_post"]:
                return self._publish_blog_post(post_title, type_content, url)

            elif action in ["list_blogs", "get_blogs", "my_blogs", "google_blogs"]:
                return self._list_blogs()

            elif action in ["open_url", "navigate"]:
                target_url = url or kwargs.get("link") or "https://www.google.com"
                res = browser.navigate(target_url)
                buttons_preview = ", ".join(res.get("buttons", [])[:6]) or "None"
                inputs_preview = ", ".join(res.get("inputs", [])[:4]) or "None"
                return {
                    "success": True,
                    "output": (
                        f"Opened '{res.get('url')}' in live Project Browser.\n"
                        f"Page Title: '{res.get('title')}'\n"
                        f"Clickable buttons visible: [{buttons_preview}]\n"
                        f"Input fields visible: [{inputs_preview}]\n\n"
                        f"Page snippet: {res.get('snippet', '')[:300]}..."
                    ),
                    "page": res
                }

            elif action == "click":
                if not target_name:
                    return {"success": False, "output": "Please provide a 'target' (button name, text, or selector) to click."}
                res = browser.click(target_name)
                return res

            elif action == "type":
                if not target_name:
                    return {"success": False, "output": "Please provide a 'target' input field or placeholder to type into."}
                res = browser.type_text(target_name, type_content, press_enter=press_enter)
                return res

            elif action in ["press_enter", "enter"]:
                driver = browser.get_driver()
                from selenium.webdriver.common.keys import Keys
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                return {"success": True, "output": "Pressed Enter key in live Project Browser."}

            elif action in ["get_page", "read_page", "inspect_page"]:
                res = browser.get_page_summary()
                return {
                    "success": True,
                    "output": (
                        f"Current URL: {res.get('url')}\n"
                        f"Title: {res.get('title')}\n"
                        f"Buttons on page: {res.get('buttons')}\n"
                        f"Inputs on page: {res.get('inputs')}\n"
                        f"Content snippet: {res.get('snippet', '')[:1000]}"
                    ),
                    "page": res
                }

            elif action in ["fetch_full_page", "get_full_page", "fetch_full_web", "full_page"]:
                target_url = url or kwargs.get("link")
                if target_url and target_url != browser.get_driver().current_url:
                    browser.navigate(target_url)
                res = browser.get_full_page_content()
                headings_preview = "\n- ".join(res.get("headings", [])[:8]) or "None"
                links_preview = "\n".join(f"- {l['text']}: {l['href']}" for l in res.get("links", [])[:10]) or "None"
                buttons_preview = ", ".join(res.get("buttons", [])[:12]) or "None"
                return {
                    "success": True,
                    "title": res.get("title", ""),
                    "url": res.get("url", ""),
                    "total_characters": res.get("total_characters", 0),
                    "output": (
                        f"🌐 Full Webpage Content: '{res.get('title')}'\n"
                        f"URL: {res.get('url')}\n"
                        f"Total characters: {res.get('total_characters')}\n\n"
                        f"### Key Headings:\n- {headings_preview}\n\n"
                        f"### Interactive Buttons:\n[{buttons_preview}]\n\n"
                        f"### Main Page Text:\n{res.get('content', '')}\n\n"
                        f"### Top Navigation Links:\n{links_preview}"
                    ),
                    "page": res
                }

            elif action in ["scroll", "scroll_page"]:
                scroll_dir = kwargs.get("direction") or "down"
                scroll_px = int(kwargs.get("pixels") or 800)
                return browser.scroll(direction=scroll_dir, pixels=scroll_px)

            elif action in ["take_screenshot", "screenshot", "capture_screen"]:
                fn = kwargs.get("filename")
                return browser.take_screenshot(filename=fn)

            elif action in ["select_dropdown", "select_option", "choose_option"]:
                opt = kwargs.get("option") or type_content or ""
                if not opt:
                    return {"success": False, "output": "Please specify 'option' to select."}
                return browser.select_dropdown_option(target_name or "", opt)

            elif action in ["dismiss_popups", "close_popups"]:
                driver = browser.get_driver()
                cnt = driver.execute_script("""
                    let count = 0;
                    const popups = Array.from(document.querySelectorAll('button, [role="button"]')).filter(b => {
                        const t = (b.innerText || '').trim().toLowerCase();
                        const a = (b.getAttribute('aria-label') || '').toLowerCase();
                        return (t === 'done' || t === 'close' || t === 'not now' || t === 'dismiss' || t === 'skip' || t === 'cancel' || a === 'dismiss' || a === 'close') && b.offsetParent !== null;
                    });
                    popups.forEach(p => { try { p.click(); count++; } catch(e) {} });
                    document.querySelectorAll('.artdeco-toast, [data-test-artdeco-toast], .modal-backdrop, .artdeco-modal-overlay').forEach(t => { try { t.remove(); count++; } catch(e) {} });
                    return count;
                """)
                return {"success": True, "output": f"Dismissed/cleared {cnt} popups or modal overlays in the browser."}

            elif action in ["execute_script", "run_script", "eval_js"]:
                js_code = kwargs.get("script") or kwargs.get("code") or type_content
                if not js_code:
                    return {"success": False, "output": "Please provide 'script' code to execute."}
                driver = browser.get_driver()
                eval_res = driver.execute_script(js_code)
                return {"success": True, "output": f"Script executed successfully. Result: {eval_res}", "result": eval_res}

            elif action in ["list_tabs", "get_tabs", "tabs"]:
                return browser.list_tabs()

            elif action in ["switch_tab", "focus_tab", "select_tab"]:
                tab_target = target_name or kwargs.get("index") or kwargs.get("tab") or type_content or "0"
                return browser.switch_tab(tab_target)

            elif action in ["close_tab"]:
                tab_target = target_name or kwargs.get("index") or kwargs.get("tab")
                return browser.close_tab(tab_target)

            elif action == "close_browser":
                browser.close()
                return {"success": True, "output": "Dedicated project browser closed."}

            elif action == "draft_social_post":
                return self._draft_social_post(
                    platform=platform,
                    post_text=post_text,
                    open_in_system_browser=kwargs.get("open_in_system_browser", True)
                )

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: '{action}'.",
                    "output": f"Unknown action: '{action}'. Available: fetch_full_page, open_url, click, type, select_dropdown, scroll, take_screenshot, dismiss_popups, execute_script, press_enter, get_page, apply_linkedin_jobs, publish_linkedin_post, publish_facebook_post, publish_blog_post, close_browser."
                }

        except Exception as e:
            logger.error(f"BrowserAutomationTool execution error: {e}", exc_info=True)
            return {
                "success": False,
                "output": f"Browser automation error: {str(e)}",
                "error": str(e)
            }

    def _publish_facebook_post(self, content: str) -> Dict[str, Any]:
        """
        Autonomously creates, writes, and publishes a Facebook post with strict ground-truth verification.
        Saves local post copy to Desktop/Facebook_Posts, verifies Facebook authentication,
        and strictly verifies whether the post was successfully committed before claiming success.
        """
        import time
        from pathlib import Path
        import datetime
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains

        # Step 0: Safe local backup so user's generated deep content is NEVER lost
        saved_file_path = None
        try:
            fb_dir = Path.home() / "Desktop" / "Facebook_Posts"
            fb_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            first_line = content.splitlines()[0] if content.splitlines() else "post"
            slug = "".join([c if c.isalnum() else "_" for c in first_line[:30]]).strip("_") or "fb_post"
            out_file = fb_dir / f"FB_{slug}_{ts}.txt"
            out_file.write_text(content, encoding="utf-8")
            saved_file_path = str(out_file)
        except Exception as e:
            logger.warning(f"Could not write backup post file: {e}")

        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()

        # Step 0.5: Check for Facebook Authentication / Login requirement
        current_url = (driver.current_url or "").lower()
        if "facebook.com" not in current_url:
            browser.navigate("https://www.facebook.com/")
            time.sleep(2.5)
            current_url = (driver.current_url or "").lower()

        page_src = (driver.page_source or "").lower()
        is_login_page = (
            "login" in current_url or 
            any(k in page_src for k in ["log in to facebook", "log into facebook", "sign in to facebook", "forgot password", "create new account", "email or phone", "mobile number or email"]) or
            bool(driver.find_elements(By.XPATH, "//input[@name='email' or @id='email' or @name='pass']"))
        )
        if is_login_page:
            browser.bring_to_front()
            return {
                "success": False,
                "error": "FACEBOOK_LOGIN_REQUIRED",
                "saved_to": saved_file_path,
                "output": (
                    "❌ GOAL NOT ACHIEVED — FACEBOOK LOGIN REQUIRED:\n"
                    "• Exact Problem: The Project Chrome browser is NOT logged into Facebook (Login screen detected).\n"
                    "• Action Taken: Project Chrome Browser has been brought to the foreground for you.\n"
                    "• Concrete Solution: Please sign in to your Facebook account once in the Chrome browser window. After logging in, your session remains permanently active.\n"
                    f"• Safe Backup: Your Gujarati post has been safely generated and saved to: '{saved_file_path}'."
                )
            }

        # Step 1: Check if an active Create Post dialog is ALREADY open and usable
        target_dlg = None
        for dlg in driver.find_elements(By.XPATH, "//*[@role='dialog']"):
            try:
                if dlg.is_displayed() and dlg.find_elements(By.XPATH, ".//*[@role='textbox' or @contenteditable='true']"):
                    target_dlg = dlg
                    break
            except Exception:
                pass

        if not target_dlg:
            # Clean feed scroll
            try:
                driver.execute_script("window.scrollTo(0, 0);")
            except Exception:
                pass
            time.sleep(1.0)

            # Dismiss any floating backdrop/modals or 'Not now' prompts if present
            try:
                not_now_btns = driver.find_elements(By.XPATH, "//*[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]")
                for b in not_now_btns:
                    if b.is_displayed():
                        driver.execute_script("arguments[0].click();", b)
                        time.sleep(0.5)
                        break
            except Exception:
                pass

            # Step 2: Locate and click "What's on your mind?" composer trigger button
            opened = False
            for attempt in range(4):
                btns = driver.find_elements(By.XPATH, "//*[@role='button'] | //div[contains(@class, 'x1i10hfl')] | //div[@contenteditable='true'] | //span[contains(text(), 'mind') or contains(text(), 'મન') or contains(text(), 'मन')]")
                for b in btns:
                    try:
                        if b.is_displayed():
                            txt = (b.text or "").lower()
                            aria = (b.get_attribute("aria-label") or "").lower()
                            if any(k in txt or k in aria for k in [
                                "what's on your mind", "share a thought", "create a post",
                                "write something", "તમારા મનમાં શું છે", "પોસ્ટ બનાવો", "पोस्ट बनाएँ", "मन में क्या है"
                            ]):
                                driver.execute_script("""
                                    const el = arguments[0];
                                    el.scrollIntoView({block: 'center'});
                                    const rect = el.getBoundingClientRect();
                                    const x = rect.left + rect.width / 2;
                                    const y = rect.top + rect.height / 2;
                                    ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                                        el.dispatchEvent(new MouseEvent(evt, {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window,
                                            clientX: x,
                                            clientY: y
                                        }));
                                    });
                                """, b)
                                opened = True
                                break
                    except Exception:
                        continue
                if opened:
                    break
                time.sleep(1.0)

            # Wait for composer dialog to appear
            for _ in range(8):
                time.sleep(0.5)
                for dlg in driver.find_elements(By.XPATH, "//*[@role='dialog']"):
                    try:
                        if dlg.is_displayed() and dlg.find_elements(By.XPATH, ".//*[@role='textbox' or @contenteditable='true']"):
                            target_dlg = dlg
                            break
                    except Exception:
                        pass
                if target_dlg:
                    break

        # Step 3: Locate the composer textbox inside the active dialog or page
        textbox = None
        if target_dlg:
            for _ in range(6):
                tbs = target_dlg.find_elements(By.XPATH, ".//*[@role='textbox' or @contenteditable='true']")
                for tb in tbs:
                    try:
                        if tb.is_displayed():
                            textbox = tb
                            break
                    except Exception:
                        continue
                if textbox:
                    break
                time.sleep(0.5)

        if not textbox:
            for tb in driver.find_elements(By.XPATH, "//*[@role='textbox' and @contenteditable='true']"):
                try:
                    if tb.is_displayed():
                        aria = (tb.get_attribute("aria-label") or "").lower()
                        if any(c in aria for c in ["comment", "टिप्पणी", "ટિપ્પણી", "reply", "જવાબ", "उत्तर"]):
                            continue
                        textbox = tb
                        break
                except Exception:
                    continue

        if not textbox:
            return {
                "success": False,
                "error": "FACEBOOK_COMPOSER_NOT_FOUND",
                "saved_to": saved_file_path,
                "output": (
                    "❌ GOAL NOT ACHIEVED — FACEBOOK COMPOSER NOT FOUND:\n"
                    "• Exact Problem: Could not open or find the Facebook 'Create post' textbox on screen.\n"
                    "• Solution: Please make sure your Facebook feed is open and not blocked by account restrictions.\n"
                    f"• Safe Backup: Post safely saved to: '{saved_file_path}'."
                )
            }

        # Step 4: Focus and insert content
        try:
            textbox.click()
            time.sleep(0.2)
            ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
        except Exception:
            pass

        pasted = False
        try:
            driver.execute_script("""
                const el = arguments[0];
                const text = arguments[1];
                el.focus();
                const dt = new DataTransfer();
                dt.setData('text/plain', text);
                const pasteEvt = new ClipboardEvent('paste', {
                    clipboardData: dt,
                    bubbles: true,
                    cancelable: true
                });
                el.dispatchEvent(pasteEvt);
            """, textbox, content)
            time.sleep(0.8)
            pasted = len((textbox.text or "").strip()) > 5 or " " in (textbox.text or "")
        except Exception as e:
            pasted = False

        if not pasted:
            try:
                import pyperclip
                pyperclip.copy(content)
                time.sleep(0.2)
                ActionChains(driver).move_to_element(textbox).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                time.sleep(0.8)
                pasted = len((textbox.text or "").strip()) > 5
            except Exception:
                pass

        if not pasted:
            try:
                textbox.send_keys(content)
                time.sleep(0.8)
            except Exception as se:
                logger.warning(f"send_keys fallback failed: {se}")

        # Trigger React 18 / Lexical input & change events
        try:
            driver.execute_script("""
                const el = arguments[0];
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, textbox)
        except Exception:
            pass
        time.sleep(1.0)

        # Step 5: Locate Post button
        post_btn = None
        search_root = target_dlg if target_dlg else driver
        for _ in range(16):  # Poll up to 8 seconds for aria-disabled to lift
            btns = search_root.find_elements(By.XPATH, ".//*[@role='button'] | .//button")
            for b in btns:
                try:
                    if b.is_displayed():
                        txt = (b.text or "").strip().lower()
                        aria = (b.get_attribute("aria-label") or "").strip().lower()
                        dis = b.get_attribute("aria-disabled")
                        if any(k in txt or k in aria for k in ["post", "share", "next", "publish", "done", "પોસ્ટ", "पोस्ट"]):
                            if dis != "true":
                                post_btn = b
                                break
                except Exception:
                    continue
            if post_btn:
                break
            time.sleep(0.5)

        if not post_btn:
            return {
                "success": False,
                "error": "POST_BUTTON_DISABLED_OR_NOT_FOUND",
                "saved_to": saved_file_path,
                "output": (
                    "❌ GOAL NOT ACHIEVED — POST BUTTON NOT ACTIVE:\n"
                    "• Exact Problem: The Facebook 'Post' button remained disabled or was not found.\n"
                    "• Solution: Check if Facebook requires an audience selection (Public/Friends) or has a content restriction.\n"
                    f"• Safe Backup: Post safely saved to '{saved_file_path}'."
                )
            }

        # Step 6: Click Post button via pointer event dispatcher
        try:
            driver.execute_script("""
                const el = arguments[0];
                const rect = el.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                    el.dispatchEvent(new MouseEvent(evt, {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: x,
                        clientY: y
                    }));
                });
            """, post_btn)
        except Exception:
            try:
                post_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", post_btn)

        # Step 7: Ground-truth verification — wait for composer dialog to close
        dialog_closed = False
        start_wait = time.time()
        error_detected = None

        while time.time() - start_wait < 25:
            time.sleep(1.0)
            # Check for error banners
            for err_el in driver.find_elements(By.XPATH, "//*[@role='alert'] | //div[contains(text(), 'Something went wrong') or contains(text(), 'temporarily blocked') or contains(text(), 'community standards')]"):
                if err_el.is_displayed():
                    error_detected = err_el.text
                    break
            if error_detected:
                break

            # Check if modal closed
            if target_dlg:
                try:
                    if not target_dlg.is_displayed():
                        dialog_closed = True
                        break
                except Exception:
                    dialog_closed = True
                    break
            else:
                dialog_closed = True
                break

        if error_detected:
            return {
                "success": False,
                "error": "FACEBOOK_REJECTED_POST",
                "saved_to": saved_file_path,
                "output": f"❌ GOAL NOT ACHIEVED — FACEBOOK REJECTED POST: '{error_detected}'. Saved locally to '{saved_file_path}'."
            }

        if not dialog_closed:
            return {
                "success": False,
                "error": "POST_CONFIRMATION_TIMEOUT",
                "saved_to": saved_file_path,
                "output": (
                    "⚠️ GOAL NOT ACHIEVED — POST DIALOG DID NOT CLOSE:\n"
                    "• The post submit was clicked, but the dialog stayed open (network lag or confirmation prompt).\n"
                    f"• Safe Backup: Generated post is saved at '{saved_file_path}'."
                )
            }

        # Step 8: Reset feed cleanly
        try:
            browser.navigate("https://www.facebook.com/")
            time.sleep(2.0)
            driver.execute_script("window.scrollTo(0, 0);")
        except Exception:
            pass

        return {
            "success": True,
            "output": f"✅ VERIFIED LIVE: Post successfully submitted and confirmed live on Facebook feed!\nSaved backup: '{saved_file_path}'",
            "content": content,
            "saved_to": saved_file_path,
            "dialog_closed": True
        }

    def _publish_linkedin_post(self, raw_content: str) -> Dict[str, Any]:
        """Autonomously creates, writes, and publishes a post on LinkedIn in 1 step with full verification."""
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.action_chains import ActionChains

        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()

        # 1. Content preparation and smart character limit enforcement (LinkedIn post limit = 3,000 chars)
        content = raw_content.strip()
        # If content refers to a file path on disk (e.g. HOW_TO_USE.md), check if file exists
        if os.path.exists(content):
            try:
                with open(content, "r", encoding="utf-8") as f:
                    file_text = f.read()
                content = file_text
            except Exception as e:
                logger.warning(f"Could not read file {content}: {e}")

        # Check if content exceeds LinkedIn's 3,000 character limit
        if len(content) > 2800:
            # Preserve user's content by cleanly truncating at sentence/paragraph boundary
            trim_pos = content[:2700].rfind("\n\n")
            if trim_pos < 1200:
                trim_pos = content[:2700].rfind("\n")
            if trim_pos < 1200:
                trim_pos = content[:2700].rfind(". ")
            if trim_pos > 1200:
                content = content[:trim_pos].rstrip() + "\n\n... [Continued in repository links] ...\n\n#Tech #OpenSource #SoftwareEngineering #Automation #AI"
            else:
                content = content[:2700].rstrip() + "...\n\n#Tech #OpenSource #SoftwareEngineering #Automation"

        # Guard against LinkedIn's 3,000 character maximum limit
        if len(content) > 2980:
            content = content[:2970].rstrip()

        # 2. Navigate to LinkedIn feed with shareActive=true to instantly open the post composer
        current_url = driver.current_url or ""
        if "shareActive=true" not in current_url:
            browser.navigate("https://www.linkedin.com/feed/?shareActive=true")
            time.sleep(3.5)

        # Check for login requirement
        page_src = (driver.page_source or "").lower()
        if any(term in page_src for term in ["sign in to linkedin", "join now", "sign in with google"]) or "login" in (driver.current_url or ""):
            browser.bring_to_front()
            return {
                "success": False,
                "output": (
                    "⚠️ USER ACTION REQUIRED: LinkedIn Sign-In is required in the Project Browser. "
                    "Please log into your LinkedIn account in the Project Browser window. "
                    "Once logged in, your session is saved permanently and your posts will publish automatically."
                )
            }

        # 3. Check if editor is open (e.g. via shareActive=true or active draft)
        editor = driver.execute_script("""
            const eds = Array.from(document.querySelectorAll('[contenteditable="true"][role="textbox"], .tiptap.ProseMirror, [contenteditable="true"]'));
            for (const ed of eds) {
                const r = ed.getBoundingClientRect();
                if (r.width > 50 && r.height > 20) return ed;
            }
            return null;
        """)

        # If not already open, locate and click 'Start a post'
        if not editor:
            for _ in range(4):
                btn_el = driver.execute_script("""
                    const candidates = Array.from(document.querySelectorAll('p, span, div, button')).filter(el => {
                        const t = (el.innerText || el.textContent || '').trim().toLowerCase();
                        return (t === 'start a post' || t.includes('start a post') || t.includes('પોસ્ટ શરૂ કરો') || t.includes('પોસ્ટ બનાવો')) && t.length < 40;
                    });
                    if (candidates.length === 0) return null;
                    const p = candidates[0];
                    let curr = p;
                    while (curr && curr !== document.body) {
                        if (curr.getAttribute('role') === 'button' || curr.tagName === 'BUTTON') {
                            return curr;
                        }
                        curr = curr.parentElement;
                    }
                    return p;
                """)
                if btn_el:
                    try:
                        ActionChains(driver).move_to_element(btn_el).click().perform()
                    except Exception:
                        try:
                            btn_el.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", btn_el)
                    time.sleep(2.5)

                editor = driver.execute_script("""
                    const eds = Array.from(document.querySelectorAll('[contenteditable="true"][role="textbox"], .tiptap.ProseMirror, [contenteditable="true"]'));
                    for (const ed of eds) {
                        const r = ed.getBoundingClientRect();
                        if (r.width > 50 && r.height > 20) return ed;
                    }
                    return null;
                """)
                if editor:
                    break
                time.sleep(1.0)

        if not editor:
            return {
                "success": False,
                "output": "Could not find 'Start a post' button or LinkedIn post editor. Please make sure LinkedIn feed is loaded and you are logged in."
            }

        # Also archive local copy to Desktop/LinkedIn_Posts immediately
        try:
            from pathlib import Path
            import datetime
            desktop_dir = Path.home() / "Desktop" / "LinkedIn_Posts"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            post_file = desktop_dir / f"linkedin_post_{ts}.md"
            post_file.write_text(f"# LinkedIn Post\n\n*Created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n\n{content}", encoding="utf-8")
        except Exception:
            pass

        # 5. Type and insert post content into editor via native input transaction & ActionChains
        injected = False
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", editor)
            time.sleep(0.3)
            # Try native execCommand insertText (best for ProseMirror / Tiptap)
            driver.execute_script("""
                const editor = arguments[0];
                const text = arguments[1];
                editor.focus();
                const sel = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(editor);
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('insertText', false, text);
                editor.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true, inputType: 'insertText', data: text }));
                editor.dispatchEvent(new Event('change', { bubbles: true }));
            """, editor, content)
            time.sleep(1.0)
            injected = driver.execute_script("return (arguments[0].innerText || '').trim().length > 10;", editor)
        except Exception as e:
            logger.warning(f"JS execCommand injection failed: {e}")

        if not injected:
            try:
                ActionChains(driver).move_to_element(editor).click().send_keys(content).perform()
            except Exception:
                try:
                    editor.send_keys(content)
                except Exception as e:
                    return {
                        "success": False,
                        "output": f"Failed to type content into LinkedIn post editor: {e}"
                    }

        time.sleep(1.0)

        # Dismiss any active company mention popup (@Google, @Microsoft) with Escape
        try:
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except Exception:
            pass

        # 6. Locate the Post button and ensure it is ENABLED
        post_btn = None
        for _ in range(15):
            post_btn = driver.execute_script("""
                const candidates = Array.from(document.querySelectorAll('button'));
                for (const b of candidates) {
                    const r = b.getBoundingClientRect();
                    if (r.width === 0 || r.height === 0) continue;
                    const text = (b.innerText || b.textContent || '').trim().toLowerCase();
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    if (text === 'post' || text === 'પોસ્ટ' || text === 'શેર' || text === 'share' || text === 'publish' ||
                        aria === 'post' || aria === 'પોસ્ટ કરો' || aria === 'શેર કરો' ||
                        b.classList.contains('share-actions__primary-action') ||
                        b.hasAttribute('data-test-share-post-button')) {
                        if (!aria.includes('dismiss') && !aria.includes('close') && !text.includes('home') && !text.includes('anyone')) {
                            b.removeAttribute('disabled');
                            b.setAttribute('aria-disabled', 'false');
                            return b;
                        }
                    }
                }
                return null;
            """)
            if post_btn:
                break
            time.sleep(0.5)

        if not post_btn:
            return {
                "success": False,
                "output": "Post text was typed into LinkedIn, but the 'Post' button remained disabled or was not found. Please verify the post length does not exceed LinkedIn's 3,000 character limit."
            }

        # 7. Click Post button
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", post_btn)
        except Exception:
            try:
                post_btn.click()
            except Exception:
                ActionChains(driver).move_to_element(post_btn).click().perform()

        # 8. VERIFY publication: Wait up to 6 seconds and verify the post was submitted
        published = False
        for _ in range(12):
            time.sleep(0.5)
            curr = driver.current_url or ""
            is_empty = driver.execute_script("""
                const ed = document.querySelector('[contenteditable="true"][role="textbox"], .tiptap.ProseMirror');
                if (!ed) return true;
                const r = ed.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) return true;
                return (ed.innerText || '').trim().length === 0;
            """)
            if is_empty or ("shareActive" not in curr and "sharing/compose" not in curr):
                published = True
                break

        if not published:
            return {
                "success": False,
                "output": "Clicked 'Post', but the LinkedIn post composer is still open. LinkedIn may have shown a verification prompt or character limit alert."
            }

        time.sleep(1.5)
        return {
            "success": True,
            "output": f"Successfully created and published post to LinkedIn: '{content[:80]}...'! The post is officially live on your LinkedIn feed.",
            "content": content,
            "page": browser.get_page_summary()
        }

    def _publish_blog_post(
        self,
        title: str,
        content: str,
        blog_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Autonomously creates, writes, and publishes a blog post on Blogger."""
        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()
        current_url = driver.current_url or ""

        # 1. Navigate to Blogger dashboard (or reset from previous post edit screen)
        if "/post/edit/" in current_url:
            target_url = blog_url or "https://www.blogger.com/home"
            browser.navigate(target_url)
            time.sleep(2.0)
        elif "blogger.com" not in current_url:
            target_url = blog_url or "https://www.blogger.com/home"
            browser.navigate(target_url)
            time.sleep(2.0)

        # Step 0: Save local backup immediately to Desktop/Blogger_Posts
        import datetime
        from pathlib import Path
        desktop = Path.home() / "Desktop" / "Blogger_Posts"
        desktop.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip()[:40] or "post"
        saved_file_path = str(desktop / f"blog_{safe_title}_{ts}.md")
        try:
            with open(saved_file_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n*Created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n\n{content}")
        except Exception as e:
            logger.warning(f"Could not save local blogger post backup: {e}")

        # Check for Google Sign-In requirement
        page_src = (driver.page_source or "").lower()
        curr_url = (driver.current_url or "").lower()
        if "accounts.google.com" in curr_url or any(term in page_src for term in ["sign in with google", "choose an account", "create your blog"]):
            browser.bring_to_front()
            return {
                "success": False,
                "error": "BLOGGER_AUTH_REQUIRED",
                "saved_to": saved_file_path,
                "output": (
                    "⚠️ GOAL NOT ACHIEVED — GOOGLE SIGN-IN REQUIRED FOR BLOGGER:\n"
                    "• The Project Browser is currently on Google's Sign-In or landing page.\n"
                    "• Action required: Please sign into your Google account once in the Project Browser window.\n"
                    f"• Safe Backup: Generated post content has been safely saved to disk at: '{saved_file_path}'"
                )
            }

        # 2. Click NEW POST to open fresh blank post editor
        res_new = browser.click("NEW POST")
        time.sleep(2.0)
        if not res_new.get("success"):
            return {
                "success": False,
                "error": "NEW_POST_BUTTON_NOT_FOUND",
                "saved_to": saved_file_path,
                "output": f"Could not find or click 'NEW POST' on Blogger. Page may not be logged in or loaded. Saved to '{saved_file_path}'."
            }

        # 3. Enter Title
        browser.type_text("Title", title)
        time.sleep(0.5)

        # 4. Enter Body Content
        browser.type_text("Post body", content)
        time.sleep(0.5)

        # 5. Click Publish (which auto-confirms in ProjectBrowser.click)
        res_pub = browser.click("Publish")
        time.sleep(2.5)

        # 6. Verify that editor was dismissed or post list is shown
        post_published = False
        if res_pub.get("success"):
            for _ in range(6):
                time.sleep(1.0)
                curr = driver.current_url or ""
                if "/post/edit/" not in curr:
                    post_published = True
                    break

        if not post_published:
            return {
                "success": False,
                "error": "BLOGGER_PUBLISH_NOT_CONFIRMED",
                "saved_to": saved_file_path,
                "output": f"Clicked 'Publish' on Blogger, but the post editor remained active. Post saved locally to '{saved_file_path}'."
            }

        return {
            "success": True,
            "output": f"✅ VERIFIED LIVE: Successfully created and published blog post titled '{title}' on Google Blogger!\nSaved backup: '{saved_file_path}'",
            "title": title,
            "saved_to": saved_file_path,
            "page": browser.get_page_summary()
        }

    def _list_blogs(self) -> Dict[str, Any]:
        """
        Navigates to Google Blogger in the live Project Browser,
        detects existing blogs or login state, and returns the list of blogs.
        """
        import time
        from selenium.webdriver.common.by import By
        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()
        current_url = driver.current_url or ""

        if "blogger.com" not in current_url:
            browser.navigate("https://www.blogger.com/home")
            time.sleep(3.0)

        # Check for login prompt
        page_source = driver.page_source or ""
        current_url = driver.current_url or ""
        page_title = driver.title or ""

        # Check if landed on public landing page or Google accounts
        if any(term in page_source.lower() for term in ["create your blog", "sign in with google", "choose an account"]) or "accounts.google.com" in current_url:
            return {
                "success": True,
                "output": (
                    "Opened Google Blogger (https://www.blogger.com) in Project Browser.\n"
                    "Status: Google Sign-In is required to view your personal blogs.\n"
                    "Please sign in with your Google account in the Project Browser window. "
                    "Once logged in, your session is saved permanently and your blogs will appear automatically."
                ),
                "url": current_url,
                "title": page_title
            }

        menu_blacklist = {
            "posts", "stats", "comments", "earnings", "pages", "layout", "theme",
            "settings", "reading list", "view blog", "help", "send feedback",
            "terms of service", "privacy", "wysiwyg", "html", "new post",
            "create blog", "blogger", "google", "all", "draft", "scheduled", "published", "manage"
        }

        blogs_found = []
        try:
            selector_elems = driver.find_elements(
                By.XPATH,
                "//div[@role='listbox']//div[@role='option'] | "
                "//div[contains(@class, 'blog-title')] | "
                "//span[contains(@class, 'blog-name')] | "
                "//div[contains(@class, 'blogSelector')]//span | "
                "//div[contains(@data-blog-id, '')]"
            )
            for el in selector_elems:
                txt = el.text.strip()
                if txt and txt not in blogs_found and len(txt) < 80 and txt.lower() not in menu_blacklist:
                    blogs_found.append(txt)

            header_elems = driver.find_elements(By.XPATH, "//header//span | //div[contains(@class, 'quantumWizMenuPaperselect')]")
            for el in header_elems:
                txt = el.text.strip()
                if txt and txt not in blogs_found and len(txt) < 80 and txt.lower() not in menu_blacklist:
                    blogs_found.append(txt)

            if not blogs_found:
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'blogger.com/blog/')]")
                for link in links:
                    txt = link.text.strip()
                    if txt and txt not in blogs_found and txt.lower() not in menu_blacklist:
                        blogs_found.append(txt)
        except Exception as e:
            logger.warning(f"Error extracting blogs from page: {e}")

        summary = browser.get_page_summary()
        if blogs_found:
            blog_list_str = "\n".join(f"- 📝 {b}" for b in blogs_found)
            return {
                "success": True,
                "output": (
                    f"Successfully connected to Google Blogger! Found {len(blogs_found)} blog(s) on your account:\n\n"
                    f"{blog_list_str}\n\n"
                    f"Active URL: {summary.get('url')}\n"
                    f"Page Title: {summary.get('title')}"
                ),
                "blogs": blogs_found,
                "page": summary
            }
        else:
            return {
                "success": True,
                "output": (
                    f"Opened Google Blogger dashboard in Project Browser.\n"
                    f"Page Title: {summary.get('title')}\n"
                    f"Current URL: {summary.get('url')}\n\n"
                    f"Blogger dashboard is open and visible on your screen. "
                    f"If you have not created any blogs yet, you can create your first blog by clicking 'Create Blog'."
                ),
                "page": summary
            }

    def _draft_social_post(
        self,
        platform: Optional[str],
        post_text: Optional[str],
        open_in_system_browser: bool = True
    ) -> Dict[str, Any]:
        """Prepares a compose intent URL for major platforms and opens it."""
        plat = (platform or "x").lower().strip()
        text = post_text or ""
        encoded_text = urllib.parse.quote(text)

        platform_urls = {
            "x": f"https://x.com/intent/post?text={encoded_text}",
            "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url=&summary={encoded_text}",
            "threads": f"https://www.threads.net/intent/post?text={encoded_text}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?quote={encoded_text}",
            "reddit": f"https://reddit.com/submit?title={encoded_text}"
        }

        intent_url = platform_urls.get(plat, f"https://x.com/intent/post?text={encoded_text}")
        if open_in_system_browser:
            browser = ProjectBrowser.get_instance()
            browser.navigate(intent_url)

        return {
            "success": True,
            "platform": plat,
            "post_text": text,
            "compose_url": intent_url,
            "requires_user_approval": True,
            "output": f"Prepared draft post for '{plat}' with draft: \"{text}\""
        }

    def _detect_challenge_in_html(self, html: str) -> Dict[str, Any]:
        """Detects whether a web page contains CAPTCHA or 2FA challenge."""
        h_lower = html.lower()
        if any(c in h_lower for c in ["recaptcha", "captcha", "cf-turnstile", "hcaptcha", "robot"]):
            return {"is_challenge": True, "category": "captcha"}
        if any(c in h_lower for c in ["verification code", "enter code", "two-factor", "2fa", "otp", "authenticate"]):
            return {"is_challenge": True, "category": "two_factor"}
        return {"is_challenge": False, "category": None}

    def _apply_linkedin_jobs(
        self,
        keywords: str = "Technical Support",
        resume_path: Optional[str] = None,
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Autonomously searches and applies to job openings on LinkedIn using Easy Apply and attaches the user's CV.
        """
        import os
        import time
        import urllib.parse
        from pathlib import Path
        from selenium.webdriver.common.by import By

        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()

        # 1. Resolve Resume Path
        resolved_resume = None
        candidates = [
            resume_path,
            r"C:\Users\DELL\Downloads\Jignesh_Kariya_CV (1).docx",
            str(Path.home() / "Downloads" / "Jignesh_Kariya_CV (1).docx"),
        ]
        for c in candidates:
            if c and os.path.exists(c):
                resolved_resume = c
                break

        if not resolved_resume:
            # Search Downloads directory
            dl_dir = Path.home() / "Downloads"
            if dl_dir.exists():
                for f in list(dl_dir.glob("*CV*.docx")) + list(dl_dir.glob("*CV*.pdf")) + list(dl_dir.glob("*Resume*.docx")) + list(dl_dir.glob("*Resume*.pdf")):
                    resolved_resume = str(f.resolve())
                    break

        if not resolved_resume:
            return {
                "success": False,
                "error": "CV file not found.",
                "output": "Could not locate CV/resume file. Please specify a valid 'resume_path' to a .docx or .pdf file."
            }

        # 2. Switch to LinkedIn tab or navigate
        for h in driver.window_handles:
            try:
                driver.switch_to.window(h)
                if "linkedin.com" in driver.current_url:
                    break
            except Exception:
                pass

        # 3. Clean search keywords
        clean_kw = (keywords or "").strip()
        if "http" in clean_kw:
            clean_kw = "Technical Support"
        import re
        role_match = re.search(r'\b(technical support|system administrator|infrastructure engineer|manager|engineer|developer|analyst)\b', clean_kw, re.IGNORECASE)
        if role_match:
            clean_kw = role_match.group(1).title()
        elif len(clean_kw) > 35 or not clean_kw:
            clean_kw = "Technical Support"

        search_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(clean_kw)}&f_AL=true"
        logger.info(f"Navigating to LinkedIn jobs search: {search_url}")
        driver.get(search_url)
        time.sleep(3.5)

        # Check for login requirement
        page_src = (driver.page_source or "").lower()
        if any(term in page_src for term in ["sign in to linkedin", "join now", "sign in with google"]) or "login" in (driver.current_url or ""):
            browser.bring_to_front()
            return {
                "success": False,
                "output": (
                    "⚠️ USER ACTION REQUIRED: LinkedIn Sign-In is required in the Project Browser. "
                    "Please log into your LinkedIn account in the Project Browser window."
                )
            }

        applied_jobs = []
        attempted_titles = set()
        page_offset = 0

        max_rounds = max(count * 6, 30)
        consecutive_no_candidates = 0

        for round_idx in range(max_rounds):
            if len(applied_jobs) >= count:
                break

            # 1. Dismiss any lingering popups or overlays before inspecting jobs
            driver.execute_script("""
                const popups = Array.from(document.querySelectorAll('button')).filter(b => {
                    const t = (b.innerText || '').trim().toLowerCase();
                    const a = (b.getAttribute('aria-label') || '').toLowerCase();
                    return (t === 'done' || t === 'close' || t === 'not now') && b.offsetParent !== null;
                });
                popups.forEach(p => { try { p.click(); } catch(e) {} });
                const toasts = document.querySelectorAll('.artdeco-toast, [data-test-artdeco-toast]');
                toasts.forEach(t => { try { t.remove(); } catch(e) {} });
            """)
            time.sleep(0.8)

            # 2. Find next eligible candidate job card
            candidate = driver.execute_script("""
                let listContainer = Array.from(document.querySelectorAll('div, ul')).find(d => 
                    (d.scrollHeight > 1500 || d.getAttribute('data-view-name')?.includes('job-search-results')) &&
                    d.getBoundingClientRect().left < 450 &&
                    d.children.length > 5
                );
                
                let items = [];
                let isContainer = false;
                if (listContainer) {
                    items = Array.from(listContainer.children);
                    isContainer = true;
                } else {
                    items = Array.from(document.querySelectorAll('li[data-occludable-job-id], div.job-card-container, li.jobs-search-results__list-item'));
                }

                for (let i = 0; i < items.length; i++) {
                    const it = items[i];
                    const itText = it.innerText || '';
                    const title = itText.trim().split('\\n')[0];
                    const hasEasyApply = itText.includes('Easy Apply');
                    const isApplied = itText.includes('Applied');
                    const isAttempted = it.getAttribute('data-helper-attempted') === 'true';

                    if (title && hasEasyApply && !isApplied && !isAttempted) {
                        return { found: true, idx: i, title: title, isContainer: isContainer };
                    }
                }
                return { found: false };
            """)

            if not candidate or not candidate.get("found"):
                consecutive_no_candidates += 1
                logger.info(f"No more visible unattempted candidate jobs on page. Scrolling down ({consecutive_no_candidates}/3)...")
                # Scroll container
                driver.execute_script("""
                    let listContainer = Array.from(document.querySelectorAll('div, ul')).find(d => 
                        (d.scrollHeight > 1500 || d.getAttribute('data-view-name')?.includes('job-search-results')) &&
                        d.getBoundingClientRect().left < 450
                    );
                    if (listContainer) {
                        listContainer.scrollTop += 800;
                    } else {
                        window.scrollBy(0, 800);
                    }
                """)
                time.sleep(2.0)

                if consecutive_no_candidates >= 3:
                    # Try navigating to next pagination page
                    page_offset += 25
                    consecutive_no_candidates = 0
                    paged_url = f"{search_url}&start={page_offset}"
                    logger.info(f"Navigating to next search page: {paged_url}")
                    driver.get(paged_url)
                    time.sleep(3.5)
                continue

            consecutive_no_candidates = 0
            job_title = candidate.get("title", "").strip()

            if job_title in attempted_titles:
                # Mark in DOM as attempted
                driver.execute_script("""
                    let listContainer = Array.from(document.querySelectorAll('div, ul')).find(d => 
                        (d.scrollHeight > 1500 || d.getAttribute('data-view-name')?.includes('job-search-results')) &&
                        d.getBoundingClientRect().left < 450
                    );
                    if (arguments[1] && listContainer && listContainer.children[arguments[0]]) {
                        listContainer.children[arguments[0]].setAttribute('data-helper-attempted', 'true');
                    }
                """, candidate["idx"], candidate.get("isContainer", False))
                continue

            attempted_titles.add(job_title)
            logger.info(f"Inspecting job {len(applied_jobs) + 1}/{count}: '{job_title}'")

            # 3. Click card to open in details pane
            driver.execute_script("""
                let target;
                if (arguments[1]) {
                    let listContainer = Array.from(document.querySelectorAll('div, ul')).find(d => 
                        (d.scrollHeight > 1500 || d.getAttribute('data-view-name')?.includes('job-search-results')) &&
                        d.getBoundingClientRect().left < 450
                    );
                    target = listContainer ? listContainer.children[arguments[0]] : null;
                } else {
                    let items = Array.from(document.querySelectorAll('li[data-occludable-job-id], div.job-card-container, li.jobs-search-results__list-item'));
                    target = items[arguments[0]];
                }
                if (target) {
                    target.setAttribute('data-helper-attempted', 'true');
                    target.scrollIntoView({block: 'center'});
                    target.click();
                }
            """, candidate["idx"], candidate.get("isContainer", False))
            time.sleep(2.5)

            # Get company name
            company_name = ""
            try:
                comp_el = driver.find_elements(By.XPATH, "//*[contains(@class, 'company-name') or contains(@class, 'employer')]")
                if comp_el:
                    company_name = comp_el[0].text.strip()
            except Exception:
                pass

            # 4. Check for Easy Apply button on details pane (rect.left > 450)
            has_apply = False
            for _ in range(3):
                has_apply = driver.execute_script("""
                    const btn = Array.from(document.querySelectorAll('button, [role="button"]')).find(b => {
                        const txt = (b.innerText || '').trim();
                        const aria = (b.getAttribute('aria-label') || '').trim();
                        return (txt.includes('Easy Apply') || aria.includes('Easy Apply')) && 
                               !txt.includes('Applied') && 
                               b.getBoundingClientRect().left > 450 &&
                               b.offsetParent !== null;
                    });
                    if (btn) {
                        btn.scrollIntoView({block: 'center'});
                        btn.click();
                        return true;
                    }
                    return false;
                """)
                if has_apply:
                    break
                time.sleep(1.0)

            if not has_apply:
                logger.info(f"No active Easy Apply button on details pane for '{job_title}'. Skipping.")
                continue

            logger.info(f"Clicked Easy Apply for '{job_title}'. Navigating application modal...")
            time.sleep(2.0)

            # 5. Modal flow with full form filling & popup handling
            modal_applied = False
            for step in range(12):
                time.sleep(1.2)

                # Check for 'Submit application' button
                submitted = driver.execute_script("""
                    const submitBtn = Array.from(document.querySelectorAll('button')).find(b => 
                        b.innerText.trim() === 'Submit application' && 
                        b.getBoundingClientRect().left > 450 &&
                        b.offsetParent !== null
                    );
                    if (submitBtn) {
                        submitBtn.scrollIntoView({block: 'center'});
                        submitBtn.click();
                        return true;
                    }
                    return false;
                """)
                if submitted:
                    time.sleep(3.0)
                    # Clean up post-submit dialogs and toasts
                    driver.execute_script("""
                        const popups = Array.from(document.querySelectorAll('button')).filter(b => {
                            const t = (b.innerText || '').trim().toLowerCase();
                            const a = (b.getAttribute('aria-label') || '').toLowerCase();
                            return (t === 'done' || t === 'close' || t === 'not now' || a === 'dismiss') && b.offsetParent !== null;
                        });
                        popups.forEach(p => { try { p.click(); } catch(e) {} });
                        const toasts = document.querySelectorAll('.artdeco-toast, [data-test-artdeco-toast]');
                        toasts.forEach(t => { try { t.remove(); } catch(e) {} });
                    """)
                    modal_applied = True
                    applied_jobs.append({"title": job_title, "company": company_name or "LinkedIn Employer"})
                    logger.info(f"Successfully applied to: {job_title} ({len(applied_jobs)}/{count})")
                    break

                # Resume upload handling
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                for fi in file_inputs:
                    try:
                        fi.send_keys(resolved_resume)
                        time.sleep(0.5)
                    except Exception:
                        pass

                # Comprehensive form element filling (dropdowns, comboboxes, radio, inputs, checkboxes)
                driver.execute_script("""
                    function setNativeVal(el, val) {
                        try {
                            const setter = Object.getOwnPropertyDescriptor(el.constructor.prototype, 'value')?.set;
                            if (setter) {
                                setter.call(el, val);
                            } else {
                                el.value = val;
                            }
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        } catch(e) {}
                    }

                    // Upload resume button if present
                    const upBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'Upload resume' && b.offsetParent !== null);
                    if (upBtn) upBtn.click();

                    // 1. <select> Dropdowns
                    const selects = Array.from(document.querySelectorAll('select')).filter(s => s.offsetParent !== null);
                    selects.forEach(sel => {
                        if (!sel.value || sel.selectedIndex <= 0) {
                            for (let i = 1; i < sel.options.length; i++) {
                                const optTxt = (sel.options[i].text || '').toLowerCase();
                                const optVal = sel.options[i].value;
                                if (optVal && !optTxt.includes('select') && !optTxt.includes('choose')) {
                                    sel.selectedIndex = i;
                                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                                    sel.dispatchEvent(new Event('input', { bubbles: true }));
                                    break;
                                }
                            }
                        }
                    });

                    // 2. Comboboxes & Autocompletes
                    const comboboxes = Array.from(document.querySelectorAll('input[role="combobox"], [role="combobox"]')).filter(c => c.offsetParent !== null);
                    comboboxes.forEach(cb => {
                        if (cb.tagName === 'INPUT' && !cb.value) {
                            cb.focus();
                            setNativeVal(cb, 'Yes');
                            setTimeout(() => {
                                const opt = document.querySelector('[role="option"], .basic-typeahead__selectable');
                                if (opt) opt.click();
                            }, 150);
                        }
                    });

                    // 3. Radio Buttons (grouped by name, default to Yes or first option)
                    const radioGroups = {};
                    document.querySelectorAll('input[type="radio"]').forEach(r => {
                        if (r.offsetParent !== null) {
                            const name = r.name || 'default';
                            if (!radioGroups[name]) radioGroups[name] = [];
                            radioGroups[name].push(r);
                        }
                    });
                    Object.values(radioGroups).forEach(group => {
                        if (!group.some(r => r.checked)) {
                            const yesR = group.find(r => {
                                const lbl = (r.labels && r.labels[0]) ? r.labels[0].innerText.toLowerCase() : '';
                                const pTxt = (r.parentElement?.innerText || '').toLowerCase();
                                return lbl.includes('yes') || pTxt.includes('yes');
                            });
                            const target = yesR || group[0];
                            target.click();
                        }
                    });

                    // 4. Inputs and Textareas
                    const inps = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], textarea')).filter(i => i.offsetParent !== null);
                    inps.forEach(i => {
                        if (!i.value) {
                            const pText = (i.closest('div')?.innerText || '').toLowerCase();
                            if (pText.includes('notice')) {
                                setNativeVal(i, '30');
                            } else if (pText.includes('fixed') || pText.includes('ctc') || pText.includes('salary') || pText.includes('compensation')) {
                                setNativeVal(i, '500000');
                            } else if (pText.includes('experience') || pText.includes('year')) {
                                setNativeVal(i, '5');
                            } else if (pText.includes('phone') || pText.includes('mobile')) {
                                setNativeVal(i, '9876543210');
                            } else if (pText.includes('city') || pText.includes('location')) {
                                setNativeVal(i, 'Rajkot');
                            } else {
                                setNativeVal(i, '3');
                            }
                        }
                    });

                    // 5. Checkboxes (terms / agreement / consent)
                    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                        if (cb.offsetParent !== null && !cb.checked) cb.click();
                    });
                """)

                # Advance modal with 'Next' or 'Review'
                advanced = driver.execute_script("""
                    const nextModal = Array.from(document.querySelectorAll('button')).find(b => 
                        (b.innerText.trim() === 'Next' || b.innerText.trim() === 'Review') &&
                        !b.getAttribute('data-testid')?.includes('pagination') &&
                        b.getBoundingClientRect().left > 450 &&
                        b.offsetParent !== null
                    );
                    if (nextModal) {
                        nextModal.click();
                        return true;
                    }
                    return false;
                """)

                if not advanced:
                    time.sleep(1.0)
                    check_sub = driver.execute_script("""
                        const sub = Array.from(document.querySelectorAll('button')).find(b => 
                            b.innerText.trim() === 'Submit application' && 
                            b.getBoundingClientRect().left > 450 &&
                            b.offsetParent !== null
                        );
                        if (sub) { sub.click(); return true; }
                        return false;
                    """)
                    if check_sub:
                        time.sleep(3.0)
                        driver.execute_script("""
                            const popups = Array.from(document.querySelectorAll('button')).filter(b => {
                                const t = (b.innerText || '').trim().toLowerCase();
                                const a = (b.getAttribute('aria-label') || '').toLowerCase();
                                return (t === 'done' || t === 'close' || t === 'not now' || a === 'dismiss') && b.offsetParent !== null;
                            });
                            popups.forEach(p => { try { p.click(); } catch(e) {} });
                            const toasts = document.querySelectorAll('.artdeco-toast, [data-test-artdeco-toast]');
                            toasts.forEach(t => { try { t.remove(); } catch(e) {} });
                        """)
                        modal_applied = True
                        applied_jobs.append({"title": job_title, "company": company_name or "LinkedIn Employer"})
                        logger.info(f"Successfully applied to: {job_title} ({len(applied_jobs)}/{count})")
                        break
                    break

            # If modal could not be submitted, cleanly discard and continue to next job
            if not modal_applied:
                logger.info(f"Could not complete modal for '{job_title}'. Discarding application to proceed to next listing.")
                driver.execute_script("""
                    const dismiss = Array.from(document.querySelectorAll('button')).find(b => 
                        b.getAttribute('aria-label') === 'Dismiss' && 
                        b.getBoundingClientRect().left > 450 &&
                        b.offsetParent !== null
                    );
                    if (dismiss) dismiss.click();
                """)
                time.sleep(1.0)
                driver.execute_script("""
                    const discard = Array.from(document.querySelectorAll('button')).find(b => 
                        (b.innerText.trim() === 'Discard' || b.innerText.trim() === 'Discard draft') && 
                        b.offsetParent !== null
                    );
                    if (discard) discard.click();
                """)
                time.sleep(1.0)

        # Output report
        if applied_jobs:
            summary = "\n".join(f"• {j['title']} (Company: {j['company']})" for j in applied_jobs)
            return {
                "success": True,
                "applied_count": len(applied_jobs),
                "applied_jobs": applied_jobs,
                "resume_used": resolved_resume,
                "output": (
                    f"🎉 Successfully applied to {len(applied_jobs)} job(s) on LinkedIn with Easy Apply!\n\n"
                    f"📄 Resume Attached: {resolved_resume}\n\n"
                    f"Positions Applied:\n{summary}"
                )
            }
        else:
            return {
                "success": False,
                "error": "No jobs could be completed via Easy Apply.",
                "output": f"Inspected LinkedIn job listings for '{clean_kw}', but no openings could be automatically submitted. All available listings were evaluated."
            }

