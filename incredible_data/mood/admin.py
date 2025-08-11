from typing import TYPE_CHECKING, cast, final, override

from django import forms
from django.contrib import admin
from django.http import HttpRequest

from incredible_data.helpers.admin import UserStampedAdmin
from incredible_data.mood import models as mood_models

if TYPE_CHECKING:
    from incredible_data.users.models import User

    MoodModelAdmin = admin.ModelAdmin[mood_models.Mood]
else:
    MoodModelAdmin = admin.ModelAdmin


@final
class MoodAdmin(MoodModelAdmin):
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

    @override
    def save_model(
        self,
        request: HttpRequest,
        obj: mood_models.Mood,
        form: forms.ModelForm,
        change: bool,
    ) -> None:
        assert request.user.is_authenticated, "User must be authenticated to save Mood."
        if not change:
            obj.entered_by = cast("User", request.user)
        super().save_model(request, obj, form, change)


if TYPE_CHECKING:
    MetricTypeModelAdmin = admin.ModelAdmin[mood_models.MetricType]
else:
    MetricTypeModelAdmin = admin.ModelAdmin


@final
@admin.register(mood_models.MetricType)
class MetricTypeAdmin(MetricTypeModelAdmin):
    """Admin interface for the MetricType model."""

    list_display = ("name", "is_score")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_score",)


if TYPE_CHECKING:
    MetricTabularInline = admin.TabularInline[mood_models.Metric]
else:
    MetricTabularInline = admin.TabularInline


@final
class MetricInline(MetricTabularInline):
    model = mood_models.Metric
    extra = 2


@final
@admin.register(mood_models.Entry)
class EntryAdmin(UserStampedAdmin[mood_models.Entry]):
    list_display = ("created_by", "effective_date", "value_display")
    search_fields = ("notes",)
    list_filter = ("created_by",)
    date_hierarchy = "effective_date"
    ordering = ("-effective_date",)
    inlines = [MetricInline]
    readonly_fields = ("created_by", "created_on")
    fieldsets = (
        (None, {"fields": ("effective_date", "notes")}),
        (
            "Details",
            {"fields": (("created_by", "created_on"),), "classes": ("collapse",)},
        ),
    )


if TYPE_CHECKING:
    MetricModelAdmin = admin.ModelAdmin[mood_models.Metric]
else:
    MetricModelAdmin = admin.ModelAdmin


@final
@admin.register(mood_models.Metric)
class MetricAdmin(MetricModelAdmin):
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
