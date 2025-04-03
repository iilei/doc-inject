from pathlib import Path

import pytest
from pydantic import ValidationError

from doc_inject.config import InjectItem


def test_parser_inferred_from_json_extension():
    item = InjectItem(file=Path("example.json"), query="$.uid", template="{{ value }}")
    assert item.parser == "json"


def test_parser_can_be_set_explicitly():
    item = InjectItem(
        file=Path("example.data"), parser="yaml", query="root.key", template="{{ value }}"
    )
    assert item.parser == "yaml"


def test_vars_satisfies_validation():
    item = InjectItem(
        file=Path("example.yaml"),
        vars={"uid": "$.uid", "title": "$.title"},
        template="{{ uid }} / {{ title }}",
    )
    assert item.parser == "yaml"
    assert "uid" in item.vars


def test_validation_fails_without_query_or_vars():
    with pytest.raises(ValidationError) as excinfo:
        InjectItem(file=Path("data.json"), template="{{ value }}")
    assert "Either 'vars' or 'query' must be defined." in str(excinfo.value)


def test_validation_fails_with_ambiguous_query_and_vars():
    with pytest.raises(ValidationError) as excinfo:
        InjectItem(
            file=Path("example.json"), query="$.uid", vars={"uid": "$.uid"}, template="{{ uid }}"
        )
    assert "Provide either 'query' or 'vars', not both." in str(excinfo.value)


def test_validation_fails_with_unknown_extension():
    with pytest.raises(ValidationError) as excinfo:
        InjectItem(file=Path("data.unknown"), query="$.uid", template="{{ value }}")
    assert "Cannot infer parser from file extension" in str(excinfo.value)


def test_parser_inferred_from_toml_extension():
    item = InjectItem(
        file=Path("pyproject.toml"), query="tool.project.name", template="{{ value }}"
    )
    assert item.parser == "toml"


def test_parser_inferred_from_yaml_extension():
    item = InjectItem(file=Path("config.yaml"), query="dashboard.title", template="{{ value }}")
    assert item.parser == "yaml"


def test_parser_inferred_from_yml_extension():
    item = InjectItem(
        file=Path("config.yml"), vars={"uid": "dashboard.uid"}, template="UID: {{ uid }}"
    )
    assert item.parser == "yaml"
    assert "uid" in item.vars
