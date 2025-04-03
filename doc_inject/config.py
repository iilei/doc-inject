from pathlib import Path
from typing import Dict, Literal, Optional

from pydantic import BaseModel, model_validator

ParserType = Literal["json", "yaml", "toml", "text"]

EXTENSION_TO_PARSER = {
    ".json": "json",
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

    @model_validator(mode="after")
    def validate_parser_and_query(self) -> "InjectItem":
        # Infer parser
        if not self.parser:
            ext = self.file.suffix.lower()
            if ext in EXTENSION_TO_PARSER:
                self.parser = EXTENSION_TO_PARSER[ext]
            else:
                raise ValueError(
                    f"Cannot infer parser from file extension '{ext}' — set 'parser' explicitly."
                )

        if not self.vars and not self.query:
            raise ValueError("Either 'vars' or 'query' must be defined.")
        if self.vars and self.query:
            raise ValueError("Provide either 'query' or 'vars', not both.")

        return self
