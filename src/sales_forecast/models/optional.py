from __future__ import annotations

from importlib import import_module
from types import ModuleType


def import_optional_dependency(module_name: str, model_name: str, extra_name: str) -> ModuleType:
    try:
        return import_module(module_name)
    except ImportError as exc:
        raise ValueError(
            f"Model '{model_name}' requires optional dependency '{module_name}'. "
            f'Install it with: pip install -e ".[{extra_name}]"'
        ) from exc
