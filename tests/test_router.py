from research_agent.core.config import load_llm_profiles
from research_agent.llm.base import FakeLLMClient
from research_agent.llm.router import LLMRouter


def test_router_returns_fake_client():
    config = load_llm_profiles("configs/llm_profiles.yaml")
    router = LLMRouter(config, fake=True)
    assert isinstance(router.client_for("planner"), FakeLLMClient)
