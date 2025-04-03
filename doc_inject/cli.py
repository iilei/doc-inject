from pathlib import Path

import typer

from doc_inject.engine import inject_from_file

app = typer.Typer(help="Inject rendered content into documents using config-driven templates.")


@app.command()
def run(
    file: Path = typer.Argument(..., exists=True, help="Path to the document to inject into."),
    dry_run: bool = typer.Option(False, help="Print output instead of modifying the file."),
):
    """Render and inject content into a document."""
    try:
        inject_from_file(file, dry_run=dry_run)
    except ValueError as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1)


app.command(name=None)(run)
