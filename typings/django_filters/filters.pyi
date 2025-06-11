from collections.abc import Callable
from typing import Any, Generic, TypeVar

from django.db import models
from django.forms import Field
from django.utils.functional import Promise

_ModelT = TypeVar("_ModelT", bound=models.Model)

class Filter(Generic[_ModelT]):
    creation_counter: int = 0
    field_class: type[Field]

    field_name: str | None
    lookup_expr: str
    label: str | Promise | None
    method: (
        Callable[[models.QuerySet[_ModelT], str, Any], models.QuerySet[_ModelT]]  # pyright: ignore[reportExplicitAny]
        | str
        | None
    )
    distinct: bool = False
    exclude: bool = False
    extra: dict[str, Any] = {"required": False}  # pyright: ignore[reportExplicitAny]

    def __init__(
        self,
        field_name: str | None = None,
        lookup_expr: str | None = None,
        *,
        label: str | Promise | None = None,
        method: Callable[[models.QuerySet[_ModelT], str, Any], models.QuerySet[_ModelT]]  # pyright: ignore[reportExplicitAny]
        | str
        | None = None,
        distinct: bool = False,
        exclude: bool = False,
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> None: ...
