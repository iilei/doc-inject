from glob import glob
from pathlib import Path
from typing import Dict, Literal, Optional

from pydantic import BaseModel, RootModel, model_validator


def resolve_file_paths(file_pattern: str) -> list[Path]:
    return [Path(p) for p in glob(file_pattern, recursive=True)]


ParserType = Literal["json", "yaml", "toml", "text"]

EXTENSION_TO_PARSER = {
    ".json": "json",
    ".json5": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".txt": "text",
    ".md": "text",
    ".html": "text",
    ".j2": "text",
    ".jinja2": "text",
}


class InjectItem(BaseModel):
    file: Path
    parser: Optional[ParserType] = None
    query: Optional[str] = None
    vars: Optional[Dict[str, str]] = None
    template: str
    strict_template: Optional[bool] = None

    @model_validator(mode="after")
    def validate_and_infer(self) -> "InjectItem":
        # Infer parser from file extension
        if not self.parser:
            ext = self.file.suffix.lower()
            inferred = EXTENSION_TO_PARSER.get(ext)
            if not inferred:
                raise ValueError(f"Cannot infer parser from file extension '{ext}'")
            self.parser = inferred

        if not self.query and not self.vars:
            raise ValueError("Either 'query' or 'vars' must be defined.")

        if self.query and self.vars:
            raise ValueError("Provide either 'query' or 'vars', not both.")

        return self


class InjectConfig(RootModel[Dict[str, InjectItem]]):
    def get_items(self) -> Dict[str, InjectItem]:
        return self.root
