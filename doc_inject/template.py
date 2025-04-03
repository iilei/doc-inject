import os
from typing import Dict

from jinja2 import Environment, StrictUndefined, Undefined


def render_template(template_str: str, context: Dict[str, str], strict: bool | None = None) -> str:
    """
    Render the template using Jinja2.
    - strict=True: fail on missing variables
    - strict=False: allow missing variables (render empty string)
    - strict=None: resolve from DOC_INJECT_STRICT env or default True
    """
    if strict is None:
        strict = resolve_strict_from_env()

    env = Environment(undefined=StrictUndefined if strict else Undefined)

    try:
        template = env.from_string(template_str)
        return template.render(**context)
    except Exception as e:
        raise ValueError(f"Failed to render template: {e}")


def resolve_strict_from_env() -> bool:
    raw = os.getenv("DOC_INJECT_STRICT", "true")
    return raw.strip().lower() not in {"0", "false", "no"}
