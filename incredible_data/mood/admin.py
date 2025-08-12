import logging
from typing import final

from django.contrib import admin

from incredible_data.helpers.admin import (
    GenericModelAdmin,
    GenericTabularInline,
    UserStampedAdmin,
)
from incredible_data.mood import models as mood_models

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

    list_display = ("name", "is_score")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_score",)


@final
class MetricInline(GenericTabularInline[mood_models.Metric]):
    model = mood_models.Metric
    extra = 2


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
