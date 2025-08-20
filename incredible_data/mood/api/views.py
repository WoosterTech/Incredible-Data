import logging
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
    cast,
    final,
    override,
)

from django.db import models
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from incredible_data.mood.api.filters import EntryFilter, MetricFilter, MetricTypeFilter
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


@final
class ChartAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChartSerializer

    # def get_metric_type_queryset(self) -> "models.QuerySet[MetricType]":

    def get(self, request: "Request", _format: str | None = None):
        entry_qs = (
            Entry.objects.filter(created_by=request.user)
            .order_by("created_on")
            .prefetch_related("metric_set")
        )

        labels = entry_qs.values_list("effective_date", flat=True)

        metric_types = MetricType.objects.all()

        datasets: list[dict[str, str | bool | float | list[dict[str, date | int]]]] = []

        for metric in metric_types:
            metric_entries = entry_qs.filter(metric__metric_type=metric)
            if not metric_entries.exists():
                continue

            data = [
                {
                    "date": entry.effective_date,
                    "value": entry.metric_set.get(metric_type=metric).score_value,
                }
                for entry in metric_entries
            ]

            dataset: dict[str, str | bool | float | list[dict[str, date | int]]] = {
                "label": metric.name,
                "border_color": metric.graph_color,
                "fill": False,
                "tension": 0.1,
                "data_list": data,
            }
            datasets.append(dataset)

        logger.debug("Datasets prepared for chart: %s", datasets)

        ser = ChartSerializer(
            {
                "title": "Metrics Overview",
                "labels": labels,
                "datasets": datasets,
            }
        )

        return Response(ser.data, status=status.HTTP_200_OK)  # pyright: ignore[reportAny]
