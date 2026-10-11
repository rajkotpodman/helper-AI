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

def test_publish_linkedin_post_registered(monkeypatch):
    tool = BrowserAutomationTool()
    assert "publish_linkedin_post" in tool.parameters["properties"]["action"]["enum"]

    monkeypatch.setattr(tool, "_publish_linkedin_post", lambda content: {"success": True, "output": "Published to LinkedIn", "content": content})
    res = tool.execute(action="publish_linkedin_post", post_text="Test post")
    assert res["success"] is True
    assert res["content"] == "Test post"

def test_apply_linkedin_jobs_registered(monkeypatch):
    tool = BrowserAutomationTool()
    assert "apply_linkedin_jobs" in tool.parameters["properties"]["action"]["enum"]

    monkeypatch.setattr(
        tool,
        "_apply_linkedin_jobs",
        lambda keywords, resume_path, count: {
            "success": True,
            "applied_count": 2,
            "applied_jobs": [{"title": "Tech Support", "company": "Acme"}],
            "output": "Applied to 2 jobs"
        }
    )
    res = tool.execute(action="apply_linkedin_jobs", keywords="Technical Support", count=2)
    assert res["success"] is True
    assert res["applied_count"] == 2


def test_rule_engine_repetition_count():
    from core.llm import LLMClient
    client = LLMClient(provider="rule_engine")
    goal = "this is my cv apply in more 5 space on linkdin offline copy C:\\Users\\DELL\\Downloads\\Jignesh_Kariya_CV (1).docx"
    
    # First step: should request 5 jobs and not be complete
    step1 = client._rule_engine_step(goal, "No previous steps executed yet.")
    assert step1["is_complete"] is False
    assert step1["action"] == "browser_automation"
    assert step1["action_args"]["action"] == "apply_linkedin_jobs"
    assert step1["action_args"]["count"] >= 5

    # If only 1 job applied in trajectory, it should NOT mark complete
    step2 = client._rule_engine_step(goal, "Successfully applied to 1 job(s) on LinkedIn with Easy Apply!")
    assert step2["is_complete"] is False
    assert step2["action"] == "browser_automation"
    assert step2["action_args"]["action"] == "apply_linkedin_jobs"

    # Only when all 5 jobs are applied in trajectory should it mark complete
    step3 = client._rule_engine_step(goal, "Successfully applied to 5 job(s) on LinkedIn with Easy Apply!")
    assert step3["is_complete"] is True
    assert step3["action"] == "none"


def test_fetch_web_content_tool(monkeypatch):
    from core.tools.web_tools import FetchWebContentTool
    tool = FetchWebContentTool()

    class FakeResponse:
        status_code = 200
        text = "<html><head><title>Test Page</title></head><body><h1>Main Heading</h1><p>This is the full readable article content.</p><a href='/next'>Next Page</a></body></html>"
        def raise_for_status(self):
            pass

    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse())
    res = tool.execute(url="https://example.com/article")
    assert res["success"] is True
    assert res["title"] == "Test Page"
    assert "Main Heading" in res["output"]
    assert "full readable article content" in res["content"]


def test_browser_actions_registered():
    tool = BrowserAutomationTool()
    for act in ["fetch_full_page", "scroll", "take_screenshot", "select_dropdown", "execute_script"]:
        assert act in tool.parameters["properties"]["action"]["enum"]


def test_desktop_gui_control_extended(monkeypatch):
    from core.tools.desktop_gui_tools import DesktopGUIControlTool
    tool = DesktopGUIControlTool()

    # Test clipboard copy & paste
    res_copy = tool.execute(action="clipboard_copy", text="Test Clipboard Content")
    assert res_copy["success"] is True

    res_paste = tool.execute(action="clipboard_paste")
    assert res_paste["success"] is True
    assert res_paste["clipboard"] == "Test Clipboard Content"

    # Test hotkey action
    res_hotkey = tool.execute(action="hotkey", keys="ctrl+c")
    assert res_hotkey["success"] is True
    assert res_hotkey["hotkey"] == ["ctrl", "c"]




