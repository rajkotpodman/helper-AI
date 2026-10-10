"""Unit tests for Helper-AI Tool Arsenal."""
import os
import pytest
from pathlib import Path
from core.tools.file_tools import (
    resolve_user_path,
    WriteFileTool,
    ReadFileTool,
    ListDirectoryTool,
    SearchFilesTool,
    MoveOrCopyFileTool
)
from core.tools.system_tools import (
    GetSystemHealthTool,
    ProcessManagerTool,
    ExecutePowerShellTool
)

def test_resolve_user_path():
    home = Path.home()
    assert resolve_user_path("Desktop") in [home / "Desktop", home / "OneDrive" / "Desktop"]
    assert resolve_user_path("Downloads") in [home / "Downloads", home / "OneDrive" / "Downloads"]
    assert resolve_user_path("Documents") in [home / "Documents", home / "OneDrive" / "Documents"]

def test_file_tools_roundtrip(tmp_path):
    test_file = str(tmp_path / "test_artifact.txt")
    
    # 1. Write file
    write_tool = WriteFileTool()
    res_w = write_tool.execute(file_path=test_file, content="Helper-AI Automated Test Content")
    assert res_w["success"] is True
    assert os.path.exists(test_file)

    # 2. Read file
    read_tool = ReadFileTool()
    res_r = read_tool.execute(file_path=test_file)
    assert res_r["success"] is True
    assert "Helper-AI Automated Test Content" in res_r["output"]

    # 3. Search file
    search_tool = SearchFilesTool()
    res_s = search_tool.execute(pattern="*.txt", directory=str(tmp_path))
    assert res_s["success"] is True
    assert len(res_s["matches"]) >= 1

    # 4. Copy file
    copy_dest = str(tmp_path / "copied_artifact.txt")
    move_tool = MoveOrCopyFileTool()
    res_c = move_tool.execute(source=test_file, destination=copy_dest, action="copy")
    assert res_c["success"] is True
    assert os.path.exists(copy_dest)

def test_system_health_tool():
    health_tool = GetSystemHealthTool()
    res = health_tool.execute()
    assert res["success"] is True
    assert "OS:" in res["output"]
    assert "RAM:" in res["output"]
    assert "raw_data" in res

def test_process_manager_list():
    pm_tool = ProcessManagerTool()
    res = pm_tool.execute(action="list", limit=5)
    assert res["success"] is True
    assert "PID" in res["output"]
    assert "Memory %" in res["output"]

def test_execute_powershell_echo():
    ps_tool = ExecutePowerShellTool()
    res = ps_tool.execute(command="Write-Output 'Helper-AI-Online'")
    assert res["success"] is True
    assert "Helper-AI-Online" in res["output"]
