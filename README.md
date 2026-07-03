# Research Agent

Local-first research automation MVP for small machine-learning experiments.

Stage 1 focuses on:

- CLI orchestration only, no web UI and no desktop UI.
- OpenAI-compatible LLM profiles, with Kimi/Moonshot defaults.
- Local command execution through a safety policy.
- Run artifacts under `workspace/runs/<run_id>/`.
- Testable agent workflow using `FakeLLMClient`.

## Quick Start

```powershell
python -m apps.cli.main run `
  --task-config configs/tasks/activation_function.yaml `
  --llm-config configs/llm_profiles.yaml `
  --execution-config configs/execution_local.yaml `
  --safety-config configs/safety.yaml `
  --fake-llm `
  --auto-approve
```

For real LLM calls, set `KIMI_API_KEY` in your environment and omit `--fake-llm`.

```powershell
$env:KIMI_API_KEY="..."
python -m apps.cli.main run --auto-approve
```

All logs, state snapshots, artifacts, and reports are written under `workspace/runs/<run_id>/`.