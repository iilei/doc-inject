import tempfile
from pathlib import Path
from textwrap import dedent

from doc_inject.parsers.text import parse_text


def test_regex_multiline_with_named_group():
    content = dedent("""
        # README

        ## About
        This is a multi-line
        section of documentation.

        ## Usage
        Here goes usage instructions.
    """)

    # Write test content to a temp markdown file
    with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    # Multiline regex with named capture group
    query = r"regex:(?ms)^## About\n(?P<about>.+?)\n##"

    result = parse_text(path, query)

    expected = {"about": "This is a multi-line\nsection of documentation.\n"}

    assert result == expected


def test_regex_match_without_named_groups_falls_back_to_value():
    content = dedent("""
        Version: 3.2.1
        - Feature A
        - Fix B
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    # Regex without named group
    query = r"regex:^Version: (\d+\.\d+\.\d+)"

    result = parse_text(path, query)

    expected = {"value": "Version: 3.2.1"}

    assert result == expected


def test_slice_lines_returns_correct_range():
    content = dedent("""\
        Line 0
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
    """)

    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        path = Path(tmp.name)

    query = "slice:2:5"  # Should return lines 2, 3, 4 (zero-indexed)

    result = parse_text(path, query)

    expected = {"value": "Line 2\nLine 3\nLine 4"}

    assert result == expected
