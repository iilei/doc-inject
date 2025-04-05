# Re-import necessary functions after kernel reset
import json
from pathlib import Path
from textwrap import dedent

from doc_inject.config_loader import extract_config_from_document
from doc_inject.engine import inject_from_file


def test_relative_paths_resolve_from_config_location(tmp_path: Path):
    # Create nested structure: tmp/doc/config.md and tmp/data/db.json
    doc_dir = tmp_path / "docs"
    data_dir = tmp_path / "data"
    doc_dir.mkdir()
    data_dir.mkdir()

    dashboard = {"uid": "xyz", "title": "Ops Panel"}
    (data_dir / "db.json").write_text(json.dumps(dashboard))

    # Inline config using relative file path
    readme = doc_dir / "README.md"
    readme.write_text(
        dedent("""\
        <!-- doc-inject:configure {
          "block": {
            "file": "../data/db.json",
            "query": "$",
            "template": "** {{ value.title }} **"
          }
        } -->
        <!-- DOC_INJECT_START block -->
        (placeholder)
        <!-- DOC_INJECT_END block -->
    """)
    )

    inject_from_file(readme, config=extract_config_from_document(readme).with_base_path(doc_dir))
    result = readme.read_text()

    assert "** Ops Panel **" in result


def test_relative_glob_resolves_from_config_location(tmp_path: Path):
    # tmp/project/config.md and tmp/project/data/db[0-2].json
    root = tmp_path / "project"
    doc_dir = root
    data_dir = root / "data"
    doc_dir.mkdir()
    data_dir.mkdir()

    for i in range(3):
        (data_dir / f"db{i}.json").write_text(
            json.dumps({"uid": f"uid-{i}", "title": f"Dashboard {i}"})
        )

    readme = doc_dir / "README.md"
    readme.write_text(
        dedent("""\
        <!-- doc-inject:configure
        {
          "dashboards": {
            "glob": "./data/*.json",
            "parser": "json",
            "query": "$",
            "template": "{% for d in value %}- {{ d.title }} {% endfor %}"
          }
        }
        -->
        <!-- DOC_INJECT_START dashboards -->
        (placeholder)
        <!-- DOC_INJECT_END dashboards -->
    """)
    )

    inject_from_file(readme, config=extract_config_from_document(readme).with_base_path(doc_dir))
    result = readme.read_text()

    assert "- Dashboard 0" in result
    assert "- Dashboard 1" in result
    assert "- Dashboard 2" in result
