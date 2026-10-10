"""Unit tests for BrowserAutomationTool."""
import pytest
from core.tools.browser_tools import BrowserAutomationTool

def test_browser_tool_schema():
    tool = BrowserAutomationTool()
    schema = tool.to_schema()
    assert schema["name"] == "browser_automation"
    assert "parameters" in schema
    assert "action" in schema["parameters"]["properties"]

def test_draft_social_post():
    tool = BrowserAutomationTool()
    res = tool.execute(
        action="draft_social_post",
        platform="x",
        post_text="Hello world from Helper-AI!",
        open_in_system_browser=False
    )
    assert res["success"] is True
    assert res["platform"] == "x"
    assert "Hello%20world%20from%20Helper-AI%21" in res["compose_url"]
    assert res["requires_user_approval"] is True

def test_draft_social_post_linkedin():
    tool = BrowserAutomationTool()
    res = tool.execute(
        action="draft_social_post",
        platform="linkedin",
        post_text="Exciting update from Helper-AI",
        open_in_system_browser=False
    )
    assert res["success"] is True
    assert res["platform"] == "linkedin"
    assert "linkedin.com" in res["compose_url"]

def test_challenge_detection():
    tool = BrowserAutomationTool()
    
    # Test CAPTCHA pattern
    captcha_html = "<html><body>Please solve this recaptcha to continue</body></html>"
    challenge = tool._detect_challenge_in_html(captcha_html)
    assert challenge["is_challenge"] is True
    assert challenge["category"] == "captcha"

    # Test 2FA pattern
    otp_html = "<html><body>Enter the verification code sent to your email</body></html>"
    challenge2 = tool._detect_challenge_in_html(otp_html)
    assert challenge2["is_challenge"] is True
    assert challenge2["category"] == "two_factor"

    # Test clean page
    clean_html = "<html><body>Welcome to the home page! Everything is normal.</body></html>"
    challenge3 = tool._detect_challenge_in_html(clean_html)
    assert challenge3["is_challenge"] is False

def test_invalid_action():
    tool = BrowserAutomationTool()
    res = tool.execute(action="invalid_action_name")
    assert res["success"] is False

def test_list_blogs_action_registered(monkeypatch):
    tool = BrowserAutomationTool()
    assert "list_blogs" in tool.parameters["properties"]["action"]["enum"]
    
    # Mock _list_blogs
    monkeypatch.setattr(tool, "_list_blogs", lambda: {"success": True, "blogs": ["My Tech Blog", "AI Agent News"], "output": "Found 2 blogs"})
    res = tool.execute(action="list_blogs")
    assert res["success"] is True
    assert len(res["blogs"]) == 2

