# doc-inject

**Inject up-to-date content into your docs from a single source of truth.**
Configurable, format-aware, comment-driven content rendering — perfect for docs, dashboards, templates, and more.

[![CI](https://github.com/iilei/doc-inject/actions/workflows/ci.yml/badge.svg)](https://github.com/iilei/doc-inject/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 What is it?

`doc-inject` is a flexible CLI and pre-commit hook that **injects dynamic content** into documentation files by using:

- 🧩 Configs in **JSON, YAML, or TOML**
- ✍️ Format-aware **templating** (Markdown, HTML, AsciiDoc, Mermaid, etc.)
- 💬 Lightweight **comment markers** to drive injection points
- 🔁 Supports **dashboards, snippets, metadata**, and anything you can script

---

Each entry in the config is a named injection block.

| Field      | Type     | Required                          | Description                                                                     |
| ---------- | -------- | --------------------------------- | ------------------------------------------------------------------------------- |
| `file`     | `string` | :white_check_mark: Yes            | Path to the source file (e.g. JSON, YAML, TOML)                                 |
| `parser`   | `string` | :x:  Optional                     | One of: `json`, `yaml`, `toml`, `text`. Inferred from file extension if omitted |
| `query`    | `string` | :ballot_box_with_check: Required* | A single query to extract a value as `{{ value }}`                              |
| `vars`     | `object` | :ballot_box_with_check: Required* | A dictionary of named variables, each assigned via a query                      |
| `template` | `string` | :white_check_mark:Yes             | Jinja2-style template using `{{ value }}` or named variables like `{{ uid }}`   |

:warning: Either `query` **or** `vars` must be provided. You **cannot omit both**.

:white_check_mark: `parser` is optional — inferred from `file` extension (e.g. `.json`, `.yml`, etc.)


## ✨ Example

### `README.md` snippet:
```markdown
<!-- DOC_INJECT_CONFIG
{
  "simple-dashboard": {
    "file": "dashboards/main.json",
    "query": "$.uid",
    "template": "[Dashboard](https://grafana.example.com/d/{{ value }})",
    "strict_template": true
  },
  "version-note": {
    "file": "CHANGELOG.md",
    "parser": "text",
    "query": "regex:^Version: (?P<version>\\d+\\.\\d+\\.\\d+)",
    "template": "**Current Version**: {{ version }}",
    "strict_template": false
  }
}
-->

...

<!-- DOC_INJECT_START simple-dashboard-->
<!-- DOC_INJECT_END simple-dashboard -->

...

<!-- DOC_INJECT_START version-note -->
<!-- DOC_INJECT_END version-note -->

```


