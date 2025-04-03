from pathlib import Path

import pytest

from doc_inject.config import InjectItem
from doc_inject.template import render_template


def test_render_template_strict_template_true_blocks_missing_var():
    item = InjectItem(
        file=Path("fake.json"),  # not used
        query="$.irrelevant",
        template="Hello {{ user }}",
        strict_template=True,
    )

    context = {"something_else": "value"}

    with pytest.raises(ValueError) as e:
        render_template(item.template, context, strict=item.strict_template)

    assert "Failed to render template" in str(e.value)


def test_render_template_strict_template_false_allows_missing_var():
    item = InjectItem(
        file=Path("fake.json"),
        query="$.irrelevant",
        template="Hello {{ user }}",
        strict_template=False,
    )

    context = {"something_else": "value"}
    output = render_template(item.template, context, strict=item.strict_template)
    assert output == "Hello "


def test_render_template_strict_template_env_fallback(monkeypatch):
    monkeypatch.setenv("DOC_INJECT_STRICT", "false")

    item = InjectItem(
        file=Path("fake.json"),
        query="$.irrelevant",
        template="Hi {{ who }}",
        strict_template=None,
    )

    output = render_template(item.template, {}, strict=item.strict_template)
    assert output == "Hi "
