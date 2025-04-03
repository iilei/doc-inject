import json
from pathlib import Path
from typing import Any

import json5
from jsonpath_ng import parse as jp_parse


def parse_json(path: Path, query: str) -> Any:
    """
    Load JSON or JSON5 from file and apply a JSONPath query.
    """
    content = path.read_text(encoding="utf-8")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        try:
            data = json5.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse {path} as JSON or JSON5: {e}")

    matches = jp_parse(query).find(data)

    if not matches:
        raise ValueError(f"No match found for JSONPath query: {query}")

    if len(matches) == 1:
        return matches[0].value

    return [match.value for match in matches]
