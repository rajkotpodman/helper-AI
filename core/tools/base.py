"""Base Tool definition for Helper-AI"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Abstract base class for all agent tools."""
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executes the tool with the given arguments.
        Returns a dictionary with:
            - success: bool
            - output: str
            - error: str (optional)
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Returns the JSON schema representation of this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
