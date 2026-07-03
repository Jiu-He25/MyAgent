from pathlib import Path

import pytest

from research_agent.core.config import load_safety_config
from research_agent.core.errors import SafetyError
from research_agent.safety.permission import SafetyPolicy


def test_safety_denies_dangerous_command():
    policy = SafetyPolicy(load_safety_config("configs/safety.yaml").safety, base_dir=Path.cwd())
    with pytest.raises(SafetyError):
        policy.validate_command("sudo reboot", cwd=Path("workspace").resolve(), timeout_seconds=1)


def test_safety_denies_outside_path():
    policy = SafetyPolicy(load_safety_config("configs/safety.yaml").safety, base_dir=Path.cwd())
    with pytest.raises(SafetyError):
        policy.validate_path(Path.cwd().parent)
