from textwrap import dedent

from doc_inject.config_loader import extract_config_from_document


def test_extract_from_adoc_line_comments(tmp_path):
    file = tmp_path / "doc.adoc"
    file.write_text(
        dedent("""
        // doc-inject:configure
        // config:
        //   file: data.json
        //   query: $.uid
        //   template: "UID: {{ value }}"
    """)
    )
    config = extract_config_from_document(file)
    assert "config" in config.get_items()


def test_extract_from_adoc_block_comment_delimited(tmp_path):
    file = tmp_path / "block.adoc"
    file.write_text(
        dedent("""
        ////
        doc-inject:configure
        config:
          file: data.json
          query: $.uid
          template: "UID: {{ value }}"
        ////
    """)
    )
    config = extract_config_from_document(file)
    assert "config" in config.get_items()


def test_extract_from_adoc_block_macro_comment(tmp_path):
    file = tmp_path / "macro.adoc"
    file.write_text(
        dedent("""
        [comment]
        --
        doc-inject:configure
        config:
          file: data.json
          query: $.uid
          template: "UID: {{ value }}"
        --
    """)
    )
    config = extract_config_from_document(file)
    assert "config" in config.get_items()


def test_extract_from_adoc_paragraph_comment(tmp_path):
    file = tmp_path / "para.adoc"
    file.write_text(
        dedent("""
        [comment]
        doc-inject:configure
        config:
                file: data.json
                query: $.uid
                template: "UID: {{ value }}"
        """)
    )
    config = extract_config_from_document(file)
    assert "config" in config.get_items()
