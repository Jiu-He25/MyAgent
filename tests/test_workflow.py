from pathlib import Path

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


def test_workflow_fake_llm_smoke():
    base_dir = Path.cwd()
    task = load_task_config("configs/tasks/activation_function.yaml")
    execution = load_execution_config("configs/execution_local.yaml").execution
    safety = SafetyPolicy(load_safety_config("configs/safety.yaml").safety, base_dir=base_dir)
    executor = LocalExecutor(execution, safety, base_dir=base_dir)
    workflow = ResearchWorkflow(
        task_config=task,
        execution_config=execution,
        llm_router=LLMRouter(load_llm_profiles("configs/llm_profiles.yaml"), fake=True),
        executor=executor,
        base_dir=base_dir,
        auto_approve=True,
    )
    state = workflow.run()
    assert state.status == "completed"
    assert Path(state.report_path).exists()
    assert state.experiments
