import json
import sys
from pathlib import Path
from typing import Union

import json5
import yaml

from doc_inject.config import InjectConfig

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_config_file(path: Union[str, Path]) -> InjectConfig:
    """
    Load and validate an InjectConfig from a structured file (json, yaml, toml).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    ext = path.suffix.lower()
    content = path.read_text(encoding="utf-8")

    if ext == ".json":
        data = json.loads(content)
    elif ext == ".json5":
        data = json5.loads(content)
    elif ext in {".yaml", ".yml"}:
        data = yaml.safe_load(content)
    elif ext == ".toml":
        data = tomllib.loads(content)
    else:
        raise ValueError(f"Unsupported config file type: {ext}")

    try:
        return InjectConfig.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid config structure in {path}: {e}")
