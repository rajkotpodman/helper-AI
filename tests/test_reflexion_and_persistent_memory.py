"""Comprehensive test suite for Reflexion Ground-Truth Evaluator and Persistent Multi-Session Memory."""

import os
import tempfile
import pytest
from pathlib import Path
from core.persistent_memory import PersistentMemoryManager
from core.evaluator import GroundTruthEvaluator, EvaluationResult


class TestPersistentMemory:
    """Tests for SQLite + Mem0 Multi-Session Memory Engine."""

    @pytest.fixture
    def temp_memory(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name
        manager = PersistentMemoryManager(db_path=Path(db_path))
        yield manager
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except Exception:
                pass

    def test_remember_and_get_repos(self, temp_memory):
        temp_memory.remember_repo(
            "rajkotpodman/helper-AI",
            "Autonomous AI Agent with full PC and Internet control",
            "Python",
            42
        )
        temp_memory.remember_repo(
            "rajkotpodman/gst-billing",
            "Enterprise GST Billing System",
            "TypeScript",
            15
        )

        repos = temp_memory.get_known_repos(limit=10)
        assert len(repos) == 2
        names = [r["full_name"] for r in repos]
        assert "rajkotpodman/helper-AI" in names
        assert "rajkotpodman/gst-billing" in names

    def test_remember_and_query_posts(self, temp_memory):
        post_id = temp_memory.remember_post(
            platform="facebook",
            content="૧. GitHub Repository: rajkotpodman/helper-AI વિગતવાર માહિતી",
            repo_name="rajkotpodman/helper-AI",
            language="gu",
            status="published",
            is_verified=True,
            file_path="C:/Users/DELL/Desktop/Facebook_Posts/FB_helper_ai.txt"
        )
        assert post_id > 0

        # Check repo posted verification
        assert temp_memory.is_repo_already_posted("rajkotpodman/helper-AI", "facebook") is True
        assert temp_memory.is_repo_already_posted("rajkotpodman/other-repo", "facebook") is False

        # Query posts
        fb_posts = temp_memory.get_posts(platform="facebook")
        assert len(fb_posts) == 1
        assert fb_posts[0]["repo_name"] == "rajkotpodman/helper-AI"
        assert fb_posts[0]["is_verified"] == 1

    def test_facts_and_preferences(self, temp_memory):
        temp_memory.remember_fact("user_preference", "language", "gujarati")
        val = temp_memory.get_fact("user_preference", "language")
        assert val == "gujarati"

        # Update fact
        temp_memory.remember_fact("user_preference", "language", "english_and_gujarati")
        val2 = temp_memory.get_fact("user_preference", "language")
        assert val2 == "english_and_gujarati"

    def test_reflection_logging_and_prompt_formatting(self, temp_memory):
        temp_memory.remember_repo("rajkotpodman/helper-AI", "AI Agent")
        temp_memory.record_reflection(
            action="publish_facebook_post",
            target="rajkotpodman/helper-AI",
            was_successful=False,
            ground_truth_details="Facebook session unauthenticated",
            failure_reason="FACEBOOK_NOT_LOGGED_IN",
            suggested_fix="Log in to Facebook once in Chrome"
        )

        reflections = temp_memory.get_recent_reflections(limit=5)
        assert len(reflections) == 1
        assert reflections[0]["failure_reason"] == "FACEBOOK_NOT_LOGGED_IN"

        prompt_context = temp_memory.format_memory_for_prompt("create facebook posts")
        assert "KNOWN GITHUB REPOSITORIES" in prompt_context
        assert "GROUND-TRUTH REFLEXION LESSONS" in prompt_context
        assert "rajkotpodman/helper-AI" in prompt_context


class TestGroundTruthEvaluator:
    """Tests for Reflexion-style Ground-Truth Evaluator."""

    @pytest.fixture
    def evaluator(self):
        return GroundTruthEvaluator.get_instance()

    def test_evaluate_github_repo_listing(self, evaluator):
        tool_res = {
            "success": True,
            "output": (
                "rajkotpodman/helper-AI\tAutonomous AI Agent\tpublic\t2026-10-18\n"
                "rajkotpodman/gst-billing\tGST Billing System\tpublic\t2026-10-16\n"
            )
        }
        res = evaluator.evaluate(
            "execute_powershell",
            {"command": "gh repo list rajkotpodman --limit 5"},
            tool_res
        )
        assert res.is_verified is True
        assert res.metadata.get("repos_cached") == 2
        assert "cached 2 repository records" in res.ground_truth_evidence

    def test_evaluate_github_auth_failure(self, evaluator):
        tool_res = {
            "success": False,
            "output": "gh: You are not logged into any GitHub hosts. Run gh auth login to authenticate."
        }
        res = evaluator.evaluate(
            "execute_powershell",
            {"command": "gh repo list"},
            tool_res
        )
        assert res.is_verified is False
        assert res.failure_reason == "GITHUB_AUTH_OR_CLI_MISSING"
        assert "gh auth login" in res.suggested_fix

    def test_evaluate_file_operation(self, evaluator):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            tf.write(b"Deeply described Gujarati post content")
            t_path = tf.name

        tool_res = {"success": True, "output": f"Successfully written to {t_path}"}
        res = evaluator.evaluate("write_file", {"path": t_path}, tool_res)
        assert res.is_verified is True
        assert res.metadata.get("file_size") > 0

        # Clean up
        os.unlink(t_path)

        # Test non-existent file evaluation
        res_missing = evaluator.evaluate("write_file", {"path": "C:/invalid/non_existent_file_999.xyz"}, {"success": True})
        assert res_missing.is_verified is False
        assert res_missing.failure_reason == "FILE_NOT_FOUND_AFTER_WRITE"

    def test_evaluate_facebook_unauthenticated_rejection(self, evaluator):
        tool_res = {
            "success": False,
            "error": "FACEBOOK_LOGIN_REQUIRED",
            "output": "Project browser is on Facebook login page."
        }
        res = evaluator.evaluate(
            "browser_automation",
            {"action": "publish_facebook_post", "post_text": "demo"},
            tool_res
        )
        assert res.is_verified is False
        assert res.failure_reason is not None
        assert "Facebook" in res.ground_truth_evidence or "Facebook" in str(res.failure_reason)

    def test_evaluate_blogger_unauthenticated_rejection(self, evaluator):
        tool_res = {
            "success": False,
            "error": "BLOGGER_AUTH_REQUIRED",
            "output": "Google account sign-in required."
        }
        res = evaluator.evaluate(
            "browser_automation",
            {"action": "publish_blog_post", "title": "Test Title", "content": "Body"},
            tool_res
        )
        assert res.is_verified is False
        assert res.failure_reason is not None


class TestAgentIntegration:
    """Verifies HelperAgent integration with Persistent Memory and GroundTruthEvaluator."""

    def test_agent_has_evaluator_and_memory(self):
        from core.agent import HelperAgent
        agent = HelperAgent()
        assert hasattr(agent, "persistent_memory")
        assert hasattr(agent, "evaluator")
        assert agent.persistent_memory is not None
        assert agent.evaluator is not None
