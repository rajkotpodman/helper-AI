"""Background AI Swarm & Advisory Tool for Helper-AI.

Allows the agent to consult ANY AI provider in the background for:
- Complex problem deconstruction & planning
- Error diagnosis & self-healing
- Fast code/script synthesis
- Second opinions & multi-AI consensus
"""

from typing import Dict, Any, Optional, List
from core.tools.base import BaseTool
from core.background_ai_swarm import background_ai_swarm


class ConsultBackgroundAITool(BaseTool):
    """Universal Background AI Advisory & Swarm Tool."""
    name = "consult_background_ai"
    description = (
        "Consults ANY AI model (Groq, Gemini, DeepSeek, OpenAI, Ollama, Claude/Custom) "
        "dynamically in the background for advisory help, code generation, debugging, "
        "or multi-AI swarm consensus without blocking main execution."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The exact question, problem, code task, or error trace to consult the background AI about."
            },
            "provider": {
                "type": "string",
                "description": "Target AI provider to consult: 'auto' (fastest available), 'groq' (ultra-fast 500 T/s), 'gemini', 'deepseek', 'openai', 'ollama', 'custom', or 'swarm' (parallel multi-AI consensus).",
                "enum": ["auto", "groq", "gemini", "deepseek", "openai", "ollama", "custom", "swarm"]
            },
            "role": {
                "type": "string",
                "description": "Specialized role for background AI: 'advisor' (general advice), 'debugger' (diagnose errors & fix commands), 'coder' (write scripts), 'planner' (breakdown steps), 'critic' (audit accuracy).",
                "enum": ["advisor", "debugger", "coder", "planner", "critic"]
            },
            "context": {
                "type": "string",
                "description": "Optional context such as current execution history, directory contents, or terminal output."
            }
        },
        "required": ["query"]
    }

    def execute(
        self,
        query: str,
        provider: str = "auto",
        role: str = "advisor",
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        prov_clean = (provider or "auto").lower().strip()

        if prov_clean == "swarm":
            res = background_ai_swarm.consult_swarm(query=query, role=role)
            if res.get("success"):
                content = res.get("consensus_text") or res.get("content", "")
                return {
                    "success": True,
                    "output": f"Multi-AI Swarm Consensus ({res.get('participants_count', 1)} models, {res.get('latency_ms')}ms):\n{content}",
                    "details": res
                }
            return {
                "success": False,
                "output": f"Background AI Swarm error: {res.get('error')}",
                "details": res
            }

        res = background_ai_swarm.consult(
            query=query,
            provider=prov_clean,
            role=role,
            context=context
        )

        if res.get("success"):
            return {
                "success": True,
                "output": f"Background AI ({res.get('provider').upper()}, {res.get('latency_ms')}ms):\n{res.get('content')}",
                "provider": res.get("provider"),
                "model": res.get("model"),
                "latency_ms": res.get("latency_ms"),
                "details": res
            }
        else:
            return {
                "success": False,
                "output": f"Background AI consultation failed: {res.get('error')}",
                "details": res
            }
