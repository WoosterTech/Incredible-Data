import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar, final, override

from django.db import models
from pydantic import BaseModel, RootModel, model_validator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from incredible_data.mood.models import MetricType

logger = logging.getLogger(__name__)

_IN = TypeVar("_IN")
_MT = TypeVar("_MT", bound=models.Model)

if TYPE_CHECKING:

    class GenericSerializer(serializers.Serializer[_IN], Generic[_IN]):
        pass

    class GenericModelSerializer(serializers.ModelSerializer[_MT], Generic[_MT]):
        pass
else:

    class GenericSerializer(serializers.Serializer, Generic[_IN]):
        pass

    class GenericModelSerializer(serializers.ModelSerializer, Generic[_MT]):
        pass


@final
class MetricTypeSerializer(GenericModelSerializer[MetricType]):
    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = MetricType
        fields = ("id", "name")


class Choice(BaseModel):
    id: int
    label: str | None

    @model_validator(mode="before")
    @classmethod
    def from_tuple(cls, data: Any) -> Any:  # pyright: ignore[reportAny,reportExplicitAny]
        if isinstance(data, tuple) and len(data) == 2:  # pyright: ignore[reportUnknownArgumentType]  # noqa: PLR2004
            return {"id": data[0], "label": data[1]}  # pyright: ignore[reportUnknownVariableType]
        return data  # pyright: ignore[reportUnknownVariableType]


class Choices(RootModel[list[Choice]]):
    pass


@final
class MetricTypeChoicesSerializer(GenericSerializer[Choice]):
    id = serializers.IntegerField(required=True)
    label = serializers.CharField(required=False)

    @override
    def is_valid(self, *, raise_exception: bool = False):
        assert hasattr(self, "initial_data"), (
            "Cannot call `.is_valid()` as no `data=` keyword argument was "
            "passed when instantiating the serializer instance."
        )

        if not hasattr(self, "_validated_data"):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        logger.debug("Validation errors found: %s", self._errors)

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)
