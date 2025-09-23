import abc
import datetime as dt
import enum
import logging
from collections.abc import Callable
from decimal import Decimal
from enum import auto as autoenum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Generic,
    Protocol,
    TypeVar,
    cast,
    final,
    override,
)

from attrmagic import ClassBase, SimpleDict, SimpleListRoot
from caseconverter.camel import camelcase
from django.db import models
from pydantic import AliasChoices, AliasGenerator, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_extra_types.color import Color
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from incredible_data.helpers.filtering.backend import SerializerFilterBackend
from incredible_data.mood.api.filters import (
    ChartFilter,
    EntryFilter,
    MetricFilter,
    MetricTypeFilter,
)
from incredible_data.mood.models import Entry, Metric, MetricType

from .serializers import (
    ChartSerializer,
    Choices,
    EntrySerializer,
    MetricSerializer,
    MetricTypeChoicesSerializer,
    MetricTypeSerializer,
)

logger = logging.getLogger(__name__)


_MT_co = TypeVar("_MT_co", bound=models.Model, covariant=True)

if TYPE_CHECKING:
    from datetime import date

    from rest_framework.request import Request

    class GenericReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet, Generic[_MT_co]):
        pass

    class GenericModelViewSet(viewsets.ModelViewSet, Generic[_MT_co]):
        pass
else:

    class GenericReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet, Generic[_MT_co]):
        pass

    class GenericModelViewSet(viewsets.ModelViewSet, Generic[_MT_co]):
        pass


class ViewSetProtocol(Protocol):
    request: "Request"
    get_serializer: Callable[..., serializers.Serializer]


class ExpandableFieldsMixin:
    def get_serializer(
        self: ViewSetProtocol,
        *args: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> serializers.Serializer:
        expand = self.request.query_params.getlist("expand")
        kwargs.setdefault("expand", expand)
        return super().get_serializer(*args, **kwargs)


@final
class MetricTypeViewSet(GenericReadOnlyModelViewSet[MetricType]):
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = MetricTypeFilter

    @action(detail=True, methods=["get"])
    def choices(self, _request: "Request", pk: int | None = None) -> Response:  # pyright: ignore[reportUnusedParameter]
        """
        Get choices for the metric type.
        """
        metric_type = cast("MetricType", self.get_object())
        choices = Choices.model_validate(metric_type.get_choices())
        ser = MetricTypeChoicesSerializer(data=choices.model_dump(), many=True)
        if not ser.is_valid(raise_exception=True):
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)  # pyright: ignore[reportAny]
        return Response(ser.data, status=status.HTTP_200_OK)  # pyright: ignore[reportAny]


@final
class EntryViewSet(GenericModelViewSet[Entry]):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = EntryFilter

    @override
    def get_queryset(self) -> "models.QuerySet[Entry]":
        qs = cast("models.QuerySet[Entry]", super().get_queryset())

        return qs.filter(created_by=self.request.user)


@final
class MetricViewSet(GenericModelViewSet[Metric]):
    queryset = Metric.objects.all().prefetch_related("entry", "metric_type")
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = MetricFilter

    @override
    def get_queryset(self) -> "models.QuerySet[Metric]":
        qs = cast("models.QuerySet[Metric]", super().get_queryset())

        # Filter metrics by the user who created the entry
        return qs.filter(entry__created_by=self.request.user)


class ChartType(enum.StrEnum):
    @override
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        """
        Return the camel-case version of the enum name.
        """
        return camelcase(name)

    LINE = autoenum()
    BAR = autoenum()
    PIE = autoenum()
    DOUGHNUT = autoenum()
    RADAR = autoenum()
    POLAR_AREA = autoenum()
    HORIZONTAL_BAR = autoenum()
    MIXED = "bar"
    BUBBLE = autoenum()


class Position(enum.StrEnum):
    TOP = "top"
    LEFT = "left"
    BOTTOM = "bottom"
    RIGHT = "right"


