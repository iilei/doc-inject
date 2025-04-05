import os
from glob import glob
from pathlib import Path
from typing import Annotated, Dict, Literal, Optional, Union

from pydantic import (
    BaseModel,
    PrivateAttr,
    RootModel,
    model_validator,
)
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

    _base_path: Optional[Path] = PrivateAttr(default=None)
    _resolved_files: list[Path] = PrivateAttr(default_factory=list)

    def set_base_path(self, base: Path):
        self._base_path = base.resolve()
        self._resolve_paths()

    def _resolve_paths(self):
        base_dir = Path(self._base_path) or Path.cwd()

        if self.glob:
            pattern = (base_dir / self.glob).as_posix()
            self._resolved_files = resolve_file_paths(pattern)

        if self.file:
            path = (base_dir / self.file).resolve()
            self._resolved_files = [path]

    @model_validator(mode="after")
    def validate_and_normalize(self) -> "InjectItem":
        if bool(self.file) == bool(self.glob):
            raise ValueError("Exactly one of 'file' or 'glob' must be provided.")

        if not self.query and not self.vars:
            raise ValueError("Either 'query' or 'vars' must be defined.")
        if self.query and self.vars:
            raise ValueError("Provide either 'query' or 'vars', not both.")

        self._base_path = os.getcwd()
        self._resolve_paths()

        ext = f".{([*[x.as_posix() for x in self._resolved_files], ''][0]).rpartition('.')[-1].lower()}"

        if not self.parser:
            inferred = EXTENSION_TO_PARSER.get(ext)
            if not inferred:
                raise ValueError(f"Cannot infer parser from file extension '{ext}'")
            self.parser = inferred

        return self


class InjectConfig(RootModel[Dict[str, InjectItem]]):
    def get_items(self) -> Dict[str, InjectItem]:
        return self.root

    def with_base_path(self, path: Path) -> "InjectConfig":
        for item in self.root.values():
            item.set_base_path(path)
        return self
