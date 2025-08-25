from collections.abc import Callable

from django.db.models import CharField

VALIDATORS_PER_FORMAT: dict[str, list[Callable]] = {}
DEFAULT_PER_FORMAT: dict[str, str] = {}

class ColorField(CharField):
    default_validators: list

    def formfield(self, **kwargs):  # -> Any:
        ...
    def contribute_to_class(self, cls, name, **kwargs):  # -> None:
        ...
    def deconstruct(self):  # -> tuple[Any, Any, Any, Any]:
        ...
    def validate(self, value, *args, **kwargs):  # -> None:
        ...
