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

def test_facebook_publish_action_delegation(monkeypatch):
    tool = BrowserAutomationTool()
    monkeypatch.setattr(tool, "_publish_facebook_post", lambda content: {
        "success": True,
        "output": f"Successfully created and published post to Facebook: '{content[:80]}...'!",
        "content": content
    })
    res = tool.execute(action="publish_facebook_post", post_text="Test announcement")
    assert res["success"] is True
    assert "Successfully created and published" in res["output"]

def test_rule_engine_facebook_repo_goal():
    from core.llm import LLMClient
    client = LLMClient(provider="rule_engine")
    goal = "create and publish facebook post on the my repo https://github.com/rajkotpodman/helper-AI"

    # Step 1: should generate publish_facebook_post with repo url inside text
    step1 = client._rule_engine_step(goal, "No steps executed yet.")
    assert step1["is_complete"] is False
    assert step1["action"] == "browser_automation"
    assert step1["action_args"]["action"] == "publish_facebook_post"
    assert "https://github.com/rajkotpodman/helper-AI" in step1["action_args"]["post_text"]

    # When published output is received, should mark complete
    step2 = client._rule_engine_step(goal, "Successfully created and published post to Facebook! The post is officially live on your timeline/feed.")
    assert step2["is_complete"] is True
    assert step2["action"] == "none"

def test_gemini_automatic_failover(monkeypatch):
    from core.llm import LLMClient
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key_123")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")

    client = LLMClient(provider="groq")
    # Simulate groq failure (e.g. 429)
    monkeypatch.setattr(client, "_call_groq", lambda sys_p, user_p: (_ for _ in ()).throw(RuntimeError("429 Rate limit reached")))
    monkeypatch.setattr(client, "_call_gemini", lambda sys_p, user_p: {
        "thought": "Executed with Gemini failover",
        "action": "browser_automation",
        "action_args": {"action": "click", "target": "Post"},
        "is_complete": False,
        "completion_message": ""
    })

    res = client.generate_step("publish facebook post", "history", "schemas", {})
    assert client.provider == "gemini"
    assert "Executed with Gemini failover" in res["thought"]
    assert res["action"] == "browser_automation"

