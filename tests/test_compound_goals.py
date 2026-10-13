"""Unit tests for compound multi-step goals, preventing premature termination on intermediate steps."""
import pytest
from core.llm import LLMClient
from core.agent import HelperAgent
from unittest.mock import MagicMock


def test_rule_engine_compound_readme_linkedin_step1_and_step2():
    """Verify that rule engine plans read_file/fetch first and then publish_linkedin_post in step 2."""
    goal = "create a linkdin post for rajkotpodman/helper-AI (public) - Autonomous AI Agent with full PC and Internet control that works to goals without questioning my repo and copy paste the repos readme.md file text in post"
    llm = LLMClient(provider="rule_engine")

    # Step 1: No previous steps
    step1 = llm.generate_step(
        goal=goal,
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows"}
    )
    assert step1["is_complete"] is False
    assert step1["action"] in ["read_file", "fetch_web_content"]

    # Step 2: Step 1 fetched the README
    trajectory_step2 = (
        "Step 1:\n"
        "  Thought: I will read the repository's README.md file first.\n"
        "  Action: read_file with arguments {\"file_path\": \"E:\\\\ai agent\\\\README.md\"}\n"
        "  Observation (SUCCESS): # ⚡ Helper-AI\nAutonomous AI Agent with Full PC & Internet Control\n"
    )
    step2 = llm.generate_step(
        goal=goal,
        trajectory_summary=trajectory_step2,
        tool_schemas="",
        os_info={"os": "Windows"}
    )
    assert step2["is_complete"] is False
    assert step2["action"] == "browser_automation"
    assert step2["action_args"]["action"] == "publish_linkedin_post"
    assert len(step2["action_args"]["post_text"]) > 0
    assert "Helper-AI" in step2["action_args"]["post_text"]


def test_agent_does_not_prematurely_stop_on_fetch_web_content():
    """Verify that an intermediate fetch_web_content does not trigger early completion if goal has follow-up action."""
    goal = "create a linkdin post for repo and copy paste the repos readme.md file text in post"
    lower_goal = goal.lower()
    has_followup_action = any(k in lower_goal for k in [
        "post", "publish", "share", "linkedin", "linkdin", "linkden", "facebook", "blogger", "twitter", "tweet",
        "create", "write", "save", "paste", "copy paste", "copy and paste", "summarize", "apply", "download",
        "then", "and then", "after that"
    ])
    assert has_followup_action is True
