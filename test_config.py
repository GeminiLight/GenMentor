"""Tiny tester to validate Hydra/OmegaConf configuration wiring.

This composes the app config from the project's `config/` directory and
prints key fields. It also demonstrates environment variable overrides.
"""

from __future__ import annotations

import os
from typing import Dict

from hydra import initialize, compose
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf


def compose_cfg(env_overrides: Dict[str, str] | None = None):
    """Compose Hydra config from config/ directory with optional env overrides."""

    if env_overrides:
        os.environ.update(env_overrides)

    # Allow re-initialization within the same process when composing multiple times
    if GlobalHydra().is_initialized():
        GlobalHydra().clear()

    with initialize(version_base=None, config_path="config"):
        cfg = compose(config_name="ppo_trainer")
        return cfg


def show_summary(cfg) -> None:
    print("=== Effective Config (summary) ===")
    print(f"environment: {cfg.environment}")
    print(f"log_level:  {cfg.log_level}")
    print("llm:")
    print(f"  provider:   {cfg.llm.provider}")
    print(f"  model_name: {cfg.llm.model_name}")
    print("search:")
    print(f"  provider:   {cfg.search.provider}")
    print(f"  max_results:{cfg.search.max_results}")
    print("server:")
    print(f"  host:       {cfg.server.host}")
    print(f"  port:       {cfg.server.port}")


def main() -> None:
    print("\n--- Compose defaults (no env overrides) ---")
    cfg = compose_cfg()
    show_summary(cfg)

    print("\n--- Compose with env overrides ---")
    overrides = {
        "GENMENTOR_LLM__MODEL_NAME": "test-model",
        "GENMENTOR_SEARCH__PROVIDER": "duckduckgo",
        "GENMENTOR_SERVER_PORT": "8180",
    }
    cfg2 = compose_cfg(overrides)
    show_summary(cfg2)

    # Print full YAML at the end for inspection
    print("\n=== Full YAML (effective) ===")
    print(OmegaConf.to_yaml(cfg2))


if __name__ == "__main__":
    main()