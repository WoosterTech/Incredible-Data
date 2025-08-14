from .base import library
from .linkcolumn import BaseLinkColumn

@library.register
class URLColumn(BaseLinkColumn):
    def get_url(self, value): ...
    @classmethod
    def from_field(cls, field, **kwargs):  # -> Self | None:
        ...