def create_alias_choices(field_name: str) -> AliasChoices:
    return AliasChoices(field_name, to_camel(field_name))


class General(ClassBase, abc.ABC):
    model_config: ConfigDict = ConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        alias_generator=AliasGenerator(
            validation_alias=lambda x: create_alias_choices(x),
            serialization_alias=lambda x: to_camel(x),
        )
    )


class Title(General):
    text: str = "My Chart"
    display: bool = True
    position: Position = Position.TOP
    padding: int = 10


class Legend(General):
    display: bool = True
    position: Position = Position.TOP
    full_width: bool = True
    reverse: bool = False
    labels: str = "default"


class MetricData(General):
    date: dt.date
    value: int
    time_of_day: Entry.TimeOfDay | None


class MetricDataRoot(SimpleListRoot[MetricData]):
    pass


class DataSet(General):
    label: str | None = None
    border_color: Color = Color((0, 0, 0, 0.1))
    border_cap_style: str = "butt"
    background_color: Color = Color((0, 0, 0, 0.1))
    border_dash: list[int] = []
    border_dash_offset: float = 0.0
    data: MetricDataRoot
    fill: bool | None = None
    tension: Decimal = Decimal("0")


class DataSets(SimpleListRoot[DataSet]):
    pass


class Data(General):
    datasets: DataSets
    labels: list[str] | None = None


class Plugins(SimpleDict[str, Legend | Title]):
    pass


class Options(General):
    responsive: bool = True
    maintain_aspect_ratio: bool = True
    aspect_ratio: Decimal = Decimal("2")
    on_resize: Callable[..., None] | None = None
    resize_delay: Annotated[
        int, Field(description="Delay in milliseconds before resizing")
    ] = 0
    plugins: Plugins = Plugins(root={})


class BaseChart(ClassBase):
    type: ChartType = ChartType.LINE
    data: Data
    options: Options | None = None


@final
class ChartAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartSerializer
    # filter_backends = [SerializerFilterBackend]
    # filter_serializer_class = ChartFilter
    queryset = Entry.objects.all()
    filterset_class = ChartFilter

    # def get_metric_type_queryset(self) -> "models.QuerySet[MetricType]":

    @override
    def get(self, request: "Request", _format: str | None = None):
        entry_qs = (
            self.get_queryset().order_by("created_on").prefetch_related("metric_set")
        )

        labels = entry_qs.values_list("effective_date", flat=True)

        metric_types = MetricType.objects.all()

        datasets = DataSets(root=[])

        for metric in metric_types:
            metric_entries = entry_qs.filter(metric__metric_type=metric).order_by(
                "effective_date"
            )
            if not metric_entries.exists():
                continue

            data = MetricDataRoot.model_validate(
                [
                    {
                        "date": entry.effective_date,
                        "value": entry.metric_set.get(metric_type=metric).score_value,
                        "time_of_day": entry.time_of_day,
                    }
                    for entry in metric_entries
                ]
            )

            datasets.append(
                DataSet(
                    label=metric.name,
                    border_color=Color(metric.graph_color),
                    fill=False,
                    tension=Decimal("0.1"),
                    data=data,
                )
            )

        logger.debug("Datasets prepared for chart: %s", datasets)

        ser = ChartSerializer(
            {
                "title": "Metrics Overview",
                "labels": labels,
                "datasets": datasets,
            }
        )

        return Response(ser.data, status=status.HTTP_200_OK)  # pyright: ignore[reportAny]

    @override
    def get_queryset(self) -> "models.QuerySet[Entry]":
        qs = cast("models.QuerySet[Entry]", super().get_queryset())
        return (
            qs.filter(created_by=self.request.user)
            .prefetch_related("metric_set")
            .order_by("created_on")
        )

    @override
    def list(self, request: "Request", *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        logger.debug("Final query: %s", queryset.query)

        page = self.paginate_queryset(queryset)
        is_paginated = page is not None

        queryset = page if is_paginated else queryset

        serializer = self.get_serializer(queryset, many=True)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
