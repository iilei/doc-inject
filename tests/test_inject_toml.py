# Re-execute the final test after code environment reset
import json
from pathlib import Path
from textwrap import dedent

from doc_inject.config_loader import extract_config_from_file
from doc_inject.engine import inject_from_file


def test_cli_inject_from_toml_config(tmp_path):
    # Create dashboard source files
    dashboards_dir = tmp_path / "dashboards"
    dashboards_dir.mkdir(parents=True)
    for i in range(2):
        (dashboards_dir / f"db{i}.json").write_text(
            json.dumps({"uid": f"uid-{i}", "title": f"Dashboard {i}"})
        )

    # Create pyproject.toml with config section
    (tmp_path / "pyproject.toml").write_text(
        dedent(
            r'''
            [tool.doc-inject.dashboard-list]
            glob = "dashboards/*.json"
            parser = "json"
            query = "$"
            template = """
            {%- for d in value|sort(attribute='uid', reverse = True) -%}
            * https://grafana.example.com/d/{{ d.uid }}[{{ d.title }}]
            {% endfor -%}
            """
            '''.replace("dashboards/*.json", f"{dashboards_dir}/*.json")
        )
    )

    # Create README.adoc with tag
    readme = tmp_path / "README.adoc"
    readme.write_text(
        dedent("""\
        <!-- DOC_INJECT_START dashboard-list -->
        <!-- DOC_INJECT_END dashboard-list -->
    """)
    )

    print(tmp_path / "pyproject.toml")

    # Run the injection
    inject_from_file(
        file_path=readme,
        config=extract_config_from_file(Path(tmp_path / "pyproject.toml")),
    )

    result = readme.read_text()
    assert (
        dedent(
            """\
                <!-- DOC_INJECT_START dashboard-list -->
                * https://grafana.example.com/d/uid-1[Dashboard 1]
                * https://grafana.example.com/d/uid-0[Dashboard 0]

                <!-- DOC_INJECT_END dashboard-list -->
            """
        )
        in result
    )
