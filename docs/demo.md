<!--
Line 1
Line 2
Line 3
Line 4
Line 5
-->

<!-- doc-inject:configure
{
    "test-block": {
    "file": "docs/demo.md",
    "parser": "text",
    "query": "slice:2:4" ,
    "template": "```\n{{ value }}\n```",
    "strict_template": false
    }
}
-->

# Injected content:

<!-- DOC_INJECT_START test-block -->
```
Line 2
Line 3
```
<!-- DOC_INJECT_END test-block -->

***
