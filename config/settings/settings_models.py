import abc
from enum import StrEnum
from typing import Annotated, Any, ClassVar

from attrmagic import ClassBase, SimpleDict
from attrmagic.sentinels import MISSING, Missing
from pydantic import ConfigDict, Field, SecretStr, model_serializer


def serialize_missing(self: ClassBase) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
    return {
        k: v
        for k, v in self.model_dump(by_alias=True).items()  # pyright: ignore[reportAny]
        if v is not MISSING
    }


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


class BuiltInEngine(StrEnum):
    POSTGRESQL = "django.db.backends.postgresql"
    MYSQL = "django.db.backends.mysql"
    SQLITE = "django.db.backends.sqlite3"
    ORACLE = "django.db.backends.oracle"


class TestDatabase(ClassBase):
    model_config: ConfigDict = ConfigDict(alias_generator=lambda s: s.upper())  # pyright: ignore[reportIncompatibleVariableOverride]
    name: str | Missing = MISSING
    charset: str | Missing = MISSING
    collation: str | Missing = MISSING
    migrate: bool | Missing = MISSING
    mirror: str | Missing = MISSING
    template: str | Missing = MISSING
    create_db: bool | Missing = MISSING
    create_user: bool | Missing = MISSING
    user: str | Missing = MISSING
    password: SecretStr | Missing = MISSING

    @model_serializer
    def serialize_missing(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        return serialize_missing(self)


class DatabaseOptions(ClassBase):
    engine: ClassVar[BuiltInEngine | str]


class Database(ClassBase):
    model_config: ConfigDict = ConfigDict(alias_generator=lambda s: s.upper())  # pyright: ignore[reportIncompatibleVariableOverride]
    atomic_requests: bool | Missing = MISSING
    autocommit: bool | Missing = MISSING
    engine: BuiltInEngine | str | Missing = MISSING
    host: str | Missing = MISSING
    name: str | Missing = MISSING
    conn_max_age: int | None | Missing = MISSING
    conn_health_checks: bool | Missing = MISSING
    options: DatabaseOptions | Missing = MISSING
    password: SecretStr | Missing = MISSING
    port: Annotated[int | Missing, Field(ge=0, le=65535)] = MISSING
    time_zone: str | Missing = MISSING
    disable_server_side_cursors: bool | Missing = MISSING
    user: str | Missing = MISSING
    test: TestDatabase | Missing = MISSING

    @model_serializer
    def serialize_missing(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        output: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
        cls = self.__class__
        for key, value in self:  # pyright: ignore[reportAny]
            if (value_mut := value) is MISSING:  # pyright: ignore[reportAny]
                continue
            key_alias = cls.model_fields[key].alias or key
            if isinstance(value, SecretStr):
                value_mut = value.get_secret_value()
            output[key_alias] = value_mut

        return output


class Databases(SimpleDict[str, Database]):
    def render(self) -> dict[str, dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
        """
        Render the databases to a format suitable for Django's DATABASES setting.
        """
        return {db_name: db.model_dump(by_alias=True) for db_name, db in self.items()}


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
