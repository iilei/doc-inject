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
    "adoc": ("//", "//"),
    "asciidoc": ("//", "//"),
    "json": ("//", "//"),
    "json5": ("//", "//"),
    "html": ("<!--", "-->"),
    "md": ("<!--", "-->"),
    "ini": (";", ";"),
    "j2": ("{#", "#}"),
    "jinja2": ("{#", "#}"),
    "py": ("#", "#"),
    "toml": ("#", "#"),
    "yaml": ("#", "#"),
    "yml": ("#", "#"),
}


def extract_config_from_document(path: Path) -> InjectConfig:
    ext_chain = _get_extension_chain(path)
    content = path.read_text(encoding="utf-8")

    for ext in ext_chain:
        if ext not in COMMENT_SYNTAX:
            continue

        prefix, suffix = COMMENT_SYNTAX[ext]
        block = _extract_comment_block(content, prefix, suffix, ext)

        if block:
            try:
                config_data = _parse_structured_config(block)
                return InjectConfig.model_validate(config_data)
            except Exception as e:
                print(e)
            except Exception as e:
                raise ValueError(f"Config block found but failed to parse: {e}")

    raise ValueError(f"No usable config block found in {path}")


def extract_config_from_file(path: Path, query: str | None = None) -> InjectConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    content = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()

    if ext == ".toml" and not query:
        query = "tool.doc-inject"

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


def _extract_comment_block(text: str, prefix: str, suffix: str, ext: str) -> Optional[str]:
    lines = text.splitlines()

    if ext in ["asciidoc", "adoc"]:
        # 1. AsciiDoc delimited block comment: ////
        for i, line in enumerate(lines):
            if line.strip() == "////":
                block = []
                for inner in lines[i + 1 :]:
                    if inner.strip() == "////":
                        break
                    block.append(inner)
                if block and "doc-inject:configure" in block[0]:
                    return _dedent_after_directive(block)

        # 2. AsciiDoc [comment] -- -- block
        for i, line in enumerate(lines):
            if line.strip().lower() == "[comment]" and i + 2 < len(lines):
                if lines[i + 1].strip() == "--":
                    block = []
                    for inner in lines[i + 2 :]:
                        if inner.strip() == "--":
                            break
                        block.append(inner)
                    if block and "doc-inject:configure" in block[0]:
                        return _dedent_after_directive(block)

        # 3. AsciiDoc paragraph macro [comment] + contiguous lines
        for i, line in enumerate(lines):
            if line.strip().lower() == "[comment]" and i + 1 < len(lines):
                block = []
                for inner in lines[i + 1 :]:
                    if not inner.strip():
                        break
                    block.append(inner)
                if block and "doc-inject:configure" in block[0]:
                    return _dedent_after_directive(block)

    # 4. Line-comment mode (//, #, etc.)
    if prefix == suffix and prefix in {"#", "//", ";"}:
        directive_pattern = re.compile(
            rf"^{re.escape(prefix)}\s+doc-inject:configure\b", re.IGNORECASE
        )
        block_lines = []
        found = False

        for line in lines:
            stripped = line.lstrip()
            if directive_pattern.match(stripped):
                found = True
                continue
            if found:
                if stripped.startswith(prefix):
                    after_prefix = stripped[len(prefix) :]
                    block_lines.append(after_prefix.rstrip("\n"))
                else:
                    break
        if block_lines:
            return textwrap.dedent("\n".join(block_lines))

    # 5. Block-style (<!-- -->, {# #}, etc.)
    pattern = re.compile(
        rf"{re.escape(prefix)}\s*doc-inject:configure\s*(.*?)\s*{re.escape(suffix)}",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _parse_structured_config(config_str: str) -> dict:
    try:
        loaded = yaml.safe_load(config_str)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass

    try:
        loaded = json5.loads(config_str)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        raise ValueError("Unable to parse config block as YAML or JSON5.")


def _dedent_after_directive(block: list[str]) -> str:
    return textwrap.dedent(
        "\n".join(
            block[1:] if block and block[0].strip().startswith("doc-inject:configure") else block
        )
    )
