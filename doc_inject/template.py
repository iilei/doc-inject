from typing import Dict

from jinja2 import Environment, StrictUndefined, Undefined


def render_template(template_str: str, context: Dict[str, str], strict: bool = True) -> str:
    """
    Render the template using Jinja2 with optional strict mode.
    - strict=True (default): raise error on missing variables
    - strict=False: silently ignore missing variables
    """
    env = Environment(undefined=StrictUndefined if strict else Undefined)
    try:
        template = env.from_string(template_str)
        return template.render(**context)
    except Exception as e:
        raise ValueError(f"Failed to render template: {e}")
