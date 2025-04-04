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
    readme_text = dedent("""\
        <!-- doc-inject:configure
        {
          "test-block": {
            "file": "<file>",
            "parser": "json",
            "query": "$.uid",
            "template": "Hello {{ missing }}!",
            "strict_template": false
          }
        }
        -->

        <!-- DOC_INJECT_START test-block -->
        <!-- DOC_INJECT_END test-block -->
        """).replace("<file>", str(json_path))
    readme_path.write_text(readme_text)

    result = runner.invoke(app, ["run", str(readme_path)])

    updated = readme_path.read_text()
    assert result.exit_code == 0
    assert "Hello !" in updated


def test_cli_strict_env_false_allows_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("DOC_INJECT_STRICT", "false")

    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps({"x": 1}))

    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        dedent("""\
        <!-- doc-inject:configure
        {
          "env-test": {
            "file": "<file>",
            "parser": "json",
            "query": "$.x",
            "template": "{{ missing }}"
          }
        }
        -->

        <!-- DOC_INJECT_START env-test -->
        ?
        <!-- DOC_INJECT_END env-test -->
    """).replace("<file>", str(data_path))
    )

    result = runner.invoke(app, ["run", str(readme_path)])

    assert result.exit_code == 0
    assert "<!-- DOC_INJECT_START env-test --><!-- DOC_INJECT_END env-test -->" in "".join(
        readme_path.read_text().split("\n")
    )
