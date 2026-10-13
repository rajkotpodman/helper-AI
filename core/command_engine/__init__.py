"""Universal Command Engine Package for Helper-AI.

Cross-platform terminal command execution, OS introspection,
encyclopedic command synthesis, and community cheatsheet downloading.
"""

from core.command_engine.os_detector import OSDetector
from core.command_engine.command_encyclopedia import CommandEncyclopedia
from core.command_engine.command_fetcher import CommandFetcher
from core.command_engine.executor import UniversalCommandExecutor

__all__ = [
    "OSDetector",
    "CommandEncyclopedia",
    "CommandFetcher",
    "UniversalCommandExecutor"
]
