import json
from pathlib import Path
from textwrap import dedent

from doc_inject.config_loader import extract_config_from_document
from doc_inject.engine import inject_from_file


def test_injection_comment_styles_without_html_multiline(tmp_path: Path):
    dashboards_dir = tmp_path / "dashboards"
    dashboards_dir.mkdir()
    dashboard_file = dashboards_dir / "test.json"
    dashboard_file.write_text(json.dumps({"uid": "abc", "title": "Test Dash"}))

    comment_styles = {
        "hash": ("#", "", "yaml"),
        "slash": ("//", "", "json5"),
        "semicolon": (";", "", "toml"),
    }
    jinja = "{{ value.title }}"
    for style, (prefix, suffix, filetype) in comment_styles.items():
        file = tmp_path / f"test_{style}.{filetype}"
        file.write_text(
            dedent(f"""\
                {prefix} doc-inject:configure {suffix}
                {prefix} test-block:
                {prefix}   file: {dashboard_file.as_posix()}
                {prefix}   query: "$"
                {prefix}   template: "* {jinja}"
                {prefix} {suffix}

                {prefix} DOC_INJECT_START test-block {suffix}
                (placeholder)
                {prefix} DOC_INJECT_END test-block {suffix}
                """)
        )

        inject_from_file(file, config=extract_config_from_document(file))

        result = file.read_text()
        assert "* Test Dash" in result, f"Injection failed for comment style: {style}"
