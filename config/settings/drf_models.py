from typing import ClassVar

from attrmagic import ClassBase, SimpleListRoot
from pydantic import AnyUrl, ConfigDict

from .settings_models import SettingsModel


class DRFBase(SettingsModel):
    model_config: ConfigDict = ConfigDict(alias_generator=lambda s: s.upper())  # pyright: ignore[reportIncompatibleVariableOverride]


class Server(ClassBase):
    url: AnyUrl
    description: str | None = None


class Servers(SimpleListRoot[Server]): ...


class Spectacular(DRFBase):
    name: ClassVar[str] = "SPECTACULAR_SETTINGS"
    title: str
    description: str
    version: str
    serve_permissions: list[str]
    servers: Servers = Servers(root=[])
