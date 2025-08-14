from .base import Column, library

@library.register
class ManyToManyColumn(Column):
    def __init__(
        self,
        transform=...,
        filter=...,  # noqa: A002
        separator=...,
        linkify_item=...,
        *args,
        **kwargs,
    ) -> None: ...
    def transform(self, obj): ...
    def filter(self, qs): ...
    def render(self, value):  # -> SafeString:
        ...
    @classmethod
    def from_field(cls, field, **kwargs):  # -> Self | None:
        ...
