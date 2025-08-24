import logging
from typing import TYPE_CHECKING, Any, final, override

from django.contrib import admin

from incredible_data.helpers.admin import (
    GenericModelAdmin,
    GenericTabularInline,
    UserStampedAdmin,
)
from incredible_data.mood import models as mood_models

if TYPE_CHECKING:
    from django.db import models
    from django.forms.models import BaseInlineFormSet
    from django.http.request import HttpRequest

logger = logging.getLogger(__name__)


@final
class MoodAdmin(UserStampedAdmin[mood_models.Mood]):
    """Admin interface for the Mood model."""

    list_display = ("timestamp", "entered_by")
    search_fields = ("notes",)
    list_filter = ("entered_by",)
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp", "entered_by")
    date_hierarchy = "timestamp"

    fieldsets = (
        (None, {"fields": ("timestamp", "entered_by")}),
        (None, {"fields": ("notes",)}),
    )
    created_by_field = "entered_by"

    


@final
@admin.register(mood_models.MetricType)
class MetricTypeAdmin(GenericModelAdmin[mood_models.MetricType]):
    """Admin interface for the MetricType model."""

    list_display = ("name", "is_score", "graph_color")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_score",)


@final
class MetricInline(GenericTabularInline[mood_models.Metric]):
    model = mood_models.Metric
    extra = 0

    @override
    def get_extra(
        self,
        request: "HttpRequest",
        obj: mood_models.Metric | None = None,
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> int:
        if obj is not None:
            return super().get_extra(request, obj, **kwargs)
        return self.model.objects.all().count()

    @override
    def get_formset(
        self,
        request: "HttpRequest",
        obj: mood_models.Metric | None = None,
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> "type[BaseInlineFormSet]":
        return super().get_formset(request, obj, **kwargs)


@final
@admin.register(mood_models.Entry)
class EntryAdmin(UserStampedAdmin[mood_models.Entry]):
    list_display = ("created_by", "effective_date", "time_of_day", "value_display")
    search_fields = ("notes",)
    list_filter = ("created_by", "time_of_day")
    date_hierarchy = "effective_date"
    ordering = ("-effective_date",)
    inlines = [MetricInline]
    readonly_fields = ("created_by", "created_on")
    fieldsets = (
        (None, {"fields": ("effective_date", "time_of_day", "notes")}),
        (
            "Details",
            {"fields": (("created_by", "created_on"),), "classes": ("collapse",)},
        ),
    )

    @override
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

@final
@admin.register(mood_models.Metric)
class MetricAdmin(GenericModelAdmin[mood_models.Metric]):
    list_display = (
        "entry__created_by",
        "entry__effective_date",
        "metric_type",
        "score_value",
    )
    search_fields = ("entry__created_by__first_name", "metric_type__name")
    list_filter = ("metric_type",)
    ordering = (
        "entry__created_by",
        "-entry__effective_date",
    )

    @override
    def get_queryset(
        self, request: "HttpRequest"
    ) -> "models.QuerySet[mood_models.Metric]":
        qs = super().get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs

        return qs.filter(entry__created_by=user)
