import os
from pathlib import Path
from typing import Optional

import typer

from doc_inject.config import InjectConfig
from doc_inject.engine import inject_from_file

app = typer.Typer(help="Inject rendered content into documents using config-driven templates.")


@app.command()
def run(
    files: list[Path] = typer.Argument(...),
    config: Optional[Path] = None,
    config_query: Optional[str] = None,
):
    from doc_inject.config_loader import extract_config_from_document, extract_config_from_file

    for file in files:
        base_path = Path(os.path.dirname(os.path.realpath(file)))

        config: InjectConfig = (
            extract_config_from_file(config, query=config_query).with_base_path(base_path)
            if config
            else extract_config_from_document(file).with_base_path(base_path)
        )

        inject_from_file(file, config=config)


app.command(name=None)(run)
