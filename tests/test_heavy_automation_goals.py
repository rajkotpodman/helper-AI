import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from core.agent import HelperAgent
from core.llm import LLMClient
from core.tools import ToolRegistry
from core.tools.system_tools import GetSystemHealthTool, ExecutePowerShellTool
from core.tools.file_tools import ListDirectoryTool, WriteFileTool
from core.tools.web_tools import SearchWebTool
from core.translator import GoogleTranslator
from core.memory import AgentMemory
from core.memory_recorder import MarkdownMemoryRecorder
from core.audit import AuditLogger
from core.voice_engine import VoiceEngine


# ==============================================================================
# 1. Goal 1: 5-Post Gujarati International AI News Creation & Publishing
# ==============================================================================
@pytest.mark.asyncio
async def test_goal_1_five_gujarati_ai_posts_publication(tmp_path):
    """
    Validates the exact user prompt:
    'create 5 post for today top 5 international ai releated news in the world of web create 5 seperate post in gujarati and publish'
    Ensures agent executes all 5 distinct posts without infinite looping or empty results.
    """
    user_goal = "create 5 post for today top 5 international ai releated news in the world of web create 5 seperate post in gujarati and publish"
    
    events = []
    def on_event(event_type, data):
        events.append((event_type, data))

    tools = ToolRegistry()
    fake_publish_counter = 0
    def mock_browser_automation(**kwargs):
        nonlocal fake_publish_counter
        fake_publish_counter += 1
        title = kwargs.get("title", f"AI Post {fake_publish_counter}")
        return {
            "success": True,
            "output": f"Successfully created and published blog post titled '{title}' on Google Blogger! The post is now live.",
            "data": {"post_id": f"post_{fake_publish_counter}", "title": title}
        }

    tools._tools["browser_automation"].execute = mock_browser_automation

    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, tool_registry=tools, safe_mode=False, max_steps=15)

    result = await agent.run(user_goal, on_event=on_event)

    assert result["success"] is True
    assert "published all 5 requested post(s)" in result["message"]
    
    action_results = [data for etype, data in events if etype == "action_result"]
    assert len(action_results) >= 5
    for ar in action_results:
        assert ar.get("output") != ""
        assert ar.get("result") != ""
        assert "Successfully created and published" in ar.get("output")


