from pathlib import Path

from research_agent.core.config import load_execution_config, load_safety_config
from research_agent.executors.local_executor import LocalExecutor
from research_agent.safety.permission import SafetyPolicy


def test_local_executor_runs_command():
    base_dir = Path.cwd()
    execution = load_execution_config("configs/execution_local.yaml").execution
    safety = SafetyPolicy(load_safety_config("configs/safety.yaml").safety, base_dir=base_dir)
    executor = LocalExecutor(execution, safety, base_dir=base_dir)
    executor.repo_path.mkdir(parents=True, exist_ok=True)
    result = executor.run("python -c \"print('ok')\"", timeout_seconds=5)
    assert result.exit_code == 0
    assert "ok" in result.stdout
