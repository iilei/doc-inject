import json
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from jsonpath_ng import parse as jp_parse

from doc_inject.config import InjectItem
from doc_inject.parsers.json import parse_json
from doc_inject.parsers.text import parse_text
from doc_inject.parsers.toml import parse_toml
from doc_inject.parsers.yaml import parse_yaml

# Use tomllib if available (Python 3.11+), fallback to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def resolve_query(item: InjectItem) -> Dict[str, Any]:
    if item.vars:
        return {name: _query(item.file, q, parser=item.parser) for name, q in item.vars.items()}

    elif item.query:
        if item.parser == "text":
            return parse_text(item.file, item.query)

        return {"value": _query(item.file, item.query, parser=item.parser)}

    else:
        raise ValueError("No query or vars defined")


def _load_file(path: Path, parser: str):
    content = path.read_text(encoding="utf-8")

    if parser == "json":
        return json.loads(content)

    elif parser == "yaml":
        return yaml.safe_load(content)

    elif parser == "toml":
        return tomllib.loads(content)

    elif parser == "text":
        return None

    raise ValueError(f"Unsupported parser: {parser}")


def _query(path: Path, expression: str, parser: str) -> Any:
    if parser == "json":
        return parse_json(path, expression)
    elif parser == "yaml":
        return parse_yaml(path, expression)
    elif parser == "toml":
        return parse_toml(path, expression)
    else:
        raise ValueError(f"Unsupported parser: {parser}")


def _jsonpath_query(data: Any, expr: str) -> Any:
    matches = jp_parse(expr).find(data)
    if not matches:
        raise ValueError(f"No match found for JSONPath query: {expr}")
    if len(matches) == 1:
        return matches[0].value
    return [match.value for match in matches]


def _dotted_path_query(data: Any, path: str) -> Any:
    parts = path.split(".")
    for key in parts:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            raise ValueError(f"Key '{key}' not found while traversing: {path}")
    return data
