import json
from textwrap import dedent

from typer.testing import CliRunner

from doc_inject.cli import app

runner = CliRunner()


def test_cli_respects_strict_template_false(tmp_path):
    # Write source JSON file
    json_path = tmp_path / "data.json"
    json_path.write_text(json.dumps({"uid": "abc123"}))

    # README with config + injection marker, and missing variable in template
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        dedent("""\
        <!-- DOC_INJECT_CONFIG
        {
          "test-block": {
            "file": "data.json",
            "parser": "json",
            "query": "$.uid",
            "template": "Hello {{ missing }}",
            "strict_template": false
          }
        }
        -->

        <!-- DOC_INJECT_START test-block -->
        <!-- DOC_INJECT_END test-block -->
    """)
    )

    result = runner.invoke(app, ["run", str(readme_path)])

    updated = readme_path.read_text()
    assert result.exit_code == 0
    assert "Hello " in updated


def test_cli_strict_env_false_allows_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("DOC_INJECT_STRICT", "false")

    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps({"x": 1}))

    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        dedent("""\
        <!-- DOC_INJECT_CONFIG
        {
          "env-test": {
            "file": "data.json",
            "parser": "json",
            "query": "$.x",
            "template": "{{ missing }}"
          }
        }
        -->

        <!-- DOC_INJECT_START env-test -->
        <!-- DOC_INJECT_END env-test -->
    """)
    )

    result = runner.invoke(app, ["run", str(readme_path)])

    assert result.exit_code == 0
    assert readme_path.read_text().count("{{ missing }}") == 0
