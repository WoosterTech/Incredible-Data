from typing import TYPE_CHECKING, cast, final, override

from django import forms
from django.contrib import admin
from django.http import HttpRequest

from incredible_data.mood import models as mood_models

# Register your models here.
if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser

    MoodModelAdmin = admin.ModelAdmin[mood_models.Mood]
    ModelForm = forms.ModelForm[mood_models.Mood]
else:
    MoodModelAdmin = admin.ModelAdmin
    ModelForm = forms.ModelForm


@final
@admin.register(mood_models.Mood)
class MoodAdmin(MoodModelAdmin):
    """Admin interface for the Mood model."""

    list_display = ("timestamp", "anxiety", "energy", "entered_by")
    search_fields = ("notes",)
    list_filter = ("entered_by",)
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp", "entered_by")
    date_hierarchy = "timestamp"

    fieldsets = (
        (None, {"fields": ("timestamp", "entered_by")}),
        (
            "Mood Ratings",
            {
                "fields": ("anxiety", "energy"),
                "description": "Rate your anxiety and energy levels on a scale of 1-10.",
            },
        ),
        (None, {"fields": ("notes",)}),
    )

    @override
    def save_model(
        self,
        request: HttpRequest,
        obj: mood_models.Mood,
        form: ModelForm,
        change: bool,
    ) -> None:
        assert request.user.is_authenticated, "User must be authenticated to save Mood."
        if not change:
            obj.entered_by = cast("AbstractBaseUser", request.user)
        super().save_model(request, obj, form, change)
