from typing import TYPE_CHECKING, Self, cast

from attrmagic import ClassBase
from django.conf import settings
from django.utils.version import get_version
from pydantic import Field

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class ProjectInfo(ClassBase):
    version: str
    commit_hash: str
    django_version: str = Field(default_factory=get_version)

    @property
    def build_number(self) -> str:
        return self.commit_hash

    @classmethod
    def from_settings(cls) -> Self:
        return cls(
            version=cast("str", settings.VERSION),
            commit_hash=cast("str", settings.BUILD_NUMBER),
        )

    @property
    def full_version(self) -> str:
        return f"{self.version}+{self.build_number}"


def version(_request: "HttpRequest"):
    return {"project": ProjectInfo.from_settings()}
