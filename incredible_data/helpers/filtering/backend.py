import logging
from typing import TYPE_CHECKING, TypeVar, override

from django.db.models import Model
from rest_framework import filters, serializers
from rest_framework.serializers import BaseSerializer

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import APIView

logger = logging.getLogger(__name__)

_ModelT = TypeVar("_ModelT", bound=Model)


class SerializerFilterBackend(filters.BaseFilterBackend):
    serializer_class: type[serializers.BaseSerializer] | None = None

    def get_filter_serializer(
        self, request: "Request", view: "APIView"
    ) -> BaseSerializer:
        logger.debug("Creating filter serializer with data: %s", request.query_params)
        serializer_class = self.serializer_class or view.filter_serializer_class
        return serializer_class(data=request.query_params)

    @override
    def filter_queryset(
        self, request: "Request", queryset: "QuerySet[_ModelT]", view: "APIView"
    ) -> "QuerySet[_ModelT]":
        logger.debug("Filtering queryset with params: %s", view.request.query_params)
        serializer = self.get_filter_serializer(request, view)
        _ = serializer.is_valid(raise_exception=True)
        view.filter_data = serializer.validated_data

        return queryset
