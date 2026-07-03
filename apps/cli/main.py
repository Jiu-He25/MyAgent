"""Research Agent CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from research_agent.core.config import (
    load_execution_config,
    load_llm_profiles,
    load_safety_config,
    load_task_config,
)
from research_agent.executors.local_executor import LocalExecutor
from research_agent.llm.router import LLMRouter
from research_agent.safety.permission import SafetyPolicy
from research_agent.workflows.research_loop import ResearchWorkflow

app = typer.Typer(help="Local-first Research Agent MVP")
console = Console()


@app.callback()
def main() -> None:
    """Research Agent command group."""


@app.command()
def run(
    task_config: Path = typer.Option(Path("configs/tasks/activation_function.yaml"), help="Task YAML path"),
    llm_config: Path = typer.Option(Path("configs/llm_profiles.yaml"), help="LLM profiles YAML path"),
    execution_config: Path = typer.Option(Path("configs/execution_local.yaml"), help="Execution YAML path"),
    safety_config: Path = typer.Option(Path("configs/safety.yaml"), help="Safety YAML path"),
    fake_llm: bool = typer.Option(False, help="Use deterministic fake LLM responses"),
    auto_approve: bool = typer.Option(False, help="Approve the generated plan without prompting"),
) -> None:
    load_dotenv()
    base_dir = Path.cwd()
    task = load_task_config(task_config)
    llms = load_llm_profiles(llm_config)
    execution = load_execution_config(execution_config).execution
    safety = load_safety_config(safety_config).safety
    policy = SafetyPolicy(safety, base_dir=base_dir)
    executor = LocalExecutor(execution, policy, base_dir=base_dir)
    router = LLMRouter(llms, fake=fake_llm)

    def approve(_plan: dict, markdown: str) -> bool:
        console.print(Markdown(markdown))
        return typer.confirm("Continue with this plan?", default=False)

    workflow = ResearchWorkflow(
        task_config=task,
        execution_config=execution,
        llm_router=router,
        executor=executor,
        base_dir=base_dir,
        auto_approve=auto_approve,
        approval_callback=approve,
    )
    state = workflow.run()
    console.print(f"[bold]Status:[/bold] {state.status}")
    console.print(f"[bold]Run:[/bold] {state.run_dir}")
    if state.report_path:
        console.print(f"[bold]Report:[/bold] {state.report_path}")


if __name__ == "__main__":
    app()
