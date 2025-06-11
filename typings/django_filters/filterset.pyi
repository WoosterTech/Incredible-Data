from collections import OrderedDict
from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from django.db import models
from django.db.models import Field
from django.forms import Form
from django.forms.utils import ErrorDict
from django.http import HttpRequest, QueryDict
from django_filters.filters import Filter

_ModelT = TypeVar("_ModelT", bound=models.Model)

class BaseFilterSet(Generic[_ModelT]):
    FILTER_DEFAULTS: dict[type[Field[type, type]], dict[str, Filter[_ModelT]]]

    is_bound: bool = False
    data: dict[str, Any] | QueryDict  # pyright: ignore[reportExplicitAny]
    queryset: models.QuerySet[_ModelT] | None = None
    request: HttpRequest | None = None
    form_prefix: str | None = None
    filters: list[tuple[Any, Any]]  # pyright: ignore[reportExplicitAny]

    def is_valid(self) -> bool: ...
    @property
    def errors(self) -> ErrorDict: ...
    def filter_queryset(
        self, queryset: models.QuerySet[_ModelT]
    ) -> models.QuerySet[_ModelT]: ...
    @property
    def qs(self) -> models.QuerySet[_ModelT]: ...
    def get_form_class(self) -> type[Form]: ...
    @property
    def form(self) -> Form: ...
    @classmethod
    def get_fields(cls) -> OrderedDict[str, Iterable[str]]: ...
    @classmethod
    def get_filter_name(cls, field_name: str, lookup_expr: str) -> str: ...
    @classmethod
    def get_filters(cls) -> OrderedDict[str, Filter[_ModelT]]: ...

class FilterSet(BaseFilterSet[_ModelT], Generic[_ModelT]): ...
