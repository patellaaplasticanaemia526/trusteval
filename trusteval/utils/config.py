# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Configuration management for TrustEval.

Reads settings from environment variables (prefixed ``TRUSTEVAL_``),
a YAML file at ``~/.trusteval/config.yaml``, and explicit overrides.
Uses Pydantic Settings for validation and type coercion.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
    _HAS_PYDANTIC = True
except ImportError:
    try:
        from pydantic import BaseSettings, Field  # type: ignore[assignment]
        _HAS_PYDANTIC = True
    except ImportError:
        _HAS_PYDANTIC = False

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------

_CONFIG_DIR = Path.home() / ".trusteval"
_CONFIG_FILE = _CONFIG_DIR / "config.yaml"

# ---------------------------------------------------------------------------
# YAML loader helper
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict.

    Args:
        path: Filesystem path to the YAML configuration file.

    Returns:
        Parsed dict, or empty dict if the file does not exist or
        PyYAML is not installed.
    """
    if not _HAS_YAML or not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# Config model
# ---------------------------------------------------------------------------

if _HAS_PYDANTIC:

    class TrustEvalConfig(BaseSettings):
        """Centralised configuration for the TrustEval SDK.

        Values are resolved with the following precedence (highest first):

        1. Explicit keyword arguments passed to the constructor.
        2. Environment variables prefixed with ``TRUSTEVAL_``.
        3. Values from ``~/.trusteval/config.yaml``.
        4. Built-in defaults defined on this class.
        """

        # Provider / model
        provider: str = Field(default="openai", description="LLM provider name")
        model: str = Field(default="gpt-4", description="Model identifier")
        api_key: Optional[str] = Field(default=None, description="Provider API key")

        # Evaluation
        industry: str = Field(default="general", description="Target industry")
        pillars: List[str] = Field(
            default=["hallucination", "bias", "pii", "toxicity"],
            description="Evaluation pillars to run",
        )
        pillar_weights: Dict[str, float] = Field(
            default={
                "hallucination": 0.30,
                "bias": 0.25,
                "pii": 0.25,
                "toxicity": 0.20,
            },
            description="Weight per pillar for overall score",
        )

        # Behaviour
        verbose: bool = Field(default=False, description="Enable debug logging")
        parallel: bool = Field(default=True, description="Run pillars in parallel")
        timeout_seconds: int = Field(default=300, description="Per-pillar timeout")
        max_retries: int = Field(default=3, description="Max retries on transient errors")

        # Paths
        config_dir: str = Field(
            default=str(_CONFIG_DIR),
            description="Directory for TrustEval config/data",
        )
        cache_enabled: bool = Field(default=True, description="Enable response caching")

        model_config = {
            "env_prefix": "TRUSTEVAL_",
            "env_nested_delimiter": "__",
            "case_sensitive": False,
            "extra": "ignore",
        }

        @classmethod
        def from_yaml(cls, path: Path | str | None = None, **overrides: Any) -> "TrustEvalConfig":
            """Create a config instance pre-populated from a YAML file.

            Args:
                path: Path to config YAML. Defaults to ``~/.trusteval/config.yaml``.
                **overrides: Additional keyword arguments that take precedence.

            Returns:
                A fully-resolved ``TrustEvalConfig`` instance.
            """
            yaml_path = Path(path) if path else _CONFIG_FILE
            yaml_data = _load_yaml(yaml_path)
            yaml_data.update(overrides)
            return cls(**yaml_data)

else:
    # Lightweight fallback when Pydantic is not installed.

    class TrustEvalConfig:  # type: ignore[no-redef]
        """Minimal configuration container (pydantic-settings not installed)."""

        _DEFAULTS: dict[str, Any] = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": None,
            "industry": "general",
            "pillars": ["hallucination", "bias", "pii", "toxicity"],
            "pillar_weights": {
                "hallucination": 0.30,
                "bias": 0.25,
                "pii": 0.25,
                "toxicity": 0.20,
            },
            "verbose": False,
            "parallel": True,
            "timeout_seconds": 300,
            "max_retries": 3,
            "config_dir": str(_CONFIG_DIR),
            "cache_enabled": True,
        }

        def __init__(self, **kwargs: Any) -> None:
            merged = {**self._DEFAULTS, **kwargs}
            for key, value in merged.items():
                setattr(self, key, value)

        @classmethod
        def from_yaml(cls, path: Path | str | None = None, **overrides: Any) -> "TrustEvalConfig":
            yaml_path = Path(path) if path else _CONFIG_FILE
            yaml_data = _load_yaml(yaml_path)
            yaml_data.update(overrides)
            return cls(**yaml_data)


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def load_config(
    path: Path | str | None = None,
    **overrides: Any,
) -> TrustEvalConfig:
    """Load and return a ``TrustEvalConfig``.

    Args:
        path: Optional path to a YAML config file.
        **overrides: Keyword overrides that take highest precedence.

    Returns:
        Fully-resolved configuration instance.
    """
    return TrustEvalConfig.from_yaml(path=path, **overrides)
