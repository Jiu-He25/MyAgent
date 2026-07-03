"""Project-specific exceptions."""


class ResearchAgentError(Exception):
    """Base exception for recoverable Research Agent errors."""


class ConfigError(ResearchAgentError):
    """Raised when configuration is missing or invalid."""


class LLMError(ResearchAgentError):
    """Raised when an LLM request cannot be completed."""


class SafetyError(ResearchAgentError):
    """Raised when a path, command, or budget violates safety policy."""


class ExecutionError(ResearchAgentError):
    """Raised when command execution fails unexpectedly."""


class WorkflowError(ResearchAgentError):
    """Raised when the workflow cannot advance safely."""
