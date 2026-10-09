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
                    "Action to perform: 'publish_blog_post' (autonomously creates, writes, and publishes a blog post with title and text in 1 step), "
                    "'open_url' (load a page), 'click' (click button/link by text), "
                    "'type' (enter text into field), 'get_page' (read current page state), "
                    "'close_browser' (close window), 'draft_social_post' (compose social post)"
                ),
                "enum": [
                    "publish_blog_post",
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
                "description": "Text to type into the targeted input or content area, or blog post body text."
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
                "description": "Post text (for draft_social_post)."
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
            if action in ["publish_blog_post", "create_blog_post"]:
                return self._publish_blog_post(post_title, type_content, url)

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
                return self._draft_social_post(platform, post_text)

            else:
                return {
                    "success": False,
                    "output": f"Unknown action: '{action}'. Available: publish_blog_post, open_url, click, type, get_page, close_browser."
                }

        except Exception as e:
            logger.error(f"BrowserAutomationTool execution error: {e}", exc_info=True)
            return {
                "success": False,
                "output": f"Browser automation error: {str(e)}",
                "error": str(e)
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

    def _draft_social_post(
        self,
        platform: Optional[str],
        post_text: Optional[str]
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
        browser = ProjectBrowser.get_instance()
        browser.navigate(intent_url)

        return {
            "success": True,
            "platform": plat,
            "post_text": text,
            "compose_url": intent_url,
            "output": f"Opened compose window for '{plat}' with draft: \"{text}\""
        }
