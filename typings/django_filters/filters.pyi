from typing import Any

from django import forms

from .fields import (
    BaseCSVField,
    BaseRangeField,
    ChoiceField,
    DateRangeField,
    DateTimeRangeField,
    IsoDateTimeField,
    IsoDateTimeRangeField,
    LookupChoiceField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    RangeField,
    TimeRangeField,
)

__all__ = [
    "AllValuesFilter",
    "AllValuesMultipleFilter",
    "BaseCSVFilter",
    "BaseInFilter",
    "BaseRangeFilter",
    "BooleanFilter",
    "CharFilter",
    "ChoiceFilter",
    "DateFilter",
    "DateFromToRangeFilter",
    "DateRangeFilter",
    "DateTimeFilter",
    "DateTimeFromToRangeFilter",
    "DurationFilter",
    "Filter",
    "IsoDateTimeFilter",
    "IsoDateTimeFromToRangeFilter",
    "LookupChoiceFilter",
    "ModelChoiceFilter",
    "ModelMultipleChoiceFilter",
    "MultipleChoiceFilter",
    "NumberFilter",
    "NumericRangeFilter",
    "OrderingFilter",
    "RangeFilter",
    "TimeFilter",
    "TimeRangeFilter",
    "TypedChoiceFilter",
    "TypedMultipleChoiceFilter",
    "UUIDFilter",
]

class Filter:
    creation_counter = ...
    field_class = forms.Field
    def __init__(
        self,
        field_name=...,
        lookup_expr=...,
        *,
        label=...,
        method=...,
        distinct=...,
        exclude=...,
        **kwargs,
    ) -> None: ...
    def get_method(self, qs): ...
    def method() -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        ...
    def label() -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        ...
    @property
    def field(self):  # -> field_class:
        ...
    def filter(self, qs, value): ...

class CharFilter(Filter):
    field_class = forms.CharField

class BooleanFilter(Filter):
    field_class = forms.NullBooleanField

class ChoiceFilter(Filter):
    field_class = ChoiceField
    def __init__(self, *args, **kwargs) -> None: ...
    def filter(self, qs, value): ...

class TypedChoiceFilter(Filter):
    field_class = forms.TypedChoiceField

class UUIDFilter(Filter):
    field_class = forms.UUIDField

class MultipleChoiceFilter(Filter):
    field_class = MultipleChoiceField
    always_filter = ...
    def __init__(self, *args, **kwargs) -> None: ...
    def is_noop(self, qs, value):  # -> bool:
        ...
    def filter(self, qs, value): ...
    def get_filter_predicate(self, v):  # -> dict[str | Any | None, Any]:
        ...

class TypedMultipleChoiceFilter(MultipleChoiceFilter):
    field_class = forms.TypedMultipleChoiceField

class DateFilter(Filter):
    field_class = forms.DateField

class DateTimeFilter(Filter):
    field_class = forms.DateTimeField

class IsoDateTimeFilter(DateTimeFilter):
    field_class = IsoDateTimeField

class TimeFilter(Filter):
    field_class = forms.TimeField

class DurationFilter(Filter):
    field_class = forms.DurationField

class QuerySetRequestMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    def get_request(self):  # -> None:
        ...
    def get_queryset(self, request):  # -> object | None:
        ...
    @property
    def field(self): ...

class ModelChoiceFilter(QuerySetRequestMixin, ChoiceFilter):
    field_class = ModelChoiceField
    def __init__(self, *args, **kwargs) -> None: ...

class ModelMultipleChoiceFilter(QuerySetRequestMixin, MultipleChoiceFilter):
    field_class = ModelMultipleChoiceField

class NumberFilter(Filter):
    field_class = forms.DecimalField
    def get_max_validator(self):  # -> MaxValueValidator:
        ...
    @property
    def field(self):  # -> field_class:
        ...

class NumericRangeFilter(Filter):
    field_class = RangeField
    def filter(self, qs, value): ...

class RangeFilter(Filter):
    field_class = RangeField
    def filter(self, qs, value): ...

class DateRangeFilter(ChoiceFilter):
    choices = ...
    filters = ...
    def __init__(self, choices=..., filters=..., *args, **kwargs) -> None: ...
    def filter(self, qs, value): ...

class DateFromToRangeFilter(RangeFilter):
    field_class = DateRangeField

class DateTimeFromToRangeFilter(RangeFilter):
    field_class = DateTimeRangeField

class IsoDateTimeFromToRangeFilter(RangeFilter):
    field_class = IsoDateTimeRangeField

class TimeRangeFilter(RangeFilter):
    field_class = TimeRangeField

class AllValuesFilter(ChoiceFilter):
    @property
    def field(self):  # -> field_class:
        ...

class AllValuesMultipleFilter(MultipleChoiceFilter):
    @property
    def field(self):  # -> field_class:
        ...

class BaseCSVFilter(Filter):
    base_field_class = BaseCSVField
    def __init__(self, *args, **kwargs) -> None: ...

class BaseInFilter(BaseCSVFilter):
    def __init__(self, *args, **kwargs) -> None: ...

class BaseRangeFilter(BaseCSVFilter):
    base_field_class = BaseRangeField
    def __init__(self, *args, **kwargs) -> None: ...

class LookupChoiceFilter(Filter):
    field_class = ...
    outer_class = LookupChoiceField
    def __init__(
        self, field_name=..., lookup_choices=..., field_class=..., **kwargs
    ) -> None: ...
    @classmethod
    def normalize_lookup(cls, lookup):  # -> tuple[str, str] | tuple[Any, Any]:
        ...
    def get_lookup_choices(self):  # -> list[tuple[str, str] | tuple[Any, Any]]:
        ...
    @property
    def field(self):  # -> outer_class:
        ...
    def filter(self, qs, lookup): ...

class OrderingFilter(BaseCSVFilter, ChoiceFilter):
    descending_fmt = ...
    def __init__(self, *args, **kwargs) -> None: ...
    def get_ordering_value(self, param): ...
    def filter(self, qs, value): ...
    @classmethod
    def normalize_fields(cls, fields):  # -> OrderedDict[Any, Any]:
        ...
    def build_choices(self, fields, labels):  # -> list[tuple[Any, Any]]:
        ...

class FilterMethod:
    def __init__(self, filter_instance) -> None: ...
    def __call__(self, qs, value):  # -> object:
        ...
    @property
    def method(self):  # -> Callable[..., object]:
        ...
