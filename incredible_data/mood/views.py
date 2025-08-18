import abc
import datetime as dt
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Annotated, cast

from caseconverter.camel import camelcase
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from pydantic import BaseModel, ConfigDict, RootModel, computed_field, model_serializer
from pydantic_extra_types.color import Color

from .models import Entry, Metric

if TYPE_CHECKING:
    from incredible_data.mood.manager import UserScopedManager

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


class ChartJSBase(BaseModel, abc.ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    model_config: ConfigDict = ConfigDict(alias_generator=lambda s: camelcase(s))  # pyright: ignore[reportIncompatibleVariableOverride]


class MetricChartDataPoint(BaseModel):
    date: dt.date
    value: int


class Dataset(ChartJSBase):
    label: str
    data: list[MetricChartDataPoint] = []
    border_color: Color | None = None
    background_color: Color | None = None


class ChartData(BaseModel):
    datasets: dict[str, list[MetricChartDataPoint]]

    _dates: set[dt.date] = set()

    def populate_dates(self) -> None:
        for values in self.datasets.values():
            for point in values:
                self._dates.add(point.date)

    def get_dates(self, *, force: bool = False) -> set[dt.date]:
        if not self._dates or force:
            self.populate_dates()
        return self._dates

    @computed_field
    @property
    def labels(self) -> list[str]:
        sorted_dates = sorted(self.get_dates(force=True))
        return list(map(str, sorted_dates))


@login_required
def user_metric_chart(request: HttpRequest) -> HttpResponse:
    manager = cast("UserScopedManager[Entry]", Entry.objects)
    entries = manager.fetch_user_records(request).order_by("created_on")
    metrics = Metric.objects.filter(entry__in=entries).select_related(
        "metric_type", "entry"
    )

    metric_data: defaultdict[str, list[MetricChartDataPoint]] = defaultdict(list)
    for metric in metrics:
        mtype = metric.metric_type.name
        metric_data[mtype].append(
            MetricChartDataPoint(
                date=metric.entry.effective_date, value=metric.score_value
            )
        )
    chart_data = ChartData(datasets=metric_data)
    return render(
        request,
        "mood/user_metric_chart.html",
        {"chart_data": chart_data.model_dump(mode="json", exclude_none=True)},
    )
