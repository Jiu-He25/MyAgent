"""LLM client interfaces and test doubles."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from research_agent.core.schemas import LLMMessage


class LLMClient(ABC):
    @abstractmethod
    def complete(self, messages: list[LLMMessage], *, response_format: str = "text") -> str:
        """Return an LLM completion."""


class FakeLLMClient(LLMClient):
    def __init__(self, profile_name: str = "fake") -> None:
        self.profile_name = profile_name

    def complete(self, messages: list[LLMMessage], *, response_format: str = "text") -> str:
        prompt = "\n".join(message.content for message in messages).lower()
        if self.profile_name == "planner" or "planner" in prompt:
            return json.dumps(
                {
                    "summary": "Run a small local activation comparison.",
                    "experiments": [
                        {
                            "method": "relu",
                            "seed": 0,
                            "command": "python train.py --method relu --seed 0",
                        },
                        {
                            "method": "my_activation",
                            "seed": 0,
                            "command": "python train.py --method my_activation --seed 0",
                        },
                    ],
                }
            )
        if self.profile_name == "coder":
            return json.dumps(
                {
                    "summary": "Create a deterministic toy training script if missing.",
                    "files": [
                        {
                            "path": "train.py",
                            "content": (
                                "import argparse, json, time\n"
                                "p=argparse.ArgumentParser(); p.add_argument('--method'); "
                                "p.add_argument('--seed', type=int, default=0); a=p.parse_args()\n"
                                "scores={'relu':0.812,'gelu':0.819,'silu':0.821,"
                                "'my_activation':0.827}\n"
                                "metrics={'val_accuracy':scores.get(a.method,0.8)+a.seed*0.0001,"
                                "'train_loss':0.41,'val_loss':0.37,'training_time':1.0}\n"
                                "print('val_accuracy=' + str(metrics['val_accuracy']))\n"
                                "open('metrics.json','w',encoding='utf-8').write(json.dumps(metrics))\n"
                            ),
                        }
                    ],
                }
            )
        if self.profile_name == "analyzer":
            return json.dumps({"summary": "The new method is ahead in the toy run.", "best_method": "my_activation"})
        if self.profile_name == "reviewer":
            return json.dumps({"decision": "promising", "reason": "Primary metric improved in the smoke run."})
        if self.profile_name == "reporter":
            return "# Experiment Report\n\nThe local research workflow completed successfully.\n"
        return "OK"
