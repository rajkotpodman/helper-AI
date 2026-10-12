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


def test_rule_engine_facebook_5_posts_how_to_use():
    from core.llm import LLMClient
    client = LLMClient(provider="rule_engine")
    goal = "create facebook posts E:\\ai agent\\HOW_TO_USE.md content in 5 defferent post in gujarati describe howtouse.md file in 5 posts and publish minimum 200 lines in each post"

    # Step 1: Must read HOW_TO_USE.md first
    step1 = client._rule_engine_step(goal, "No previous steps executed yet.")
    assert step1["is_complete"] is False
    assert step1["action"] == "read_file"
    assert "HOW_TO_USE.md" in step1["action_args"]["file_path"]

    # Step 2: After file read, must generate Part 1 in Gujarati
    traj_after_read = "Step 1: read_file HOW_TO_USE.md - Success: Read 25000 chars"
    step2 = client._rule_engine_step(goal, traj_after_read)
    assert step2["is_complete"] is False
    assert step2["action"] == "browser_automation"
    assert step2["action_args"]["action"] == "publish_facebook_post"
    assert "ભાગ ૧" in step2["action_args"]["post_text"]
    assert "Helper-AI" in step2["action_args"]["post_text"]

    # Step 3: After post 1 published, must generate Part 2 in Gujarati
    traj_after_post1 = traj_after_read + "\nStep 2: Successfully created and published post to Facebook! The post is officially live on your timeline/feed."
    step3 = client._rule_engine_step(goal, traj_after_post1)
    assert step3["is_complete"] is False
    assert step3["action"] == "browser_automation"
    assert "ભાગ ૨" in step3["action_args"]["post_text"]

    # Step 4: After post 2 published, must generate Part 3 in Gujarati
    traj_after_post2 = traj_after_post1 + "\nStep 3: Successfully created and published post to Facebook! The post is officially live on your timeline/feed."
    step4 = client._rule_engine_step(goal, traj_after_post2)
    assert step4["is_complete"] is False
    assert "ભાગ ૩" in step4["action_args"]["post_text"]

    # Step 5: After post 3 published, must generate Part 4
    traj_after_post3 = traj_after_post2 + "\nStep 4: Successfully created and published post to Facebook! The post is officially live on your timeline/feed."
    step5 = client._rule_engine_step(goal, traj_after_post3)
    assert step5["is_complete"] is False
    assert "ભાગ ૪" in step5["action_args"]["post_text"]

    # Step 6: After post 4 published, must generate Part 5
    traj_after_post4 = traj_after_post3 + "\nStep 5: Successfully created and published post to Facebook! The post is officially live on your timeline/feed."
    step6 = client._rule_engine_step(goal, traj_after_post4)
    assert step6["is_complete"] is False
    assert "ભાગ ૫" in step6["action_args"]["post_text"]

    # Step 7: After post 5 published, all 5 posts are done -> is_complete MUST be True!
    traj_after_post5 = traj_after_post4 + "\nStep 6: Successfully created and published post to Facebook! The post is officially live on your timeline/feed."
    step7 = client._rule_engine_step(goal, traj_after_post5)
    assert step7["is_complete"] is True
    assert step7["action"] == "none"
    assert "5" in step7["completion_message"]


@pytest.mark.asyncio
async def test_agent_multi_post_loop_execution(monkeypatch, tmp_path):
    from core.agent import HelperAgent
    from core.llm import LLMClient
    from core.memory_recorder import MarkdownMemoryRecorder

    client = LLMClient(provider="rule_engine")
    mem_file = tmp_path / "test_multi_mem.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file)
    agent = HelperAgent(llm_client=client, memory_recorder=recorder, max_steps=10)

    # Mock tool executions so no real browser or real files are touched
    def mock_execute(action, action_args):
        if action == "read_file":
            return {"success": True, "output": "# Mock HOW_TO_USE content with 200 lines"}
        elif action == "browser_automation":
            post_txt = action_args.get("post_text", "")
            return {
                "success": True,
                "output": f"Successfully created and published post to Facebook: '{post_txt[:60]}...'! The post is officially live on your timeline/feed."
            }
        return {"success": True, "output": "OK"}

    monkeypatch.setattr(agent.tools, "execute", mock_execute)

    goal = "create facebook posts E:\\ai agent\\HOW_TO_USE.md content in 5 defferent post in gujarati describe howtouse.md file in 5 posts and publish minimum 200 lines in each post"
    res = await agent.run(goal=goal)

    assert res["success"] is True
    # History should contain 1 read_file step + 5 browser_automation steps = 6 steps total
    assert len(res["history"]) == 6
    post_steps = [s for s in res["history"] if s["action"] == "browser_automation"]
    assert len(post_steps) == 5
    # Verify all 5 Gujarati parts were published
    assert any("ભાગ ૧" in s["action_args"]["post_text"] for s in post_steps)
    assert any("ભાગ ૨" in s["action_args"]["post_text"] for s in post_steps)
    assert any("ભાગ ૩" in s["action_args"]["post_text"] for s in post_steps)
    assert any("ભાગ ૪" in s["action_args"]["post_text"] for s in post_steps)
    assert any("ભાગ ૫" in s["action_args"]["post_text"] for s in post_steps)

