import tempfile
from pathlib import Path
from textwrap import dedent

from doc_inject.config import InjectItem
from doc_inject.parsers.core import resolve_query


def test_resolve_query_with_json_value():
    content = dedent("""
        {
            "dashboard": {
                "uid": "abc123"
            }
        }
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    item = InjectItem(
        file=path, parser="json", query="$.dashboard.uid", template="UID: {{ value }}"
    )

    context = resolve_query(item)
    assert context == {"value": "abc123"}


def test_resolve_query_with_yaml_vars():
    content = dedent("""
        dashboard:
          uid: "xyz789"
          title: "Overview"
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    item = InjectItem(
        file=path,
        parser="yaml",
        vars={"uid": "dashboard.uid", "title": "dashboard.title"},
        template="[{{ title }}](https://grafana.example.com/d/{{ uid }})",
    )

    context = resolve_query(item)
    assert context == {"uid": "xyz789", "title": "Overview"}


def test_resolve_query_with_text_regex():
    content = dedent("""
        # Changelog

        Version: 2.4.0
        - Added sync support
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    item = InjectItem(
        file=path,
        parser="text",
        query=r"regex:^Version: (?P<version>\d+\.\d+\.\d+)",
        template="Version: {{ version }}",
    )

    context = resolve_query(item)
    assert context == {"version": "2.4.0"}
