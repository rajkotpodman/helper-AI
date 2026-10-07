import sys
import os
import asyncio
import argparse

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

load_dotenv()

from core.agent import HelperAgent
from core.llm import LLMClient
from core.tools import ToolRegistry

console = Console()

def print_banner():
    banner_text = Text()
    banner_text.append("⚡ Helper-AI: Autonomous PC & Internet Agent\n", style="bold cyan")
    banner_text.append("Full control of running PC • Internet Search & Fetch • Runs until Goal is Complete\n", style="dim")
    banner_text.append("Non-technical friendly • Automatic Self-Healing", style="italic green")
    console.print(Panel(banner_text, border_style="cyan"))

async def run_cli(goal: str, provider: str = None, safe_mode: bool = False, max_steps: int = 25):
    print_banner()

    llm = LLMClient(provider=provider)
    agent = HelperAgent(llm_client=llm, safe_mode=safe_mode, max_steps=max_steps)

    console.print(f"\n[bold yellow]🎯 Active Goal:[/bold yellow] [bold white]{goal}[/bold white]")
    console.print(f"[dim]Provider: {llm.provider.upper()} | Model: {llm.model} | Safe Mode: {safe_mode}[/dim]\n")

    def handle_event(event_type: str, data: dict):
        if event_type == "thought":
            step = data.get("step")
            thought = data.get("thought")
            action = data.get("action")
            console.print(f"\n[bold magenta]─── Step {step} ───[/bold magenta]")
            console.print(f"[bold cyan]💭 Thought:[/bold cyan] {thought}")
            if action != "none":
                console.print(f"[bold blue]⚡ Action:[/bold blue] [green]{action}[/green] {data.get('action_args', {})}")
        elif event_type == "action_result":
            status_style = "green" if data.get("success") else "red"
            status_symbol = "✔" if data.get("success") else "✖"
            output = data.get("output", "")
            snippet = output if len(output) < 800 else output[:800] + f"\n... [Truncated {len(output)-800} chars]"
            console.print(Panel(
                snippet,
                title=f"[{status_style}]{status_symbol} Result: {data.get('action')}[/{status_style}]",
                border_style=status_style,
                expand=False
            ))
        elif event_type == "completed":
            msg = data.get("message")
            console.print(Panel(
                f"[bold green]🎉 MISSION ACCOMPLISHED![/bold green]\n\n{msg}",
                title="Goal Complete",
                border_style="green"
            ))

    result = await agent.run(goal, on_event=handle_event)
    return result

def main():
    parser = argparse.ArgumentParser(description="Helper-AI Autonomous PC & Internet Agent")
    parser.add_argument("goal", nargs="?", default="", help="Goal to accomplish (e.g. 'clean up downloads')")
    parser.add_argument("--provider", default=None, help="LLM provider: gemini, openai, groq, ollama, rule_engine")
    parser.add_argument("--safe", action="store_true", help="Enable Safe Mode to restrict destructive commands")
    parser.add_argument("--steps", type=int, default=25, help="Maximum execution steps")

    args = parser.parse_args()
    goal = args.goal.strip()

    if not goal:
        print_banner()
        console.print("[bold yellow]What goal would you like Helper to achieve?[/bold yellow]")
        goal = console.input("[bold cyan]> [/bold cyan]").strip()

    if not goal:
        console.print("[red]No goal provided. Exiting.[/red]")
        sys.exit(0)

    try:
        asyncio.run(run_cli(goal, provider=args.provider, safe_mode=args.safe, max_steps=args.steps))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting gracefully.[/yellow]")

if __name__ == "__main__":
    main()
