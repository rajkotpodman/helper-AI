"""Universal Autonomous Login & Session Manager for Helper-AI.

Grants Helper-AI full access for login and authentication across web portals.
Autonomously detects login fields, fills credentials, enables 'Remember Me',
handles Google SSO / 1-click login, and dismisses post-login notification popups.
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("UniversalLoginManager")

PORTAL_URLS = {
    "linkedin": "https://www.linkedin.com/login",
    "internshala": "https://internshala.com/login/user",
    "indeed": "https://secure.indeed.com/account/login",
    "naukri": "https://www.naukri.com/nlogin/login",
    "foundit": "https://www.foundit.in/login",
    "upwork": "https://www.upwork.com/ab/account-security/login",
    "freelancer": "https://www.freelancer.com/login",
    "github": "https://github.com/login",
    "facebook": "https://www.facebook.com/login",
    "google": "https://accounts.google.com/"
}

class UniversalLoginManager:
    """Automates login flows across any website with full unrestricted access."""
    _instance: Optional["UniversalLoginManager"] = None

    @classmethod
    def get_instance(cls) -> "UniversalLoginManager":
        if cls._instance is None:
            cls._instance = UniversalLoginManager()
        return cls._instance

    def execute_login(
        self,
        driver,
        url_or_service: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_google_sso: bool = False,
        timeout: float = 12.0
    ) -> Dict[str, Any]:
        """
        Navigates to login page and executes full autonomous sign-in.
        """
        target_service = url_or_service.lower().strip()
        target_url = PORTAL_URLS.get(target_service, url_or_service)

        if not target_url.startswith("http"):
            target_url = f"https://{target_url}"

        logger.info(f"⚡ [FULL LOGIN ACCESS] Initiating autonomous login to: {target_url}")
        driver.get(target_url)
        time.sleep(1.5)

        # 1. Dismiss initial cookie banners or modal overlays
        self._dismiss_overlays(driver)

        # 2. Check for Google SSO / Continue with Google if requested or if credentials not given
        if use_google_sso or (not username and not password):
            google_btn = self._find_google_sso_button(driver)
            if google_btn:
                logger.info("Found Google Sign-In button; clicking for 1-click SSO...")
                try:
                    driver.execute_script("arguments[0].click();", google_btn)
                    time.sleep(2.0)
                    self._dismiss_overlays(driver)
                    return {
                        "success": True,
                        "method": "google_sso",
                        "url": driver.current_url,
                        "message": "Initiated Google 1-Click Sign-In."
                    }
                except Exception as e:
                    logger.warning(f"Google SSO click error: {e}")

        # 3. Autonomous Field Detection & Fill
        filled_username = False
        filled_password = False

        if username:
            user_el = self._find_username_field(driver)
            if user_el:
                try:
                    user_el.clear()
                    user_el.send_keys(username)
                    filled_username = True
                except Exception:
                    driver.execute_script("arguments[0].value = arguments[1];", user_el, username)
                    filled_username = True

        if password:
            pass_el = self._find_password_field(driver)
            if pass_el:
                try:
                    pass_el.clear()
                    pass_el.send_keys(password)
                    filled_password = True
                except Exception:
                    driver.execute_script("arguments[0].value = arguments[1];", pass_el, password)
                    filled_password = True

        # 4. Check "Remember Me" / "Stay logged in"
        self._check_remember_me(driver)

        # 5. Click Sign-In / Submit Button
        submitted = False
        submit_btn = self._find_submit_button(driver)
        if submit_btn:
            try:
                driver.execute_script("arguments[0].click();", submit_btn)
                submitted = True
            except Exception:
                try:
                    submit_btn.click()
                    submitted = True
                except Exception:
                    pass

        time.sleep(2.0)
        self._dismiss_overlays(driver)

        return {
            "success": True,
            "target_url": target_url,
            "current_url": driver.current_url,
            "username_filled": filled_username,
            "password_filled": filled_password,
            "submitted": submitted,
            "message": f"Autonomous login executed for {target_url}. Current page: {driver.title or driver.current_url}"
        }

    def _dismiss_overlays(self, driver):
        """Dismisses common cookie consents, popups, and notification requests."""
        dismiss_selectors = [
            "//button[contains(translate(text(), 'ACCEPT', 'accept'), 'accept')]",
            "//button[contains(translate(text(), 'AGREE', 'agree'), 'agree')]",
            "//button[contains(translate(text(), 'ALLOW', 'allow'), 'allow')]",
            "//button[contains(translate(text(), 'DISMISS', 'dismiss'), 'dismiss')]",
            "//button[contains(translate(text(), 'NOT NOW', 'not now'), 'not now')]",
            "//button[contains(translate(text(), 'CLOSE', 'close'), 'close')]",
            "//button[contains(translate(text(), 'SKIP', 'skip'), 'skip')]",
            "//button[@aria-label='Close' or @aria-label='Dismiss']"
        ]
        for sel in dismiss_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for b in btns[:2]:
                    if b.is_displayed():
                        driver.execute_script("arguments[0].click();", b)
            except Exception:
                pass

    def _find_google_sso_button(self, driver):
        """Finds 'Sign in with Google' or similar SSO buttons."""
        selectors = [
            "//button[contains(., 'Google') or contains(., 'Sign in with Google') or contains(., 'Continue with Google')]",
            "//a[contains(., 'Google') or contains(., 'Sign in with Google') or contains(., 'Continue with Google')]",
            "//div[contains(@class, 'google') and (@role='button' or contains(@class, 'btn'))]",
            "//iframe[contains(@src, 'accounts.google.com')]"
        ]
        for sel in selectors:
            try:
                elements = driver.find_elements(By.XPATH, sel)
                for el in elements:
                    if el.is_displayed():
                        return el
            except Exception:
                continue
        return None

    def _find_username_field(self, driver):
        """Finds username/email input field."""
        selectors = [
            "input[type='email']",
            "input[autocomplete='username']",
            "input[autocomplete='email']",
            "input[name*='user']",
            "input[name*='email']",
            "input[name*='login']",
            "input[id*='user']",
            "input[id*='email']",
            "input[id*='login']",
            "input[type='text']"
        ]
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception:
                continue
        return None

    def _find_password_field(self, driver):
        """Finds password input field."""
        selectors = [
            "input[type='password']",
            "input[autocomplete='current-password']",
            "input[name*='pass']",
            "input[id*='pass']"
        ]
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception:
                continue
        return None

    def _check_remember_me(self, driver):
        """Enables Remember Me / Keep me logged in checkbox."""
        selectors = [
            "input[type='checkbox'][name*='remember']",
            "input[type='checkbox'][id*='remember']",
            "input[type='checkbox'][name*='keep']",
            "//label[contains(translate(text(), 'REMEMBER', 'remember'), 'remember')]"
        ]
        for sel in selectors:
            try:
                if sel.startswith("//"):
                    elements = driver.find_elements(By.XPATH, sel)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed():
                        if not el.is_selected():
                            driver.execute_script("arguments[0].click();", el)
                        return
            except Exception:
                continue

    def _find_submit_button(self, driver):
        """Finds login submit button."""
        selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "//button[contains(translate(text(), 'SIGN IN', 'sign in'), 'sign in')]",
            "//button[contains(translate(text(), 'LOG IN', 'log in'), 'log in')]",
            "//button[contains(translate(text(), 'LOGIN', 'login'), 'login')]",
            "//button[contains(translate(text(), 'CONTINUE', 'continue'), 'continue')]",
            "//button[contains(translate(text(), 'NEXT', 'next'), 'next')]"
        ]
        for sel in selectors:
            try:
                if sel.startswith("//"):
                    elements = driver.find_elements(By.XPATH, sel)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception:
                continue
        return None

universal_login_manager = UniversalLoginManager.get_instance()
