# doc-inject

**Inject up-to-date content into your docs from a single source of truth.**
Configurable, format-aware, comment-driven content rendering — perfect for docs, dashboards, templates, and more.

[![CI](https://github.com/iilei/doc-inject/actions/workflows/ci.yml/badge.svg)](https://github.com/iilei/doc-inject/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 What is it?

`doc-inject` is a flexible CLI and pre-commit hook that **injects dynamic content** into documentation and template files using:

- 🧩 Configs defined in **JSON, YAML, TOML** — or inline via **comments**
- ✍️ Format-aware **templating** (Markdown, HTML, Jinja2, etc.)
- 💬 Lightweight **comment-based injection markers**
- 🔁 Sources like dashboards, changelogs, frontmatter, metadata, or any structured file

It supports embedded config blocks inside `.md`, `.yaml`, `.toml`, `.json5`, `.jinja2` and others.


## ⚙️ How It Works

Each config entry defines a named injection block:

| Field             | Type     | Required                          | Description                                                                  |
| ----------------- | -------- | --------------------------------- | ---------------------------------------------------------------------------- |
| `file`            | `string` | :white_check_mark: Yes            | Path to the source file (e.g. JSON, YAML, Markdown)                          |
| `parser`          | `string` | :x: Optional                      | `json`, `yaml`, `toml`, or `text`. Inferred from `file` extension if omitted |
| `query`           | `string` | :ballot_box_with_check: Required* | Query used to extract a single value (as `{{ value }}`)                      |
| `vars`            | `object` | :ballot_box_with_check: Required* | Named variables mapped to queries (`{{ uid }}`, `{{ title }}`)               |
| `template`        | `string` | :white_check_mark: Yes            | Jinja2-style template string                                                 |
| `strict_template` | `bool`   | :x: Optional                      | Raise on missing template vars (default: true; can be set via env var)       |

> :warning: Either `query` **or** `vars` must be provided. Not both. Not neither.

> ✅ Environment fallback: use `export DOC_INJECT_STRICT=false` to disable strict rendering globally.


## ✨ Example

### 📝 Inject block into `README.md`
```markdown
<!-- doc-inject:configure
{
  "simple-dashboard": {
    "file": "dashboards/main.json",
    "query": "$.uid",
    "template": "[Dashboard](https://grafana.example.com/d/{{ value }})"
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

<!-- DOC_INJECT_START simple-dashboard -->
<!-- DOC_INJECT_END simple-dashboard -->

...

<!-- DOC_INJECT_START version-note -->
<!-- DOC_INJECT_END version-note -->
```

This results in:
```markdown
<!-- DOC_INJECT_START simple-dashboard -->
[Dashboard](https://grafana.example.com/d/abc123)
<!-- DOC_INJECT_END simple-dashboard -->
```

---

💡 You can also load config externally (e.g. `pyproject.toml`, `doc-inject.yaml`) and pass it via CLI:
```bash
doc-inject run README.md --config doc-inject.yaml
```

For more details on configuration structure and inline embedding formats, see [docs/configuration.md](docs/configuration.md).

