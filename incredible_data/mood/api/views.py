import logging
from typing import TYPE_CHECKING, Generic, TypeVar, final

from django.db import models
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from incredible_data.mood.api.filters import MetricTypeFilter
from incredible_data.mood.models import MetricType

from .serializers import (
    Choices,
    MetricTypeChoicesSerializer,
    MetricTypeSerializer,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from rest_framework.request import Request


_MT_co = TypeVar("_MT_co", bound=models.Model, covariant=True)

if TYPE_CHECKING:

    class GenericReadOnlyModelViewSet(
        viewsets.ReadOnlyModelViewSet[_MT_co], Generic[_MT_co]
    ):
        pass
else:

    class GenericReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet, Generic[_MT_co]):
        pass


@final
class MetricTypeViewSet(GenericReadOnlyModelViewSet[MetricType]):  # pyright: ignore[reportUninitializedInstanceVariable]
    queryset = MetricType.objects.all()
    serializer_class = MetricTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = MetricTypeFilter

    @action(detail=True, methods=["get"])
    def choices(self, _request: "Request", pk: int | None = None) -> Response:  # pyright: ignore[reportUnusedParameter]
        """
        Get choices for the metric type.
        """
        metric_type = self.get_object()
        choices = Choices.model_validate(metric_type.get_choices())
        ser = MetricTypeChoicesSerializer(data=choices.model_dump(), many=True)
        if not ser.is_valid(raise_exception=True):
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(ser.data, status=status.HTTP_200_OK)
