"""Helper-AI Reverse Engineering & App Memory Suite.

Integrates REA (Reverse Engineer Anything) with persistent AppMemoryStore,
deep application dissection, and 100% accurate fast-path automation.
"""

from core.reverse_engineering.rea_bridge import REABridge
from core.reverse_engineering.app_memory_store import AppMemoryStore
from core.reverse_engineering.app_analyzer import ReverseEngineeringEngine
from core.reverse_engineering.fast_operator import FastAppOperator

__all__ = [
    "REABridge",
    "AppMemoryStore",
    "ReverseEngineeringEngine",
    "FastAppOperator"
]
