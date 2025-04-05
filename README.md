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

| Field             | Type     | Required                                     | Description                                                                |
| ----------------- | -------- | -------------------------------------------- | -------------------------------------------------------------------------- |
| `file`            | `string` | :white_check_mark: Yes (if not using `glob`) | Path to a source file. Mutually exclusive with `glob`.                     |
| `glob`            | `string` | :white_check_mark: Yes (if not using `file`) | Glob pattern resolving to multiple files.                                  |
| `parser`          | `string` | :x: Optional                                 | `json`, `yaml`, `toml`, or `text`. Inferred from file extension if omitted |
| `query`           | `string` | :ballot_box_with_check: Required*            | Query used to extract a value or object                                    |
| `vars`            | `object` | :ballot_box_with_check: Required*            | Named variables mapped to queries (`{{ uid }}`, `{{ title }}`)             |
| `template`        | `string` | :white_check_mark: Yes                       | Jinja2-style template string                                               |
| `strict_template` | `bool`   | :x: Optional                                 | Raise on missing template vars (default: true; can be set via env var)     |

> :warning: Either `query` **or** `vars` must be provided. Not both. Not neither.

> ✅ Environment fallback: use `export DOC_INJECT_STRICT=false` to disable strict rendering globally.


## ✨ Example

### 📝 Inject block into `README.adoc`
```adoc
[comment]
doc-inject:configure
dashboard-list:
  glob: "dashboards/*.json"
  parser: json
  query: "$"
  template: |
    {% for d in value|sort(attribute='uid', reverse = True) -%}
    * https://grafana.example.com/d/{{ d.uid }}[{{ d.title }}]
    {% endfor %}

<!-- DOC_INJECT_START dashboard-list -->
<!-- DOC_INJECT_END dashboard-list -->
```

Will be rendered as:

```adoc
<!-- DOC_INJECT_START dashboard-list -->
* https://grafana.example.com/d/uid-2[Dashboard 2]
* https://grafana.example.com/d/uid-1[Dashboard 1]
* https://grafana.example.com/d/uid-0[Dashboard 0]

<!-- DOC_INJECT_END dashboard-list -->
```

---

💡 You can also load config externally (e.g. `pyproject.toml`, `doc-inject.yaml`) and pass it via CLI:
```bash
doc-inject run README.adoc --config pyproject.toml --config-query tool.doc-inject
```

For more details on configuration structure and inline embedding formats, see [docs/configuration.md](docs/configuration.md).

