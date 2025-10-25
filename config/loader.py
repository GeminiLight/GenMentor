from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from omegaconf import OmegaConf, DictConfig

from .schemas import AppConfig


CONFIG_DIR = Path(__file__).resolve().parent


def _load_yaml_if_exists(path: Path):
    return OmegaConf.load(path) if path.exists() else OmegaConf.create({})


def load_config(env: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None, *, validate: bool = True) -> DictConfig:
    """Load OmegaConf configuration.

    Precedence: default.yaml < {env}.yaml (if provided) < overrides (dict)
    Environment variables are referenced within YAML via ${env:VAR, default}.

    If validate=True, merges with a structured schema derived from dataclasses
    in config/schemas.py to catch typos and ensure types.
    """
    env = env or OmegaConf.create({}).get("env", None) or None

    base_cfg = _load_yaml_if_exists(CONFIG_DIR / "default.yaml")
    env_cfg = _load_yaml_if_exists(CONFIG_DIR / f"{env}.yaml") if env else OmegaConf.create({})
    merged = OmegaConf.merge(base_cfg, env_cfg)

    if overrides:
        merged = OmegaConf.merge(merged, OmegaConf.create(overrides))

    if validate:
        # Validate by merging with structured schema
        schema = OmegaConf.structured(AppConfig)
        merged = OmegaConf.merge(schema, merged)

    # Resolve interpolations like ${env:VAR}
    OmegaConf.set_readonly(merged, False)
    merged_container = OmegaConf.to_container(merged, resolve=True)
    # Ensure we always return a dictionary-like configuration (DictConfig)
    if not isinstance(merged_container, dict):
        merged_container = {"config": merged_container}
    merged = OmegaConf.create(merged_container)
    OmegaConf.set_readonly(merged, True)
    return merged


def save_effective_config(cfg: DictConfig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        OmegaConf.save(config=cfg, f=f)


if __name__ == "__main__":
    # Example: quick manual check
    cfg = load_config(env="dev")
    print(OmegaConf.to_yaml(cfg))