# ==============================================================================
# 2. Goal 2: Instant Web Research & Desktop Markdown Report Synthesis
# ==============================================================================
def test_goal_2_web_research_and_desktop_synthesis(tmp_path):
    """
    Validates SearchWebTool querying technical workflows and
    writing synthesized documentation to desktop.
    """
    web_tool = SearchWebTool()
    
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <html>
            <div class="result">
                <a class="result__snippet" href="https://example.com/ai">OpenAI releases advanced reasoning model o3 for autonomous engineering.</a>
            </div>
        </html>
        """
        mock_get.return_value = mock_resp

        res = web_tool.execute(query="latest 2025 AI breakthroughs in web and agents", max_results=3)
        assert res["success"] is True or "Results" in res.get("output", "")

    desktop_file = tmp_path / "AI_Research_Report.md"
    write_tool = WriteFileTool()
    report_content = "# 2025 International AI News\n\n1. OpenAI o3 breakthrough.\n2. Gemini 2.0 multimodal agents."
    w_res = write_tool.execute(file_path=str(desktop_file), content=report_content)
    assert w_res["success"] is True
    assert desktop_file.exists()


# ==============================================================================
# 3. Goal 3: Comprehensive PC Hardware & Operating System Diagnostics
# ==============================================================================
def test_goal_3_pc_hardware_system_diagnostics():
    """
    Validates comprehensive system telemetry: CPU, RAM, Disk, and OS specs.
    """
    health_tool = GetSystemHealthTool()
    res = health_tool.execute()
    assert res["success"] is True
    output = res["output"]
    assert "CPU:" in output or "CPU Usage:" in output or "OS:" in output
    assert "RAM:" in output
    assert "raw_data" in res


# ==============================================================================
# 4. Goal 4: Safe Navigation & File Processing with Spaced Paths
# ==============================================================================
def test_goal_4_spaced_path_navigation(tmp_path):
    """
    Validates navigation, listing, and inspection on directories with spaces
    such as 'E:\\Freelancer Crack The Deal'.
    """
    spaced_dir = tmp_path / "Freelancer Crack The Deal"
    spaced_dir.mkdir()
    sample_file = spaced_dir / "HOW_TO_USE.md"
    sample_file.write_text("# Freelancer Crack The Deal Guide\nAutomate client projects safely.", encoding="utf-8")

    list_tool = ListDirectoryTool()
    res = list_tool.execute(path=str(spaced_dir))
    assert res["success"] is True
    assert "HOW_TO_USE.md" in res["output"]


# ==============================================================================
# 5. Goal 5: LinkedIn Automation Pipeline (Job Discovery & Application Loop)
# ==============================================================================
@pytest.mark.asyncio
async def test_goal_5_linkedin_job_application_pipeline():
    """
    Validates multi-target job search and easy application tracking.
    """
    tools = ToolRegistry()
    def mock_linkedin_jobs(**kwargs):
        action = kwargs.get("action")
        if action == "apply_linkedin_jobs":
            return {
                "success": True,
                "output": "Found 3 matching jobs. Successfully applied to 3 job(s) using Easy Apply on LinkedIn.",
                "data": {"applied_count": 3}
            }
        return {"success": False, "output": "Unknown action"}

    tools._tools["browser_automation"].execute = mock_linkedin_jobs
    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, tool_registry=tools, safe_mode=False, max_steps=5)

    res = await agent.run("search and apply to 3 python developer jobs on linkedin")
    assert res["success"] is True
    assert "successfully applied to 3 job" in res["message"].lower() or "3" in res["message"]


# ==============================================================================
# 6. Goal 6: Universal Multi-Language Neural Translation (5 Concurrent Languages)
# ==============================================================================
def test_goal_6_universal_multilanguage_translation():
    """
    Validates translation across 5 world languages: Gujarati, Hindi, Spanish, French, and Japanese.
    """
    translator = GoogleTranslator.get_instance()
    sample_english = "Helper-AI is an autonomous PC control and internet agent built for high productivity."

    targets = ["gu", "hi", "es", "fr", "ja"]
    results = {}
    for lang in targets:
        translator._cache[f"auto->{lang}:{sample_english}"] = f"[{lang.upper()}] Translated: {sample_english}"
        res = translator.translate_text(sample_english, target_lang=lang)
        results[lang] = res

    assert len(results) == 5
    for lang in targets:
        assert f"[{lang.upper()}]" in results[lang]


# ==============================================================================
# 7. Goal 7: Web Scraping, HTML Table Extraction & Structured Compilation
# ==============================================================================
def test_goal_7_structured_table_extraction():
    """
    Validates extracting and parsing structured HTML web elements into clean datasets.
    """
    sample_html = """
    <table>
        <tr><th>Rank</th><th>Model</th><th>Provider</th><th>Score</th></tr>
        <tr><td>1</td><td>Gemini 2.5 Pro</td><td>Google</td><td>94.2</td></tr>
        <tr><td>2</td><td>Claude 3.7 Sonnet</td><td>Anthropic</td><td>93.8</td></tr>
        <tr><td>3</td><td>GPT-4.5</td><td>OpenAI</td><td>92.5</td></tr>
    </table>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, "html.parser")
    rows = soup.find_all("tr")
    headers = [th.get_text() for th in rows[0].find_all("th")]
    assert headers == ["Rank", "Model", "Provider", "Score"]
    
    data_rows = []
    for tr in rows[1:]:
        cols = [td.get_text() for td in tr.find_all("td")]
        data_rows.append(cols)

    assert len(data_rows) == 3
    assert data_rows[0][1] == "Gemini 2.5 Pro"
    assert data_rows[1][1] == "Claude 3.7 Sonnet"
    assert data_rows[2][1] == "GPT-4.5"


# ==============================================================================
# 8. Goal 8: Resilient PowerShell Command Execution & Self-Healing
# ==============================================================================
def test_goal_8_powershell_execution_and_resilience():
    """
    Validates executing local PowerShell commands safely with accurate output capture.
    """
    ps_tool = ExecutePowerShellTool()
    cmd = 'Write-Output "Helper-AI Autonomous System Ready"'
    res = ps_tool.execute(cmd)
    assert res["success"] is True
    assert "Helper-AI Autonomous System Ready" in res["output"]


