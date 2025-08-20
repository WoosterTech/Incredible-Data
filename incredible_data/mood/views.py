import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from incredible_data.mood.api.serializers import (
    ChartSerializer,
)

from .models import Entry

if TYPE_CHECKING:
    import datetime as dt

    from rest_framework.request import Request

logger = logging.getLogger(__name__)


def rating_widget(request: HttpRequest) -> HttpResponse:
    query_dict = request.GET
    name = query_dict.get("name")
    value = int(query_dict.get("value", 0))
    max_rating = int(query_dict.get("max_rating", 5))
    emoji = query_dict.get("emoji", "⭐")
    ratings = list(range(1, max_rating + 1))
    html_context = {
        "hx_get_url": reverse("mood:rating_widget"),
        "name": name,
        "value": value,
        "ratings": ratings,
        "emoji": emoji,
    }
    widget_html = render_to_string("mood/rating_widget.html", html_context)
    script = f"<script>document.getElementById('id_{name}').value = {value};</script>"
    return HttpResponse(
        mark_safe(  # noqa: S308
            f'<div id="{name}-stars" class="star-rating">{widget_html}</div>{script}'
        )
    )


@api_view(["GET"])
def user_metric_chart(request: "Request") -> Response:
    entry_qs = (
        Entry.objects.filter(created_by=request.user)
        .order_by("created_on")
        .prefetch_related("metric_set")
    )

    labels: list[dt.date] = list(entry_qs.values_list("effective_date", flat=True))

    metrics_dict: dict[str, list[dict[str, dt.date | int]]] = defaultdict(list)

    for entry in entry_qs:
        for metric in entry.metric_set.all():
            metrics_dict[metric.metric_type.name].append(
                {
                    "date": entry.effective_date,
                    "value": metric.score_value,
                }
            )

    ser = ChartSerializer({"labels": labels, "metrics": metrics_dict})

    return Response(ser.data, status=status.HTTP_200_OK)  # pyright: ignore[reportAny]
