import logging
from collections import defaultdict
from typing import TYPE_CHECKING, cast

from django import forms
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from incredible_data.mood.api.serializers import (
    ChartSerializer,
)
from incredible_data.mood.forms import EntryForm, MetricForm

from .models import Entry, Metric, MetricType

if TYPE_CHECKING:
    import datetime as dt

    from rest_framework.request import Request

    from incredible_data.users.models import User

logger = logging.getLogger(__name__)


def rating_widget(request: "HttpRequest") -> "HttpResponse":
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


@login_required
@permission_required("mood.add_entry", raise_exception=True)
def mood_entry(request: "HttpRequest") -> "HttpResponse":
    user = cast("User", request.user)

    active_metrics = MetricType.objects.active_for_user(user)

    formset_initial = [{"metric_type": metric} for metric in active_metrics]

    logger.debug("Initial formset_initial: %s", formset_initial)

    # Create a formset with extra set to the number of active metrics
    MetricFormSet = forms.inlineformset_factory(  # noqa: N806
        Entry,
        Metric,
        form=MetricForm,
        extra=len(active_metrics),
        can_delete=False,
    )

    if request.method == "POST":
        form = EntryForm(request.POST)
        formset = MetricFormSet(request.POST, initial=formset_initial)

        if form.is_valid() and formset.is_valid():
            entry_instance = cast("Entry", form.save(commit=False))
            entry_instance.created_by = user
            entry_instance.save()

            formset.instance = entry_instance
            formset.save()

            return redirect(entry_instance.get_absolute_url())
    else:
        form = EntryForm()
        formset = MetricFormSet(initial=formset_initial)

        logger.debug("Initialized MetricFormSet with %d forms", len(formset.forms))

    return render(
        request,
        "mood/mood_entry.html",
        {
            "user": user,
            "form": form,
            "formset": formset,
        },
    )


@login_required
@permission_required("mood.view_entry", raise_exception=True)
def mood_entry_detail(request: "HttpRequest", entry: Entry) -> "HttpResponse":
    return render(
        request,
        "mood/mood_entry_detail.html",
        {
            "entry": entry,
            "metrics": entry.metric_set.all(),
        },
    )
