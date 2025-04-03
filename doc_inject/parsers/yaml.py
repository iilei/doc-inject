from pathlib import Path
from typing import Any

import yaml


def parse_yaml(path: Path, query: str) -> Any:
    """
    Load YAML from a file and resolve a dotted key path.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _resolve_dotted_path(data, query)


def _resolve_dotted_path(data: Any, path: str) -> Any:
    parts = path.split(".")
    for key in parts:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            raise ValueError(f"Key '{key}' not found while traversing: {path}")
    return data
