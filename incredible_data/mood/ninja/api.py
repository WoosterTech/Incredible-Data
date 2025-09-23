# pyright: reportUnusedParameter=false


import logging
from enum import StrEnum
from typing import TYPE_CHECKING

from django.db.models import Prefetch, Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.router import Router

from incredible_data.helpers.dates import TimeRangeChoice, get_dates
from incredible_data.mood.models import Entry, Metric, MetricType
from incredible_data.mood.ninja.filters import EntryFilters, TrendFilters
from incredible_data.mood.ninja.schemas import (
    EntryOut,
    MetricDatasetOut,
    MetricOut,
    MetricTypeOut,
    TrendOut,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)

router = Router(tags=["mood"])

DEFAULT_QUERY = Query(...)  # pyright: ignore[reportCallIssue, reportUnknownVariableType]


@router.get("/metric-types/{metric_type_id}", response=MetricTypeOut)
def get_metric_type(request: "HttpRequest", metric_type_id: int):
    return get_object_or_404(MetricType, id=metric_type_id)


@router.get("/metric-types", response=list[MetricTypeOut])
def list_metric_types(request: "HttpRequest"):
    return MetricType.objects.all()


@router.get("/metrics", response=list[MetricOut])
def list_metrics(request: "HttpRequest"):
    return Metric.objects.all()


class EntryOrderField(StrEnum):
    CREATED_AT = "created_at"
    CREATED_AT_DESC = "-created_at"
    EFFECTIVE_DATE = "effective_date"
    EFFECTIVE_DATE_DESC = "-effective_date"


@router.get("/entries", response=list[EntryOut])
def list_entries(
    request: "HttpRequest",
    filters: EntryFilters = DEFAULT_QUERY,
    order_by: EntryOrderField | None = None,
):
    q = Q(created_by=request.user)
    logger.debug("Filtering entries with: %s", filters.model_dump(exclude_none=True))
    q &= filters.get_filter_expression()

    qs = Entry.objects.filter(q)
    if order_by:
        qs = qs.order_by(order_by.value)
    return qs


@router.get("/trends/{metric_type_id}", response=list[MetricDatasetOut], by_alias=True)
def metric_trend(request: "HttpRequest", metric_type_id: int):
    qs = Metric.objects.order_by("entry__effective_date")
    q = Q(entry__created_by=request.user)
    q &= Q(metric_type_id=metric_type_id)
    return qs.filter(q)


class TrendOrderField(StrEnum):
    NAME = "name"
    NAME_DESC = "-name"


@router.get("/trends", response=list[TrendOut], by_alias=True)
def list_trends(
    request: "HttpRequest",
    filters: EntryFilters = DEFAULT_QUERY,
    trend_filters: TrendFilters = DEFAULT_QUERY,
    order_by: TrendOrderField | None = None,
    reverse_chronological: bool = False,  # noqa: FBT001, FBT002
):
    logger.debug("Filtering trends with: %s", filters.model_dump(exclude_none=True))
    entries = Entry.objects.all()
    q = Q(created_by=request.user)
    q &= filters.get_filter_expression()
    entries = entries.filter(q)

    filtered_metrics = Metric.objects.filter(entry__in=entries)

    if not reverse_chronological:
        filtered_metrics = filtered_metrics.order_by("entry__effective_date")
    else:
        filtered_metrics = filtered_metrics.order_by("-entry__effective_date")

    qs = MetricType.objects.all()
    trend_q = trend_filters.get_filter_expression()
    qs = qs.filter(trend_q)

    qs = qs.prefetch_related(Prefetch("metric_set", queryset=filtered_metrics))

    if order_by is TrendOrderField.NAME or order_by is TrendOrderField.NAME_DESC:
        qs = qs.order_by(order_by.value)

    return qs


@router.get("/period_choices")
def period_choices(request: "HttpRequest") -> "HttpResponse":
    options = '<option value="">-- Select Period --</option>'
    for value, label in TimeRangeChoice:
        if value != "custom":  # Don't show custom as an option
            options += f'<option value="{value}">{label}</option>'

    return HttpResponse(options)


@router.post("/update_dates")
def update_dates(request: "HttpRequest", period: TimeRangeChoice | None = None):
    if not period:
        return HttpResponse("")

    start_date, end_date = get_dates(period)

    return HttpResponse(f"""
        <label>Start:
        <input type="date" id="startDate" name="start" value="{start_date}"
               hx-trigger="change" hx-post="/api/v2/mood/clear_period" hx-target="#period">
        </label>
        <label>End:
        <input type="date" id="endDate" name="end" value="{end_date}"
               hx-trigger="change" hx-post="/api/v2/mood/clear_period" hx-target="#period">
        </label>
    """)


@router.post("/clear_period")
def clear_period(request: "HttpRequest"):
    options = '<option value="" selected>-- Custom Date Range --</option>'
    for value, label in TimeRangeChoice.choices:
        if value != "custom":
            options += f'<option value="{value}">{label}</option>'

    return HttpResponse(options)
