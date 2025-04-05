import json
from textwrap import dedent

from doc_inject.config_loader import extract_config_from_document
from doc_inject.engine import inject_from_file


def test_inject_dashboard_list_from_glob(tmp_path):
    # Create dashboard files
    dashboards_dir = tmp_path / "dashboards"
    dashboards_dir.mkdir(parents=True)
    for i in range(3):
        (dashboards_dir / f"db{i}.json").write_text(
            json.dumps({"uid": f"uid-{i}", "title": f"Dashboard {i}"})
        )

    # Create README.md with inline config
    readme = tmp_path / "README.adoc"
    readme.write_text(
        dedent(
            """\
        [comment]
        doc-inject:configure
        dashboard-list:
          glob: "dashboards/*.json"
          parser: json
          query: "$"
          template: |-
            {% for d in value|sort(attribute='uid', reverse = True) %}
            * https://grafana.example.com/d/{{ d.uid }}[{{ d.title }}]
            {%- endfor %}

        <!-- DOC_INJECT_START dashboard-list -->
        <!-- DOC_INJECT_END dashboard-list -->
    """.replace("dashboards/*.json", f"{dashboards_dir}/*.json")
        )
    )

    # Inject
    inject_from_file(readme, config=extract_config_from_document(readme))

    result = readme.read_text()
    assert (
        dedent(
            """\
                <!-- DOC_INJECT_START dashboard-list -->

                * https://grafana.example.com/d/uid-2[Dashboard 2]
                * https://grafana.example.com/d/uid-1[Dashboard 1]
                * https://grafana.example.com/d/uid-0[Dashboard 0]
                <!-- DOC_INJECT_END dashboard-list -->
            """
        )
        in result
    )
