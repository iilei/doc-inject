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
<!-- DOC_INJECT_CONFIG
{
  "md-from-dashboard": {
    "file": "dashboards/overview.json",
    "query": "$.panels[?(@.type=='text')].options.content",
    "template": "{{ value }}"
  },
  "ref-dashboard": {
    "file": "dashboards/main.json",
    "parser": "json",
    "vars": {
      "uid": "$.uid",
      "title": "$.title"
    },
    "template": "[{{ title }}](https://grafana.example.com/d/{{ uid }})"
  }
}
-->

...

<!-- DOC_INJECT_START md-from-dashboard -->
<!-- DOC_INJECT_END md-from-dashboard -->

...

<!-- DOC_INJECT_START ref-dashboard -->
<!-- DOC_INJECT_END ref-dashboard -->

```
