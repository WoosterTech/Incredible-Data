from .base import Column, library

class BaseLinkColumn(Column):
    def __init__(self, text=..., *args, **kwargs) -> None: ...
    def text_value(self, record, value):  # -> object:
        ...
    def value(self, record, value):  # -> object:
        ...
    def render(self, record, value):  # -> object:
        ...

@library.register
class LinkColumn(BaseLinkColumn):
    def __init__(
        self,
        viewname=...,
        urlconf=...,
        args=...,
        kwargs=...,
        current_app=...,
        attrs=...,
        **extra,
    ) -> None: ...

@library.register
class RelatedLinkColumn(LinkColumn): ...
