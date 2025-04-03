import tempfile
from pathlib import Path

from doc_inject.engine import inject_from_file


def test_basic_injection():
    with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
        tmp.write("Before {{example}} after.")
        tmp.flush()

        inject_from_file(Path(tmp.name))

        tmp.seek(0)
        assert "Injected content!" in tmp.read()
