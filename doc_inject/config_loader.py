import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Optional

import json5
import yaml

from doc_inject.config import InjectConfig

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


COMMENT_SYNTAX = {
    "json": ("//", "//"),
    "json5": ("//", "//"),
    "yaml": ("#", "#"),
    "yml": ("#", "#"),
    "toml": ("#", "#"),
    "md": ("<!--", "-->"),
    "html": ("<!--", "-->"),
    "jinja2": ("{#", "#}"),
    "j2": ("{#", "#}"),
    "py": ("#", "#"),
    "ini": (";", ";"),
}


def extract_config_from_document(path: Path) -> InjectConfig:
    ext_chain = _get_extension_chain(path)
    content = path.read_text(encoding="utf-8")

    for ext in ext_chain:
        if ext not in COMMENT_SYNTAX:
            continue

        prefix, suffix = COMMENT_SYNTAX[ext]
        block = _extract_comment_block(content, prefix, suffix)

        if block:
            try:
                config_data = _parse_structured_config(block)
                return InjectConfig.model_validate(config_data)
            except Exception as e:
                raise ValueError(f"Config block found but failed to parse: {e}")

    raise ValueError(f"No usable config block found in {path}")


def extract_config_from_file(path: Path, query: str | None = None) -> InjectConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    content = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()

    try:
        if ext == ".json":
            data = json.loads(content)
        elif ext == ".json5":
            data = json5.loads(content)
        elif ext in {".yaml", ".yml"}:
            data = yaml.safe_load(content)
        elif ext == ".toml":
            data = tomllib.loads(content)
        else:
            raise ValueError(f"Unsupported config file format: {ext}")
    except Exception as e:
        raise ValueError(f"Failed to parse config file '{path}': {e}")

    # Optional query
    if query:
        for key in query.split("."):
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                raise ValueError(f"Invalid config query: '{query}' (missing key '{key}')")

    return InjectConfig.model_validate(data)


def _get_extension_chain(path: Path) -> list[str]:
    return list(reversed(path.name.split(".")[1:])) or ["html", "json"]


def _extract_comment_block(text: str, prefix: str, suffix: str) -> Optional[str]:
    if prefix == suffix and prefix in {"#", "//", ";"}:
        directive_pattern = re.compile(
            rf"^{re.escape(prefix)}\s+doc-inject:configure\b", re.IGNORECASE
        )

        lines = text.splitlines()
        block_lines = []
        found = False

        for line in lines:
            stripped = line.lstrip()
            if directive_pattern.match(stripped):
                found = True
                continue

            if found:
                if stripped.startswith(prefix):
                    # Strip only the first comment prefix and preserve indentation
                    idx = line.index(prefix)
                    after_prefix = line[idx + len(prefix) :]
                    block_lines.append(after_prefix.rstrip("\n"))
                else:
                    break

        if block_lines:
            return textwrap.dedent("\n".join(block_lines))

        return None

    # Block-style comments (<!-- -->, {# #}, etc.)
    pattern = re.compile(
        rf"{re.escape(prefix)}\s*doc-inject:configure\s*(.*?)\s*{re.escape(suffix)}",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _parse_structured_config(config_str: str) -> dict:
    try:
        return yaml.safe_load(config_str)
    except Exception:
        pass
    try:
        return json5.loads(config_str)
    except Exception:
        raise ValueError("Unable to parse config block as YAML or JSON5.")
