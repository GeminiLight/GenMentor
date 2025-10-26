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
from config.loader import load_config, config


print("=== Testing Config Loading ===")
print(config)