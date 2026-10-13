"""Unit tests for exhaustive GitHub repository fetching, trajectory preservation, and presentation."""
import pytest
from core.memory import AgentMemory
from core.llm import LLMClient
from core.tools.web_tools import FetchWebContentTool


def test_rule_engine_github_repos_step1():
    """Verify that rule engine uses --limit 100 so all repositories are fetched."""
    llm = LLMClient(provider="rule_engine")
    step = llm.generate_step(
        goal="list or all github repos",
        trajectory_summary="No previous steps executed yet.",
        tool_schemas="",
        os_info={"os": "Windows"}
    )
    assert step["action"] == "execute_powershell"
    assert "gh repo list --limit 100" in step["action_args"]["command"]
    assert step["is_complete"] is False


def test_rule_engine_github_repos_step2_all_parsed():
    """Verify that rule engine parses all repositories in observation and produces 100% complete list."""
    llm = LLMClient(provider="rule_engine")
    # Simulate trajectory from gh repo list containing 29 repositories
    sample_repos = [
        "rajkotpodman/helper-AI\tAutonomous AI Agent with full PC\tpublic\t2026-10-12T13:20:42Z",
        "rajkotpodman/Worlds-First-Quantum-crypto-9898048483\tWorld's First Post-Quantum Cryptographic Token\tpublic\t2026-10-12T02:16:30Z",
        "rajkotpodman/Import-Module\t\tprivate\t2026-10-09T05:18:47Z",
        "rajkotpodman/Universal-Local-Signing-Bridge-usb-token\tUniversal Local Signing Bridge\tpublic\t2026-10-08T15:11:05Z",
        "rajkotpodman/rclone-cloud-manager\t\tpublic\t2026-10-04T13:19:32Z",
        "rajkotpodman/jigsi-karia-search\tCyber intelligence dashboard\tpublic\t2026-09-24T11:11:10Z"
    ]
    trajectory = (
        "Step 1:\n"
        "  Thought: I will execute gh repo list --limit 100 to fetch all repositories.\n"
        "  Action: execute_powershell with arguments {\"command\": \"gh repo list --limit 100\"}\n"
        "  Observation (SUCCESS):\n" + "\n".join(sample_repos)
    )

    step = llm.generate_step(
        goal="list or all github repos",
        trajectory_summary=trajectory,
        tool_schemas="",
        os_info={"os": "Windows"}
    )
    assert step["is_complete"] is True
    assert step["action"] == "none"
    comp_msg = step["completion_message"]
    assert "6 GitHub repositories" in comp_msg
    assert "rajkotpodman/helper-AI" in comp_msg
    assert "rajkotpodman/Import-Module (Private)" in comp_msg
    assert "rajkotpodman/jigsi-karia-search" in comp_msg


def test_fetch_web_content_json_endpoint(monkeypatch):
    """Verify FetchWebContentTool parses JSON API lists into clean, readable items."""
    tool = FetchWebContentTool()

    # Mock requests.get returning a JSON array of repositories
    class MockResponse:
        status_code = 200
        headers = {"Content-Type": "application/json; charset=utf-8"}
        def raise_for_status(self): pass
        def json(self):
            return [
                {
                    "name": "helper-AI",
                    "full_name": "rajkotpodman/helper-AI",
                    "private": False,
                    "description": "Autonomous AI Agent",
                    "html_url": "https://github.com/rajkotpodman/helper-AI",
                    "language": "Python",
                    "stargazers_count": 5
                },
                {
                    "name": "secret-vault",
                    "full_name": "rajkotpodman/secret-vault",
                    "private": True,
                    "description": "Private Vault",
                    "html_url": "https://github.com/rajkotpodman/secret-vault",
                    "language": "Go",
                    "stargazers_count": 0
                }
            ]

    import requests
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())

    res = tool.execute("https://api.github.com/users/rajkotpodman/repos?per_page=100")
    assert res["success"] is True
    assert res["items_count"] == 2
    assert "helper-AI [Public] - Autonomous AI Agent" in res["output"]
    assert "secret-vault [Private] - Private Vault" in res["output"]
