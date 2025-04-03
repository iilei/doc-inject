import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from doc_inject.parsers.toml import parse_toml
from doc_inject.parsers.yaml import parse_yaml


def test_parse_yaml_dotted_path():
    content = dedent("""
        dashboards:
          main:
            title: "Main Dashboard"
            uid: "abc123"
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    result = parse_yaml(path, "dashboards.main.title")
    assert result == "Main Dashboard"


def test_parse_toml_dotted_path():
    content = dedent("""
        [dashboards.main]
        title = "Main Dashboard"
        uid = "abc123"
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".toml", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    result = parse_toml(path, "dashboards.main.uid")
    assert result == "abc123"


def test_parse_toml_raises_on_invalid_key():
    content = dedent("""
        [app]
        version = "1.0.0"
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".toml", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    with pytest.raises(ValueError) as excinfo:
        parse_toml(path, "app.build.timestamp")

    assert "Key 'build' not found" in str(excinfo.value)