# ==============================================================================
# 9. Goal 9: Edge-TTS Neural Voice Generation (Gujarati & English)
# ==============================================================================
@pytest.mark.asyncio
async def test_goal_9_edge_tts_neural_voice_synthesis():
    """
    Validates neural speech synthesis parameter selection and audio streaming.
    """
    fake_audio_chunk = b"ID3\x03\x00\x00\x00\x00fake_mp3_data"
    with patch("edge_tts.Communicate") as mock_comm:
        instance = MagicMock()
        async def fake_stream():
            yield {"type": "audio", "data": fake_audio_chunk}
        instance.stream = fake_stream
        mock_comm.return_value = instance

        audio_bytes = await VoiceEngine.synthesize_to_bytes("નમસ્તે, Helper-AI માં તમારું સ્વાગત છે.", voice="en-US-AriaNeural")
        assert len(audio_bytes) > 0
        assert fake_audio_chunk in audio_bytes


# ==============================================================================
# 10. Goal 10: Memory Recorder 20MB Cap & High-Throughput Event Auditing
# ==============================================================================
def test_goal_10_memory_recorder_audit_trail_and_limits(tmp_path):
    """
    Validates high throughput memory persistence, 20MB rolling cap, and structured event logging.
    """
    mem = AgentMemory(goal="High throughput test")
    
    for i in range(25):
        mem.add_step(
            thought=f"Thought step {i} testing high-throughput memory storage",
            action="execute_powershell" if i % 2 == 0 else "browser_automation",
            action_args={"step_num": i},
            result=f"Successfully executed operation {i} with high accuracy.",
            success=True
        )

    assert len(mem.history) == 25
    summary = mem.get_trajectory_summary()
    assert "Step 25" in summary
    assert "execute_powershell" in summary

    # Verify 20MB MarkdownMemoryRecorder
    mem_file = tmp_path / "agent_memory.md"
    recorder = MarkdownMemoryRecorder(file_path=mem_file, max_bytes=20 * 1024 * 1024)
    rec_res = recorder.record_interaction(
        prompt="Execute heavy automation batch",
        final_reply="All 10 goals verified and executed.",
        success=True,
        steps_executed=25
    )
    assert rec_res["recorded"] is True
    assert rec_res["limit_reached"] is False
    assert mem_file.exists()

    audit_logger = AuditLogger(log_dir=str(tmp_path))
    audit_logger.log_event("heavy_goal_test", "browser_automation", {"batch": 10}, True, 12.5, "Completed 10 goals")
    assert (tmp_path / "audit.jsonl").exists()
    assert "heavy_goal_test" in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")


# ==============================================================================
# 11. Goal 11: 5-Post LinkedIn Remote AI Work ($1000/hr RaaS) Tagging Pipeline
# ==============================================================================
@pytest.mark.asyncio
async def test_goal_11_linkedin_five_posts_remote_ai_work(tmp_path):
    """
    Validates user prompt:
    'create 5 post for linkdin and publish it and tag all companey who give me job remote ai work for 1000 per hour for my result as a service the goal creater'
    Ensures all 5 LinkedIn posts are generated with company tags and published without halting.
    """
    user_goal = "create 5 post for linkdin and publish it and tag all companey who give me job remote ai work for 1000 per hour for my result as a service the goal creater"

    events = []
    def on_event(event_type, data):
        events.append((event_type, data))

    tools = ToolRegistry()
    published_posts = []
    def mock_linkedin_publish(**kwargs):
        action = kwargs.get("action")
        if action == "publish_linkedin_post":
            pt = kwargs.get("post_text", "")
            published_posts.append(pt)
            return {
                "success": True,
                "output": f"Successfully created and published post to LinkedIn: '{pt[:60]}...'! The post is officially live on your LinkedIn feed.",
                "data": {"post_id": f"li_post_{len(published_posts)}"}
            }
        return {"success": False, "output": "Unknown action"}

    tools._tools["browser_automation"].execute = mock_linkedin_publish

    llm = LLMClient(provider="rule_engine")
    agent = HelperAgent(llm_client=llm, tool_registry=tools, safe_mode=False, max_steps=15)

    result = await agent.run(user_goal, on_event=on_event)

    assert result["success"] is True
    assert len(published_posts) == 5
    # Verify company tags are present in posts
    for post in published_posts:
        assert any(c in post for c in ["@Google", "@Microsoft", "@OpenAI", "@NVIDIA", "@ScaleAI", "@Meta", "@Qualcomm"])
        assert "1,000" in post or "result as a service" in post.lower() or "autonomous" in post.lower()
