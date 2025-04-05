from pathlib import Path
from textwrap import dedent

import pytest

from doc_inject.config_loader import _parse_structured_config, extract_config_from_document


def _write_file(tmp_path, filename: str, content: str) -> Path:
    path = tmp_path / filename
    path.write_text(dedent(content))
    return path


def test_extract_from_markdown_comment(tmp_path):
    md = _write_file(
        tmp_path,
        "README.md",
        """
        <!-- doc-inject:configure
        {
          "example": {
            "file": "data.json",
            "query": "$.uid",
            "template": "{{ value }}"
          }
        }
        -->
    """,
    )

    config = extract_config_from_document(md)
    assert "example" in config.get_items()
    assert config.get_items()["example"]._resolved_files[0].name == "data.json"


def test_extract_from_yaml_comment_block(tmp_path):
    yaml_file = _write_file(
        tmp_path,
        "config.yaml",
        """
        # doc-inject:configure
        # example:
        #   file: data.json
        #   query: $.uid
        #   template: "{{ value }}"
    """,
    )

    config = extract_config_from_document(yaml_file)
    assert "example" in config.get_items()
    assert config.get_items()["example"]._resolved_files[0].name == "data.json"


def test_extract_from_jinja2_json5_comment_block(tmp_path):
    jinja_json5 = _write_file(
        tmp_path,
        "template.jinja2.json5",
        """
        {# doc-inject:configure
        {
          "block": {
            "file": "data.json",
            "query": "$.uid",
            "template": "{{ value }}"
          }
        }
        #}
    """,
    )

    config = extract_config_from_document(jinja_json5)
    assert "block" in config.get_items()
    assert config.get_items()["block"]._resolved_files[0].name == "data.json"


def test_extract_config_block_not_found(tmp_path):
    f = _write_file(tmp_path, "some.md", "Just some text.")

    with pytest.raises(ValueError, match="No usable config block found"):
        extract_config_from_document(f)


def test_extract_from_indented_yaml_config(tmp_path):
    yaml_content = dedent("""
        # This file includes embedded config
        #     doc-inject:configure
        #     test-inject:
        #       file: dashboards/sample.json
        #       query: $.uid
        #       template: "UID: {{ value }}"
    """)

    f = tmp_path / "example.yaml"
    f.write_text(yaml_content)

    config = extract_config_from_document(f)
    items = config.get_items()

    assert "test-inject" in items

    assert items["test-inject"]._resolved_files[0].name == "sample.json"
    assert items["test-inject"].template == "UID: {{ value }}"


def test_parse_invalid_yaml_falls_back():
    invalid_yaml = """
    - just
    - a
    - list
    """

    with pytest.raises(ValueError, match="Unable to parse config block as YAML or JSON5"):
        _parse_structured_config(invalid_yaml)


def test_parse_valid_json5_fallback():
    json5_input = """
    // this is a comment
    {
      example: {
        file: "data.json",
        query: "$.uid",
        template: "{{ value }}"
      }
    }
    """

    parsed = _parse_structured_config(json5_input)
    assert "example" in parsed
    assert parsed["example"]["file"] == "data.json"
    assert parsed["example"]["template"] == "{{ value }}"
    assert parsed["example"]["query"] == "$.uid"
