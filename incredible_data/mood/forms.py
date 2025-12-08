import logging
from typing import Any, cast, final

from django import forms
from django.shortcuts import get_object_or_404

from .models import Entry, Metric, MetricType, today

logger = logging.getLogger(__name__)


@final
class MetricForm(forms.ModelForm):
    metric_type = forms.ModelChoiceField(
        queryset=MetricType.objects.all(),
        disabled=True,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args: Any, **kwargs: object):  # pyright: ignore[reportAny, reportExplicitAny]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportAny]
        # Store metric name for template display
        metric_type_raw = cast(
            "MetricType | int | None", self.initial.get("metric_type")
        )
        if metric_type_raw:
            if not isinstance(metric_type_raw, MetricType):
                metric_type = get_object_or_404(MetricType, id=metric_type_raw)
            else:
                metric_type = metric_type_raw

            self.metric_name = metric_type.name
            self.metric_help_text = metric_type.help_text

            # Generate choices from min_value to max_value
            choices = [
                (value, str(value))
                for value in range(metric_type.min_value, metric_type.max_value + 1)
            ]

            # Update score_value field to use Select widget with dynamic choices
            self.fields["score_value"] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={"class": "form-select"}),
                initial=metric_type.min_value
                + (metric_type.max_value - metric_type.min_value) // 2,
            )
        else:
            self.metric_name = "Unknown Metric"
            self.metric_help_text = ""

    @final
    class Meta:
        model = Metric
        fields = ["metric_type", "score_value"]


@final
class EntryForm(forms.ModelForm):
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "How are you feeling today?",
                "rows": 4,
                "style": "resize:vertical;",
            }
        )
    )
    effective_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), initial=today
    )
    time_of_day = forms.TypedChoiceField(
        choices=Entry.TimeOfDay.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_value=None,
        coerce=int,
        initial=Entry.TimeOfDay.get_current,
    )

    @final
    class Meta:
        model = Entry
        fields = ["notes", "effective_date", "time_of_day"]
