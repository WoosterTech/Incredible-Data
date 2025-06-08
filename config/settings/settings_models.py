import abc
from enum import StrEnum
from typing import Annotated, ClassVar

from attrmagic import ClassBase, SimpleDict
from pydantic import Field


class SettingsModel(ClassBase, abc.ABC):
    name: ClassVar[str]

    def render(
        self, *, by_alias: bool = True, exclude_none: bool = True
    ) -> dict[str, int | bool | dict[str, dict[str, str]] | dict[str, str | list[str]]]:
        """
        Render the settings to a format suitable for Django's LOGGING configuration.
        """
        return self.model_dump(by_alias=by_alias, exclude_none=exclude_none)


class Levels(StrEnum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Formatter(ClassBase):
    format: str


class Formatters(SimpleDict[str, Formatter]):
    pass


class Handler(ClassBase):
    level: Levels = Levels.DEBUG
    class_name: Annotated[str, Field(alias="class")]
    formatter: str


class Handlers(SimpleDict[str, Handler]):
    pass


class RootLogger(ClassBase):
    level: Levels = Levels.INFO
    handlers: list[str]


class Logging(SettingsModel):
    name: ClassVar[str] = "LOGGING"
    version: int = 1
    disable_existing_loggers: bool
    formatters: Formatters
    handlers: Handlers
    root: RootLogger


if __name__ == "__main__":
    # This block is for testing purposes only
    from rich import print as rprint

    logging_example = Logging(
        disable_existing_loggers=False,
        formatters=Formatters(
            root={
                "example_formatter": Formatter(
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            },
        ),
        handlers=Handlers(
            root={
                "console": Handler(
                    level=Levels.DEBUG,
                    class_name="logging.StreamHandler",
                    formatter="example_formatter",
                )
            }
        ),
        root=RootLogger(level=Levels.INFO, handlers=["console"]),
    )
    rprint(logging_example.model_dump(by_alias=True))

    logging_example.handlers["console"].level = Levels.ERROR
