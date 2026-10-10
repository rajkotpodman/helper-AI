"""Unit tests for Facebook automation and ProjectBrowser enhancements."""
import pytest
from core.tools.browser_tools import BrowserAutomationTool

def test_facebook_post_action_in_schema():
    tool = BrowserAutomationTool()
    schema = tool.to_schema()
    actions = schema["parameters"]["properties"]["action"]["enum"]
    assert "publish_facebook_post" in actions

def test_facebook_challenge_detector():
    tool = BrowserAutomationTool()
    html_2fa = "<div>Please enter the two-factor authentication code sent to your device</div>"
    res = tool._detect_challenge_in_html(html_2fa)
    assert res["is_challenge"] is True
    assert res["category"] == "two_factor"
