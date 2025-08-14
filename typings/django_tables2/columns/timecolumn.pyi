from .base import library
from .templatecolumn import TemplateColumn

@library.register
class TimeColumn(TemplateColumn):
    def __init__(self, format=..., *args, **kwargs) -> None: ...  # noqa: A002
    @classmethod
    def from_field(cls, field, **kwargs):  # -> Self | None:
        ...
