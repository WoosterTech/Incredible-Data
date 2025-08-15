from typing import Any

from django.db.models.fields import Field
from django.db.models.fields.reverse_related import ForeignObjectRel
from django_filters import filterset
from django_filters.filters import Filter

FILTER_FOR_DBFIELD_DEFAULTS: dict[type[Field[Any]], Filter] = ...

class FilterSet(filterset.FilterSet):
    FILTER_DEFAULTS: dict[type[ForeignObjectRel], dict[str, type[Filter]]] = ...
    @property
    def form(self):  # -> _:
        ...
