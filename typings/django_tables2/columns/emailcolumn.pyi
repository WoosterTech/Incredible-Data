from .base import library
from .linkcolumn import BaseLinkColumn

@library.register
class EmailColumn(BaseLinkColumn):
    def get_url(self, value):  # -> str:
        ...
    @classmethod
    def from_field(cls, field, **kwargs):  # -> Self | None:
        ...
