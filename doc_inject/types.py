from pathlib import Path
from typing import Dict, Literal, Optional

from pydantic import BaseModel, model_validator

ParserType = Literal["json", "yaml", "toml", "text"]

EXTENSION_TO_PARSER = {
    ".json": "json",
    ".adoc": "yaml",
    ".asciidoc": "yaml",
    ".rst": "yaml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".txt": "text",
    ".md": "text",
}


class InjectItem(BaseModel):
    file: Path
    parser: Optional[ParserType] = None
    query: Optional[str] = None
    vars: Optional[Dict[str, str]] = None
    template: str
    strict_template: Optional[bool] = None

    @model_validator(mode="after")
    def validate_parser_and_query(self) -> "InjectItem":
        # Infer parser from extension if missing
        if not self.parser:
            ext = self.file.suffix.lower()
            inferred = EXTENSION_TO_PARSER.get(ext)
            if not inferred:
                raise ValueError(f"Cannot infer parser from file extension '{ext}'")
            self.parser = inferred

        # Validate query/vars presence
        if not self.query and not self.vars:
            raise ValueError("Either 'query' or 'vars' must be defined.")
        if self.query and self.vars:
            raise ValueError("Provide either 'query' or 'vars', not both.")

        return self
