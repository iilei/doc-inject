import re
from pathlib import Path
from typing import Any, Dict


def parse_text(path: Path, query: str) -> Dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()

    if query.startswith("regex:"):
        pattern = query[len("regex:") :]
        return _match_regex(lines, pattern)

    elif query.startswith("slice:"):
        try:
            range_str = query[len("slice:") :]
            start_str, end_str = range_str.split(":")
            start, end = int(start_str), int(end_str)
        except Exception:
            raise ValueError(f"Invalid slice syntax in query: '{query}'")

        sliced = lines[start:end]
        return {"value": "\n".join(sliced)}

    else:
        raise ValueError(f"Unsupported text query: '{query}'")


def _match_regex(lines: list[str], pattern: str) -> Dict[str, str]:
    """Match named groups from the first matching regex.

    - If the pattern uses inline flags (e.g. (?m), (?s), (?x)), it is applied to the whole file.
    - Otherwise, it is applied line-by-line.
    """
    compiled = re.compile(pattern)

    # Heuristic: If the pattern starts with inline flags, apply to whole file
    if pattern.lstrip().startswith("(?"):
        text = "\n".join(lines)
        match = compiled.search(text)
        if match:
            groups = match.groupdict()
            return groups if groups else {"value": match.group(0)}
    else:
        for line in lines:
            match = compiled.search(line)
            if match:
                groups = match.groupdict()
                return groups if groups else {"value": match.group(0)}

    raise ValueError(f"No match found for regex pattern: {pattern}")
