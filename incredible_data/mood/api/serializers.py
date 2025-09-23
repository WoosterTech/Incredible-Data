import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Generic, TypeVar, final, override

from django.db import models
from pydantic import BaseModel, RootModel, model_validator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from incredible_data.mood.models import Entry, Metric, MetricType
from incredible_data.users.api.serializers import UserSerializer

logger = logging.getLogger(__name__)

_IN = TypeVar("_IN")
_MT = TypeVar("_MT", bound=models.Model)

if TYPE_CHECKING:
    from rest_framework.utils.serializer_helpers import BindingDict

    class GenericSerializer(serializers.Serializer[_IN], Generic[_IN]):
        pass

    class GenericModelSerializer(serializers.ModelSerializer[_MT], Generic[_MT]):
        pass

    class GenericHyperlinkedModelSerializer(
        serializers.HyperlinkedModelSerializer[_MT], Generic[_MT]
    ):
        pass
else:

    class GenericSerializer(serializers.Serializer, Generic[_IN]):
        pass

    class GenericModelSerializer(serializers.ModelSerializer, Generic[_MT]):
        pass

    class GenericHyperlinkedModelSerializer(
        serializers.HyperlinkedModelSerializer, Generic[_MT]
    ):
        pass


class ExpandableFieldsMixin:
    class Meta:
        abstract: bool = True
        expandable: Sequence[str] = []

    def __init__(
        self,
        *args: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        expand: Sequence[str] | None = None,
        **kwargs: str | Any,  # pyright: ignore[reportExplicitAny]
    ) -> None:
        super().__init__(*args, **kwargs)

        expand = expand if expand is not None else []

        # raise an exception if any of expand not in Meta.expandable
        invalid_fields = [
            field for field in expand if field not in self.Meta.expandable
        ]
        if invalid_fields:
            msg = f"Invalid fields for expansion: {invalid_fields}"
            raise ValueError(msg)

        if TYPE_CHECKING:
            self.fields: BindingDict

        for field in set(self.Meta.expandable) - set(expand):
            _ = self.fields.pop(field, None)


@final
class MetricTypeSerializer(GenericModelSerializer[MetricType]):
    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = MetricType
        fields = (
            "id",
            "name",
            "help_text",
            "is_score",
            "higher_is_better",
            "min_value",
            "max_value",
            "scale_definition",
            "graph_color",
        )


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
    def is_valid(self, *, raise_exception: bool = False):  # pyright: ignore[reportIncompatibleMethodOverride]
        assert hasattr(self, "initial_data"), (
            "Cannot call `.is_valid()` as no `data=` keyword argument was "
            "passed when instantiating the serializer instance."
        )

        if not hasattr(self, "_validated_data"):
            try:
                self._validated_data = self.run_validation(self.initial_data)  # pyright: ignore[reportAny, reportUninitializedInstanceVariable]
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}  # pyright: ignore[reportUninitializedInstanceVariable]

        logger.debug("Validation errors found: %s", self._errors)

        if self._errors and raise_exception:
            raise ValidationError(self.errors)  # pyright: ignore[reportAny]

        return not bool(self._errors)


@final
class MetricSerializer(ExpandableFieldsMixin, GenericModelSerializer[Metric]):  # pyright: ignore[reportUnsafeMultipleInheritance]
    metric_type = MetricTypeSerializer(read_only=True)
    effective_date = serializers.DateField(
        source="entry.effective_date", read_only=True
    )

    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Metric
        fields = (
            "id",
            "metric_type_id",
            "metric_type",
            "entry_id",
            "score_value",
            "effective_date",
        )
        expandable = ["metric_type"]


@final
class EntrySerializer(ExpandableFieldsMixin, GenericModelSerializer[Entry]):  # pyright: ignore[reportUnsafeMultipleInheritance]
    metric_set = MetricSerializer(many=True, required=False)
    created_by_id = serializers.IntegerField(required=True)
    created_by = UserSerializer()

    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Entry
        fields = (
            "id",
            "effective_date",
            "time_of_day",
            "created_by_id",
            "created_by",
            "metric_set",
        )
        expandable = ["metric_set", "created_by"]


@final
class DataSerializer(serializers.Serializer):
    date = serializers.DateField()
    value = serializers.IntegerField()
    time_of_day = serializers.ChoiceField(choices=Entry.TimeOfDay.choices)


@final
class DatasetSerializer(serializers.Serializer):
    label = serializers.CharField()
    borderColor = serializers.CharField(source="border_color")  # noqa: N815
    data_list = DataSerializer(source="data", many=True)
    fill = serializers.BooleanField(default=True)
    tension = serializers.FloatField(default=0.1)

    @override
    def to_representation(self, instance: dict[str, Any]) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        logger.debug("Serializing dataset: %s", instance)
        rep = super().to_representation(instance)  # pyright: ignore[reportAny]
        rep["data"] = rep.pop("data_list", [])  # pyright: ignore[reportAny]
        return rep  # pyright: ignore[reportAny]


@final
class ChartSerializer(serializers.Serializer):
    type = serializers.CharField(default="line")
    title = serializers.CharField(default="Basic Chart")
    labels = serializers.ListField(child=serializers.DateField())
    datasets = DatasetSerializer(many=True)

    # djangorestframework-stubs does not match package, is missing "*"
    @override
    def is_valid(self, *, raise_exception: bool = False) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
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

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)
