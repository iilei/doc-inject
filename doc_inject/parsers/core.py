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
    result = []

    if item.vars:
        result.extend(
            [
                _query(item._resolved_files, q, parser=item.parser, assign_to=name)
                for name, q in item.vars.items()
            ]
        )

    elif item.query:
        if item.parser == "text":
            result.append([parse_text(file, item.query) for file in item._resolved_files])

        else:
            result.append(
                _query(item._resolved_files, item.query, parser=item.parser, assign_to="value")
            )
            if item.glob:
                return {"value": [y.get("value", {}) for x in result for y in x]}

    # if it is a glob-style data-gathering, return a list of imploded results.
    # if it is a file-style data-gathering, boil the list down to a single dictionary
    imploded = [{k: v for flat in x for k, v in flat.items()} for x in result]
    return imploded if item.glob else {k: v for flat in imploded for k, v in flat.items()}


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


def _query(paths: list[Path], expression: str, parser: str, assign_to: str = "value") -> Any:
    result = []
    if parser == "json":
        result = [parse_json(path, expression) for path in paths]
    elif parser == "yaml":
        result = [parse_yaml(path, expression) for path in paths]
    elif parser == "toml":
        result = [parse_toml(path, expression) for path in paths]
    else:
        raise ValueError(f"Unsupported parser: {parser}")

    return [{assign_to: x} for x in result]


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
