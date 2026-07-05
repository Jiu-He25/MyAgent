# Research Agent

Local-first research automation MVP for small machine-learning experiments.

Stage 1 focuses on:

- CLI orchestration only, no web UI and no desktop UI.
- OpenAI-compatible LLM profiles configured by YAML.
- Local command execution through a safety policy.
- Run artifacts under `workspace/runs/<run_id>/`.
- Testable agent workflow using `FakeLLMClient`.

The stage-1 implementation follows the prompt in
`research_agent_codex_prompts/01_stage_core_cli_local.txt`.

## Quick Start

Prerequisites:

- Python 3.11+
- macOS/Linux shell or Windows PowerShell
- Optional: `RESEARCH_AGENT_LLM_API_KEY` for real OpenAI-compatible LLM calls

Create and use the project-local Python environment.

macOS/Linux:

```bash
chmod +x scripts/*.sh
./scripts/setup_env.sh
```

If your default `python3` is older than 3.11, install Python 3.11+ and run:

```bash
PYTHON_BOOTSTRAP=/path/to/python3.11 ./scripts/setup_env.sh
```

Windows PowerShell:

```powershell
.\scripts\setup_env.ps1
```

The setup scripts install dependencies from `requirements.txt` and then install
this project in editable mode.

Run tests with the project-local interpreter:

macOS/Linux:

```bash
./scripts/run_tests.sh
```

Windows PowerShell:

```powershell
.\scripts\run_tests.ps1
```

Run the fake-LLM smoke workflow. This does not require an API key and is the
recommended first check.

macOS/Linux:

```bash
./scripts/run_cli.sh run \
  --task-config configs/tasks/activation_function.yaml \
  --llm-config configs/llm_profiles.yaml \
  --execution-config configs/execution_local.yaml \
  --safety-config configs/safety.yaml \
  --fake-llm \
  --auto-approve
```

Windows PowerShell:

```powershell
.\scripts\run_cli.ps1 run `
  --task-config configs/tasks/activation_function.yaml `
  --llm-config configs/llm_profiles.yaml `
  --execution-config configs/execution_local.yaml `
  --safety-config configs/safety.yaml `
  --fake-llm `
  --auto-approve
```

For real LLM calls, set `RESEARCH_AGENT_LLM_API_KEY` in your environment and
omit `--fake-llm`.

macOS/Linux:

```bash
export RESEARCH_AGENT_LLM_API_KEY="..."
./scripts/run_cli.sh run --auto-approve
```

Windows PowerShell:

```powershell
$env:RESEARCH_AGENT_LLM_API_KEY="..."
.\scripts\run_cli.ps1 run --auto-approve
```

All logs, state snapshots, artifacts, and reports are written under `workspace/runs/<run_id>/`.

## CLI Usage

The script wrappers call the same Python module:

```bash
python -m apps.cli.main run --help
```

Important options:

- `--task-config`: task definition, default `configs/tasks/activation_function.yaml`
- `--llm-config`: LLM profile definitions, default `configs/llm_profiles.yaml`
- `--execution-config`: local execution settings, default `configs/execution_local.yaml`
- `--safety-config`: allowed paths, blocked commands, and runtime budgets
- `--fake-llm`: use deterministic test responses instead of calling an API
- `--auto-approve`: skip the interactive plan confirmation

The default safety policy only allows file and command effects under
`./workspace`. Put experiment repositories under `workspace/repos/`.

## Task Configuration

Create one YAML file per task under `configs/tasks/`, for example
`configs/tasks/my_activation.yaml`.

The main field that tells the agent where the target experiment project lives is
`project.repo_path`:

```yaml
task:
  name: my_activation_test
  type: ml_ablation
idea: |
  Compare my new activation function with ReLU, GELU, and SiLU.
project:
  repo_path: ./workspace/repos/my-activation-exp
  entrypoint: train.py
experiment:
  dataset: CIFAR10
  model: small_cnn
  baselines: [relu, gelu, silu]
  new_method:
    name: my_activation
    formula: "x * sigmoid(1.5*x) + 0.1 * tanh(x)"
  seeds: [0, 1, 2]
  metrics:
    primary: val_accuracy
    secondary: [train_loss, val_loss, training_time]
decision:
  min_improvement: 0.005
  max_training_time_increase: 0.2
  min_completed_seeds: 3
```

`project.repo_path` can point to an existing local repo or an empty directory the
agent can populate. By default it should stay under `./workspace`, because
`configs/safety.yaml` only allows file and command effects there.

Run a specific task with:

```bash
./scripts/run_cli.sh run --task-config configs/tasks/my_activation.yaml --fake-llm --auto-approve
```

For real model calls, remove `--fake-llm` and set `RESEARCH_AGENT_LLM_API_KEY`.

## Current Capabilities

This repository currently implements the stage-1 local CLI MVP:

- Load task, LLM, execution, and safety YAML configs.
- Create an isolated run directory under `workspace/runs/<run_id>/`.
- Generate a plan with `PlannerAgent`.
- Optionally ask for plan approval, or skip it with `--auto-approve`.
- Generate or modify files in the configured experiment repo with `CoderAgent`.
- Execute planned local shell commands through `LocalExecutor` and `SafetyPolicy`.
- Analyze results, review the outcome, and write a Markdown report.
- Run fully offline smoke tests with `--fake-llm`.

Not implemented yet: SSH execution, persistent database storage, checkpoint
resume, and desktop UI.

## Model Configuration

The code is not tied to Kimi. It currently supports any chat-completions API
compatible with the OpenAI SDK. Configure models in `configs/llm_profiles.yaml`:

```yaml
llm_profiles:
  planner:
    provider: openai_compatible
    model: your-model-name
    base_url: https://your-provider.example/v1
    api_key_env: RESEARCH_AGENT_LLM_API_KEY
    temperature: 0.2
    max_tokens: 4096
```

You can use the same API key environment variable for every profile, or point
different profiles at different variables and providers.

## Troubleshooting

If setup reports that the existing `.venv` uses Python older than 3.11, remove
the old local environment and create it again with Python 3.11+:

```bash
rm -rf .venv
./scripts/setup_env.sh
```
