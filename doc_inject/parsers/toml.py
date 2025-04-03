import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def parse_toml(path: Path, query: str) -> Any:
    """
    Load TOML from a file and resolve a dotted key path.
    """
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return _resolve_dotted_path(data, query)


def _resolve_dotted_path(data: Any, path: str) -> Any:
    parts = path.split(".")
    for key in parts:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            raise ValueError(f"Key '{key}' not found while traversing: {path}")
    return data
