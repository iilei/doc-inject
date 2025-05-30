import re
from pathlib import Path

from doc_inject.config import InjectItem
from doc_inject.parsers.core import resolve_query
from doc_inject.template import render_template

INJECT_BLOCK_PATTERN = re.compile(
    r"""
    (?P<start>
        (?:<!--|//|\#|\;) \s* DOC_INJECT_START \s+ (?P<name>[\w\-]+) \s* (?:-->)?
    )
    (?P<content>.*?)
    (?P<end>
        (?:<!--|//|\#|\;) \s* DOC_INJECT_END \s+ \2 \s* (?:-->)?
    )
    """,
    re.DOTALL | re.VERBOSE,
)


def inject_from_file(file_path: Path, config: InjectItem):
    content = file_path.read_text(encoding="utf-8")

    items = config.get_items()

    def replace_block(match: re.Match) -> str:
        name = match.group("name")
        if name not in items:
            raise ValueError(f"No config found for injection block: '{name}'")

        item = items[name]

        # Resolve context and render
        context = resolve_query(item)
        rendered = render_template(item.template, context, strict=item.strict_template)

        return f"{match.group('start')}\n{rendered}\n{match.group('end')}"

    result = INJECT_BLOCK_PATTERN.sub(replace_block, content)

    file_path.write_text(result, encoding="utf-8")
