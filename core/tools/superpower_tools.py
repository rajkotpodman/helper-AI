"""Superpower Tools for Helper-AI.

Exposes deep research dossiers, multi-phase pipeline orchestration,
code studio scaffolding, and system performance diagnostics.
"""

from typing import Dict, Any, Optional, List
from core.tools.base import BaseTool
from core.superpowers.research_engine import SuperpowerResearchEngine
from core.superpowers.orchestrator import SuperpowerOrchestrator
from core.superpowers.code_studio import SuperpowerCodeStudio
from core.superpowers.system_optimizer import SuperpowerSystemOptimizer


class DeepResearchStudioTool(BaseTool):
    """Executes multi-query deep web research and synthesizes comprehensive intelligence dossiers."""

    name = "deep_research_studio"
    description = (
        "Perform exhaustive multi-query web research on any topic. "
        "Expands queries, concurrently fetches verified sources, distills insights, "
        "and synthesizes a publication-grade executive dossier in markdown."
    )
    parameters = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic, question, or technology to research deeply."
            },
            "max_sources": {
                "type": "integer",
                "default": 6,
                "description": "Maximum number of distinct web sources to analyze."
            },
            "save_path": {
                "type": "string",
                "description": "Optional file path to save the generated markdown dossier (e.g. 'Desktop/report.md')."
            }
        },
        "required": ["topic"]
    }

    def execute(
        self,
        topic: str,
        max_sources: int = 6,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        engine = SuperpowerResearchEngine()
        return engine.perform_deep_research(topic=topic, max_sources=max_sources, save_path=save_path)


class OrchestrateComplexGoalTool(BaseTool):
    """Plans and structures massive multi-step goals into verified 5-phase execution pipelines."""

    name = "orchestrate_complex_goal"
    description = (
        "Decomposes massive or multi-phase directives into a structured pipeline. "
        "Tracks milestones (Discovery -> Architecture -> Execution -> Verification -> Delivery)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "description": "High-level complex directive to orchestrate."
            },
            "custom_milestones": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional custom list of milestone names."
            }
        },
        "required": ["goal"]
    }

    def execute(
        self,
        goal: str,
        custom_milestones: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        orchestrator = SuperpowerOrchestrator()
        pipeline = orchestrator.plan_workflow(goal, custom_milestones)
        report = orchestrator.generate_pipeline_report(pipeline["pipeline_id"])
        return {
            "success": True,
            "pipeline": pipeline,
            "report": report
        }


class CodeStudioBuilderTool(BaseTool):
    """Scaffolds complete multi-file projects with automated syntax verification and sandbox execution."""

    name = "code_studio_builder"
    description = (
        "Builds complete multi-file projects, websites, or apps in 1 step. "
        "Performs automated syntax checking (Python/AST) and optional test execution."
    )
    parameters = {
        "type": "object",
        "properties": {
            "project_dir": {
                "type": "string",
                "description": "Destination directory for the project (e.g. 'Desktop/my_app')."
            },
            "files": {
                "type": "object",
                "description": "Dictionary mapping relative file paths to their string content."
            },
            "run_entrypoint": {
                "type": "string",
                "description": "Optional entrypoint file to execute and verify (e.g. 'main.py')."
            }
        },
        "required": ["project_dir", "files"]
    }

    def execute(
        self,
        project_dir: str,
        files: Dict[str, str],
        run_entrypoint: Optional[str] = None
    ) -> Dict[str, Any]:
        return SuperpowerCodeStudio.create_project(
            project_dir=project_dir,
            files=files,
            run_entrypoint=run_entrypoint
        )


class SystemSuperOptimizerTool(BaseTool):
    """Collects deep performance telemetry, tests network latency, and scans for recoverable disk space."""

    name = "system_super_optimizer"
    description = (
        "Performs comprehensive PC diagnostics, memory bottleneck evaluation, "
        "network latency testing to global gateways, and junk file scanning."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["snapshot", "latency", "scan_junk", "all"],
                "default": "all",
                "description": "Diagnostic action: 'snapshot' (CPU/RAM/Disks), 'latency' (Ping tests), 'scan_junk' (Disk cache), 'all'."
            },
            "target_dir": {
                "type": "string",
                "default": ".",
                "description": "Directory to scan for junk files."
            }
        },
        "required": []
    }

    def execute(
        self,
        action: str = "all",
        target_dir: str = "."
    ) -> Dict[str, Any]:
        results = {}
        if action in ["snapshot", "all"]:
            results["performance"] = SuperpowerSystemOptimizer.get_performance_snapshot()
        if action in ["latency", "all"]:
            results["latency"] = SuperpowerSystemOptimizer.test_latency()
        if action in ["scan_junk", "all"]:
            results["junk_scan"] = SuperpowerSystemOptimizer.scan_temporary_files(target_dir)

        return {
            "success": True,
            "diagnostics": results
        }
