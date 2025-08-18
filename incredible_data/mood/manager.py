from typing import TYPE_CHECKING, Generic, TypeVar, override

from django.db import models

_ModelT = TypeVar("_ModelT", bound=models.Model)

if TYPE_CHECKING:
    from django.http import HttpRequest

    class GenericManager(models.Manager[_ModelT], Generic[_ModelT]):
        pass

else:

    class GenericManager(models.Manager, Generic[_ModelT]):
        pass


class UserScopedManager(GenericManager[_ModelT], Generic[_ModelT]):
    @override
    def __init__(self, field_name: str = "created_by") -> None:
        super().__init__()

        self.field_name: str = field_name

    def fetch_user_records(self, request: "HttpRequest") -> "models.QuerySet[_ModelT]":
        user = request.user
        return self.filter(**{self.field_name: user})
