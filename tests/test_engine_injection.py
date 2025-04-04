import json
import os
from textwrap import dedent

from doc_inject.config import InjectConfig
from doc_inject.engine import inject_from_file


def test_inject_from_file_with_external_config(tmp_path):
    # Create source data file
    data_file = tmp_path / "data.json"
    data_file.write_text('{"uid": "abc-123"}')

    # Create config file with relative path
    config_file = tmp_path / "config.json"
    config = {"dashboard": {"file": "data.json", "query": "$.uid", "template": "UID: {{ value }}"}}
    config_file.write_text(json.dumps(config))

    # Create target markdown file with injection markers
    target_file = tmp_path / "README.md"
    target_file.write_text(
        dedent("""\
        # Dashboards

        <!-- DOC_INJECT_START dashboard -->
        placeholder
        <!-- DOC_INJECT_END dashboard -->
    """)
    )

    # Change cwd temporarily so relative file paths resolve
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        inject_from_file(file_path=target_file, config=InjectConfig.model_validate(config))
    finally:
        os.chdir(old_cwd)

    # Assert the file was modified with injected content
    result = target_file.read_text()
    assert "UID: abc-123" in result
    assert "placeholder" not in result
