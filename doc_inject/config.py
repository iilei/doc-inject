from glob import glob
from pathlib import Path
from typing import Annotated, Dict, Literal, Optional, Union

from pydantic import BaseModel, RootModel, model_validator
from pydantic.types import StringConstraints

NonBlankStr = Annotated[str, StringConstraints(min_length=1)]


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
    file: Optional[Union[NonBlankStr, Path]] = None
    glob: Optional[NonBlankStr] = None
    parser: Optional[ParserType] = None
    query: Optional[NonBlankStr] = None
    vars: Optional[Dict[str, NonBlankStr]] = None
    template: NonBlankStr
    strict_template: Optional[bool] = None

    @model_validator(mode="after")
    def validate_and_normalize(self) -> "InjectItem":
        if bool(self.file) == bool(self.glob):
            raise ValueError("Exactly one of 'file' or 'glob' must be provided.")

        if not self.query and not self.vars:
            raise ValueError("Either 'query' or 'vars' must be defined.")
        if self.query and self.vars:
            raise ValueError("Provide either 'query' or 'vars', not both.")

        sample_path = Path(self.file) if self.file else Path(self.glob)
        ext = sample_path.suffix.lower()
        if not self.parser:
            inferred = EXTENSION_TO_PARSER.get(ext)
            if not inferred:
                raise ValueError(f"Cannot infer parser from file extension '{ext}'")
            self.parser = inferred

        if self.glob:
            self._resolved_files = resolve_file_paths(self.glob)

        if self.file:
            self._resolved_files = [Path(self.file)]

        return self


class InjectConfig(RootModel[Dict[str, InjectItem]]):
    def get_items(self) -> Dict[str, InjectItem]:
        return self.root
