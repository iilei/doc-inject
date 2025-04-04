from pathlib import Path
from typing import Optional

import typer

from doc_inject.engine import inject_from_file

app = typer.Typer(help="Inject rendered content into documents using config-driven templates.")


@app.command()
def run(
    files: list[Path] = typer.Argument(...),
    config: Optional[Path] = None,
    config_query: Optional[str] = None,
    check: bool = False,
    verbose: bool = False,
):
    from doc_inject.config_loader import extract_config_from_document, extract_config_from_file

    failures = 0
    for file in files:
        original = file.read_text()

        config = (
            extract_config_from_file(config, query=config_query)
            if config
            else extract_config_from_document(file)
        )

        inject_from_file(file, dry_run=False, config=config)

        updated = file.read_text()
        if check and original != updated:
            typer.echo(f":: error :: {file} is out of date", err=True)
            failures += 1
        elif verbose:
            typer.echo(f"{file} is up-to-date ✅")

    if failures:
        raise typer.Exit(code=1)


app.command(name=None)(run)
