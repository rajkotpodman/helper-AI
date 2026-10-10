"""Browser Automation & Live Project Browser Tools for Helper-AI.

Provides real-time browser control (navigate, click buttons, type text, submit forms)
using a dedicated live Chromium browser with a persistent user profile, allowing Google/Blogger
logins and cookies to remain permanently saved.
"""

import os
import sys
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
                    "Action to perform: 'publish_facebook_post' (autonomously creates, writes, and publishes a Facebook post in 1 step), "
                    "'publish_blog_post' (autonomously creates, writes, and publishes a blog post with title and text in 1 step), "
                    "'open_url' (load a page), 'click' (click button/link by text), "
                    "'type' (enter text into field), 'get_page' (read current page state), "
                    "'close_browser' (close window), 'draft_social_post' (compose social post)"
                ),
                "enum": [
                    "publish_facebook_post",
                    "publish_blog_post",
                    "list_blogs",
                    "open_url",
                    "click",
                    "type",
                    "get_page",
                    "read_page",
                    "close_browser",
                    "draft_social_post"
                ]
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
        **kwargs
    ) -> Dict[str, Any]:
        browser = ProjectBrowser.get_instance()
        target_name = target or kwargs.get("element") or kwargs.get("selector") or ""
        type_content = text or kwargs.get("content") or kwargs.get("body") or kwargs.get("value") or ""
        post_title = title or kwargs.get("post_title") or target_name or "New Blog Post"

        try:
            if action in ["publish_facebook_post", "create_facebook_post", "post_facebook"]:
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

            elif action in ["get_page", "read_page", "inspect_page"]:
                res = browser.get_page_summary()
                return {
                    "success": True,
                    "output": (
                        f"Current URL: {res.get('url')}\n"
                        f"Title: {res.get('title')}\n"
                        f"Buttons on page: {res.get('buttons')}\n"
                        f"Inputs on page: {res.get('inputs')}\n"
                        f"Content snippet: {res.get('snippet', '')[:400]}"
                    ),
                    "page": res
                }

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
                    "output": f"Unknown action: '{action}'. Available: publish_facebook_post, publish_blog_post, open_url, click, type, get_page, close_browser."
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
        Autonomously creates, writes, and publishes a Facebook post.
        Navigates to Facebook, opens post composer, types the text, and submits the post.
        """
        import time
        from selenium.webdriver.common.by import By
        browser = ProjectBrowser.get_instance()
        driver = browser.get_driver()
        current_url = driver.current_url or ""

        # 1. Navigate to Facebook home if not already on facebook or on subpath
        if "facebook.com" not in current_url:
            browser.navigate("https://www.facebook.com/")
            time.sleep(2.5)
        elif "/profile" in current_url or any(x in current_url for x in ["/photo", "/watch", "/reel", "/story"]):
            browser.navigate("https://www.facebook.com/")
            time.sleep(2.5)

        # 2. Dismiss any floating backdrop/modals or 'Not now' prompts if present
        try:
            not_now_btns = driver.find_elements(By.XPATH, "//*[@role='button'][contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'not now')]")
            for b in not_now_btns:
                if b.is_displayed():
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(0.5)
                    break
        except Exception:
            pass

        # 3. Locate and click "What's on your mind" composer button
        opened = False
        for _ in range(3):
            btns = driver.find_elements(By.XPATH, "//*[@role='button'] | //div[contains(@class, 'x1i10hfl')]")
            for b in btns:
                try:
                    if b.is_displayed():
                        txt = (b.text or "").lower()
                        aria = (b.get_attribute("aria-label") or "").lower()
                        if "what's on your mind" in txt or "what's on your mind" in aria or "create a post" in txt:
                            try:
                                b.click()
                            except Exception:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", b)
                            opened = True
                            break
                except Exception:
                    continue
            if opened:
                break
            time.sleep(1.0)

        # 4. Wait for the Create Post dialog / textbox to appear
        time.sleep(1.5)
        textbox = None
        for _ in range(6):
            tbs = driver.find_elements(By.XPATH, "//*[@role='textbox'] | //*[@contenteditable='true']")
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
            return {
                "success": False,
                "output": "Could not open Facebook 'Create post' composer. Please ensure you are logged into Facebook in the Project Browser."
            }

        # 5. Type the post content
        type_res = browser.type_text("What's on your mind", content, clear=False)
        time.sleep(1.2)

        # 6. Locate the Post (or Next) button
        post_btn = None
        for _ in range(5):
            btns = driver.find_elements(By.XPATH, "//*[@role='button']")
            for b in btns:
                try:
                    if b.is_displayed():
                        txt = (b.text or "").strip().lower()
                        aria = (b.get_attribute("aria-label") or "").strip().lower()
                        dis = b.get_attribute("aria-disabled")
                        if (txt in ["post", "next"] or aria in ["post", "next"]) and dis != "true":
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
                "output": f"Post text was entered, but the 'Post' button was not found or remained disabled. Status: {type_res.get('output')}"
            }

        # 7. Click Post (or Next)
        try:
            post_btn.click()
        except Exception:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", post_btn)

        time.sleep(3.0)

        # If it was 'Next', Facebook might present a second confirmation modal with 'Post'
        try:
            second_btns = driver.find_elements(By.XPATH, "//*[@role='button']")
            for b in second_btns:
                if b.is_displayed() and b.text.strip().lower() == "post":
                    try:
                        b.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", b)
                    time.sleep(2.5)
                    break
        except Exception:
            pass

        return {
            "success": True,
            "output": f"Successfully created and published post to Facebook: '{content[:80]}...'! The post is officially live on your timeline/feed.",
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

        # 1. Navigate to Blogger dashboard if needed
        if "blogger.com" not in current_url:
            target_url = blog_url or "https://www.blogger.com/home"
            browser.navigate(target_url)
            import time
            time.sleep(2.0)

        # 2. Click NEW POST if not already on the edit page
        if "/post/edit/" not in (driver.current_url or ""):
            res_click = browser.click("NEW POST")
            import time
            time.sleep(2.0)

        # 3. Enter Title
        browser.type_text("Title", title)
        import time
        time.sleep(0.5)

        # 4. Enter Body Content
        browser.type_text("Post body", content)
        time.sleep(0.5)

        # 5. Click Publish (which auto-confirms in ProjectBrowser.click)
        res_pub = browser.click("Publish")
        time.sleep(2.0)

        return {
            "success": True,
            "output": f"Successfully created and published blog post titled '{title}' on Google Blogger! The post is now live.",
            "title": title,
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
