# Configuration Reference

This document describes all available fields in the `<!-- DOC_INJECT_CONFIG ... -->` block used by **doc-inject**.

---

## 🔧 Basic Structure
Each injection block defines how dynamic content is extracted and rendered:

```json
{
  "example-block": {
    "file": "path/to/file.json",
    "parser": "json",
    "query": "$.some.path",
    "template": "Value: {{ value }}",
    "strict_template": true
  }
}
```

---

## :puzzle_piece: Field Reference

| Field             | Type      | Required                          | Description                                                                                                   |
| ----------------- | --------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `file`            | `string`  | :white_check_mark: Yes            | Path to the source file. JSON, YAML, TOML, Markdown, etc.                                                     |
| `parser`          | `string`  | :x: No                            | One of: `json`, `yaml`, `toml`, `text`. Inferred from file extension if omitted.                              |
| `query`           | `string`  | :ballot_box_with_check: Required* | Query expression used to extract the value into `{{ value }}`. Required if `vars` is not provided.            |
| `vars`            | `object`  | :ballot_box_with_check: Required* | Mapping of variable names to query expressions. Required if `query` is not provided.                          |
| `template`        | `string`  | :white_check_mark: Yes            | Jinja2 template string. Uses `{{ value }}` or named variables from `vars`.                                    |
| `strict_template` | `boolean` | :x: No                            | Enforces strict rendering (default: true). If false, missing template variables will render as empty strings. |

> :warning: You must provide **either** `query` or `vars`. You cannot omit both.

---

## :globe_with_meridians: Global Fallback (Environment Variable)

Set a default for `strict_template` project-wide using an environment variable:

```bash
export DOC_INJECT_STRICT=false
```

This only applies when `strict_template` is **not explicitly set** in the config block.

---

## :notebook: Examples

### :white_check_mark: Minimal Example with Query
```json
{
  "version": {
    "file": "CHANGELOG.md",
    "parser": "text",
    "query": "regex:^Version: (?P<version>\\d+\\.\\d+\\.\\d+)",
    "template": "Current version: {{ version }}"
  }
}
```

### :white_check_mark: Named Variables with YAML
```json
{
  "meta": {
    "file": "config.yaml",
    "parser": "yaml",
    "vars": {
      "uid": "dashboard.uid",
      "title": "dashboard.title"
    },
    "template": "[{{ title }}](https://grafana.example.com/d/{{ uid }})",
    "strict_template": true
  }
}
```

### :white_check_mark: Lenient Mode
```json
{
  "incomplete": {
    "file": "doc.md",
    "parser": "text",
    "query": "regex:^.*?",
    "template": "Preview: {{ snippet }}",
    "strict_template": false
  }
}
```

---

## :mag: Configuration in Comments (Inline Blocks)

You may embed configuration directly into supported source files using comments. This works across file formats with different comment styles. Use the directive `doc-inject:configure` followed by structured config.

### :page_facing_up: Supported Comment Styles

| File Extension   | Comment Prefix | Example Syntax                        |
| ---------------- | -------------- | ------------------------------------- |
| `.yaml`, `.yml`  | `#`            | `# doc-inject:configure`              |
| `.toml`          | `#`            | `# doc-inject:configure`              |
| `.json5`         | `//`           | `// doc-inject:configure`             |
| `.md`, `.html`   | `<!-- ... -->` | `<!-- doc-inject:configure {...} -->` |
| `.jinja2`, `.j2` | `{# ... #}`    | `{# doc-inject:configure {...} #}`    |

For YAML-style (`#`) and similar line comment formats, the block continues on following comment-prefixed lines. Indentation is preserved and normalized.

```yaml
# doc-inject:configure
# dashboard:
#   file: dashboards/main.json
#   query: $.uid
#   template: "UID: {{ value }}"
```

You can also use:

```html
<!-- doc-inject:configure
{
  "meta": {
    "file": "config.yaml",
    "query": "dashboard.title",
    "template": "{{ value }}"
  }
}
-->
```

Indentation-sensitive formats like YAML are safely parsed by removing the comment prefix and dedenting all lines uniformly.

---

Need more? See usage examples in the main README or explore advanced templating support in Jinja2.

