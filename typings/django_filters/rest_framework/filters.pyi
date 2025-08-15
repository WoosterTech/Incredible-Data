from django_filters import filters

from ..filters import *  # noqa: F403, TID252

__all__ = filters.__all__

class BooleanFilter(filters.BooleanFilter):
    def __init__(self, *args, **kwargs) -> None: ...
