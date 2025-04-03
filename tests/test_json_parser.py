import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from doc_inject.parsers.json import parse_json


def test_parse_jsonpath_from_valid_json():
    content = dedent("""
        {
            "dashboard": {
                "uid": "abc123",
                "title": "Sales"
            }
        }
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    result = parse_json(path, "$.dashboard.uid")
    assert result == "abc123"


def test_parse_json5_with_comments_and_trailing_commas():
    content = dedent("""
        {
            // This is a comment
            "dashboard": {
                "uid": "abc123",
                "title": "Sales",
            },
        }
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".json5", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    result = parse_json(path, "$.dashboard.title")
    assert result == "Sales"


def test_parse_jsonpath_raises_if_not_found():
    content = dedent("""
        {
            "app": {
                "version": "1.2.3"
            }
        }
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    with pytest.raises(ValueError) as excinfo:
        parse_json(path, "$.app.build.timestamp")

    assert "No match found for JSONPath query" in str(excinfo.value)
