from pathlib import Path


def inject_from_file(file_path: Path, dry_run: bool = False):
    content = file_path.read_text()

    # TODO: Implement config and tag parsing logic here
    result = content.replace("{{example}}", "Injected content!")

    if dry_run:
        print(result)
    else:
        file_path.write_text(result)
