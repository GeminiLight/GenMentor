from typing import Any

# Adopt the simplified BaseAgent implementation project-wide by re-exporting
# a compatible Agent symbol that existing modules import.
from .base_agent import BaseAgent as Agent

__all__ = ["Agent"]