"""Unit tests for Helper-AI Agent Memory and Trajectory."""
import json
from core.memory import AgentMemory, StepRecord

def test_agent_memory_flow():
    goal = "Perform system health diagnostic and cleanup"
    memory = AgentMemory(goal=goal)

    assert memory.goal == goal
    assert len(memory.history) == 0

    # Step 1
    s1 = memory.add_step(
        thought="I will inspect hardware specs.",
        action="get_system_health",
        action_args={},
        result="RAM: 8GB total, CPU 15%",
        success=True
    )
    assert s1.step_number == 1
    assert len(memory.history) == 1

    # Step 2
    s2 = memory.add_step(
        thought="Everything looks healthy.",
        action="none",
        action_args={},
        result="Done",
        success=True
    )
    assert s2.step_number == 2

    # Trajectory summary
    traj = memory.get_trajectory_summary()
    assert "Step 1:" in traj
    assert "get_system_health" in traj
    assert "Step 2:" in traj

    # JSON Export
    exported = memory.export_json()
    data = json.loads(exported)
    assert data["goal"] == goal
    assert len(data["steps"]) == 2
    assert data["steps"][0]["action"] == "get_system_health"
