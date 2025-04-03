from doc_inject.template import render_template


def test_render_template_strict_mode_success():
    template = "{{ title }} v{{ version }}"
    context = {"title": "My App", "version": "1.2.3"}
    result = render_template(template, context, strict=True)
    assert result == "My App v1.2.3"


def test_render_template_strict_mode_raises_on_missing_var():
    template = "Hello, {{ user }}!"
    context = {}

    try:
        render_template(template, context, strict=True)
    except ValueError as e:
        assert "Failed to render template" in str(e)
    else:
        assert False, "Expected failure due to missing variable in strict mode"


def test_render_template_non_strict_renders_empty_on_missing_var():
    template = "Hello, {{ user }}!"
    context = {}

    result = render_template(template, context, strict=False)
    assert result == "Hello, !"
