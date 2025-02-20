from pathlib import Path
from re import Pattern
from typing import TYPE_CHECKING, Annotated, Literal

from caseconverter import kebabcase
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ImportString,
    PlainSerializer,
    RootModel,
    StringConstraints,
)
from pydantic_settings import (
    BaseSettings,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

if TYPE_CHECKING:
    from pydantic_settings import PydanticBaseSettingsSource
import sys

import toml
from rich.theme import Theme

script_theme = Theme(
    {
        "linkish": "bright_magenta",
    }
)

# Define file paths
pyproject_path = Path("pyproject.toml")
ruff_path = Path("ruff.toml")

PathStr = Annotated[
    Path,
    PlainSerializer(lambda x: str(x.as_posix()), return_type=str, when_used="json"),
]

RuleSelector = Annotated[
    str, StringConstraints(min_length=1, pattern=r"^[A-Z][A-Z]*\d*$")
]

RuleList = Annotated[
    list[RuleSelector], PlainSerializer(lambda x: sorted(x), return_type=list)
]


class BaseConfig(BaseModel):
    model_config = ConfigDict(alias_generator=kebabcase, extra="forbid")


class AnalyzeConfig(BaseConfig):
    detect_string_imports: bool | None = None
    direction: Literal["dependents", "dependencies"] | None = None


class FormatConfig(BaseConfig):
    docstring_code_format: bool | None = None
    docstring_code_line_length: int | Literal["dynamic"] | None = None
    exclude: list[PathStr] | None = None
    indent_style: Literal["space", "tab"] | None = None
    line_ending: Literal["auto", "lf", "cr-lf", "native"] | None = None
    preview: bool | None = None
    quote_style: Literal["single", "double"] | None = None
    skip_magic_trailing_comma: bool | None = None


class LintExtendPerFileIgnoresConfig(RootModel[dict[PathStr, list[str]]]):
    pass


class LintPerFileIgnoresConfig(RootModel[dict[PathStr, list[str]]]):
    pass


class LintIsortConfig(BaseConfig):
    model_config = ConfigDict(extra="ignore")
    force_single_line: bool | None = None


class LintFlake8PytestStyleConfig(BaseConfig):
    fixture_parentheses: bool | None = None


class LintConfig(BaseConfig):
    model_config = ConfigDict(extra="ignore")
    allowed_confusables: list[str] | None = None
    dummy_variable_rgx: Pattern | None = None
    exclude: list[PathStr] | None = None
    explicit_preview_rules: bool | None = None
    extend_fixable: RuleList | None = None
    extend_ignore: (
        Annotated[RuleList, Field(deprecated="Interchangeable with `ignore`")] | None
    ) = None
    extend_per_file_ignores: LintExtendPerFileIgnoresConfig | None = None
    extend_safe_fixes: RuleList | None = None
    extend_select: RuleList | None = None
    extend_unsafe_fixes: RuleList | None = None
    external: RuleList | None = None
    fixable: Literal["ALL"] | RuleList | None = None
    ignore: RuleList | None = None
    ignore_init_module_imports: bool | None = None
    logger_objects: list[ImportString] | None = None
    per_file_ignores: LintExtendPerFileIgnoresConfig | None = None
    preview: bool | None = None
    select: RuleList | None = None
    task_tags: list[str] | None = None
    typing_modules: list[ImportString] | None = None
    unfixable: RuleList | None = None
    flake8_pytest_style: LintFlake8PytestStyleConfig | None = None
    isort: LintIsortConfig | None = None


class RuffConfig(BaseSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "ruff"),
        extra="ignore",
        alias_generator=kebabcase,
    )

    builtins: list[PathStr] | None = None
    cache_dir: PathStr | None = None
    exclude: list[PathStr] | None = None
    extend: PathStr | None = None
    extend_exclude: list[PathStr] | None = None
    extend_include: list[PathStr] | None = None
    fix: bool | None = None
    fix_only: bool | None = None
    force_exclude: bool | None = None
    include: list[PathStr] | None = None
    indent_width: int | None = None
    line_length: int | None = None
    namespace_packages: list[PathStr] | None = None
    output_format: str | None = None
    preview: bool | None = None
    required_version: str | None = None
    respect_gitignore: bool | None = None
    show_fixes: bool | None = None
    src: list[PathStr] | None = None
    target_version: str | None = None
    unsafe_fixes: bool | None = None
    analyze: AnalyzeConfig | None = None
    # TODO: Add more fields as needed
    format: FormatConfig | None = None
    lint: LintConfig | None = None

    def model_dump_toml(
        self, *, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ):
        as_dict = self.model_dump(
            mode="json", by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )
        return toml.dumps(as_dict)

    def write_file(self, file_path: Path = ruff_path):
        with file_path.open("w") as file:
            toml.dump(
                self.model_dump(mode="json", by_alias=True, exclude_none=True), file
            )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: "PydanticBaseSettingsSource",
        env_settings: "PydanticBaseSettingsSource",
        dotenv_settings: "PydanticBaseSettingsSource",
        file_secret_settings: "PydanticBaseSettingsSource",
    ) -> tuple["PydanticBaseSettingsSource", ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


if __name__ == "__main__":
    from rich.console import Console

    console = Console(theme=script_theme)

    if not pyproject_path.exists():
        console.print(f"[linkish]{pyproject_path.name}[/] not found!")
        sys.exit(1)

    ruff_config = RuffConfig()

    console.print(ruff_config.model_dump_toml())

    # ruff_config.write_file()  # noqa: ERA001
