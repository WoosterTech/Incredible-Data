import logging
from typing import Generic, TypeVar, final, override

from django.db import models
from django.shortcuts import get_object_or_404
from django.urls.converters import IntConverter

from incredible_data.mood.models import Entry

logger = logging.getLogger(__name__)

_ModelT = TypeVar("_ModelT", bound=models.Model)


class ModelIdConverter(Generic[_ModelT]):
    model: type[_ModelT]
    regex: str = IntConverter.regex

    def __init__(self, model: type[_ModelT]) -> None:
        self.model = model
        super().__init__()

    def to_python(self, value: str | int) -> _ModelT:
        value_int = int(value)
        try:
            instance = self.model.objects.get(id=value_int)
        except self.model.DoesNotExist:
            msg = f"{self.model.__name__} with id {value_int} does not exist."
            raise ValueError(msg) from None
        return instance

    def to_url(self, value: _ModelT | int) -> str:
        if isinstance(value, models.Model):
            return str(value.id)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
        return str(value)


@final
class EntryIdConverter(ModelIdConverter[Entry]):
    regex: str = IntConverter.regex
    model = Entry

    @override
    def to_python(self, value: str | int) -> Entry:
        return get_object_or_404(Entry, id=int(value))

    @override
    def to_url(self, value: Entry | int) -> str:
        if isinstance(value, Entry):
            logger.debug("Entry.id type: %s", type(value.id))
            return str(value.id)
        return str(value)
