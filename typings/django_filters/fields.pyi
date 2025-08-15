from typing import Any, NamedTuple

from django import forms
from django.utils.choices import BaseChoiceIterator

from .widgets import BaseCSVWidget, CSVWidget, DateRangeWidget, RangeWidget

DJANGO_50: bool = True

class RangeField(forms.MultiValueField):
    widget = RangeWidget
    def __init__(self, fields=..., *args, **kwargs) -> None: ...
    def compress(self, data_list):  # -> slice[Any, Any, Any] | None:
        ...

class DateRangeField(RangeField):
    widget = DateRangeWidget
    def __init__(self, *args, **kwargs) -> None: ...
    def compress(
        self, data_list
    ):  # -> slice[datetime | Any, datetime | Any, Any] | None:
        ...

class DateTimeRangeField(RangeField):
    widget = DateRangeWidget
    def __init__(self, *args, **kwargs) -> None: ...

class IsoDateTimeRangeField(RangeField):
    widget = DateRangeWidget
    def __init__(self, *args, **kwargs) -> None: ...

class TimeRangeField(RangeField):
    widget = DateRangeWidget
    def __init__(self, *args, **kwargs) -> None: ...

class Lookup(NamedTuple):
    value: Any  # pyright: ignore[reportExplicitAny]
    lookup_expr: str

    def __new__(cls, value, lookup_expr):  # -> Self:
        ...

class LookupChoiceField(forms.MultiValueField):
    default_error_messages = ...
    def __init__(self, field, lookup_choices, *args, **kwargs) -> None: ...
    def compress(self, data_list):  # -> Lookup | None:
        ...

class IsoDateTimeField(forms.DateTimeField):
    ISO_8601 = ...
    input_formats = ...
    def strptime(self, value, format):  # -> datetime | Any:  # noqa: A002
        ...

class BaseCSVField(forms.Field):
    base_widget_class = BaseCSVWidget
    def __init__(self, *args, **kwargs) -> None: ...
    def clean(self, value):  # -> list[Any] | None:
        ...

class BaseRangeField(BaseCSVField):
    widget = CSVWidget
    default_error_messages = ...
    def clean(self, value):  # -> list[Any] | None:
        ...

class ChoiceIterator(BaseChoiceIterator if DJANGO_50 else object):
    def __init__(self, field, choices) -> None: ...
    def __iter__(
        self,
    ):  # -> Generator[tuple[Literal[''], Any] | tuple[Any, Any] | Any, Any, None]:
        ...
    def __len__(self):  # -> int:
        ...

class ModelChoiceIterator(forms.models.ModelChoiceIterator):
    def __iter__(
        self,
    ):  # -> Generator[tuple[int | str, str] | tuple[Any, Any], Any, None]:
        ...
    def __len__(self):  # -> int:
        ...

class ChoiceIteratorMixin:
    def __init__(self, *args, **kwargs) -> None: ...
    @property
    def choices(self): ...
    @choices.setter
    def choices(self, value):  # -> None:
        ...

class ChoiceField(ChoiceIteratorMixin, forms.ChoiceField):
    iterator = ChoiceIterator
    def __init__(self, *args, **kwargs) -> None: ...

class MultipleChoiceField(ChoiceIteratorMixin, forms.MultipleChoiceField):
    iterator = ChoiceIterator
    def __init__(self, *args, **kwargs) -> None: ...

class ModelChoiceField(ChoiceIteratorMixin, forms.ModelChoiceField):
    iterator = ...
    def to_python(self, value):  # -> Any | None:
        ...

class ModelMultipleChoiceField(ChoiceIteratorMixin, forms.ModelMultipleChoiceField):
    iterator = ...
