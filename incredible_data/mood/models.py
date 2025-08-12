import datetime as dt
from typing import TYPE_CHECKING, TypeAlias, cast, final, override

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from incredible_data.users.models import User

    UserForeignKey: TypeAlias = "models.ForeignKey[User]"

AUTH_USER_MODEL = cast("str", settings.AUTH_USER_MODEL)


# Create your models here.
@final
class Mood(models.Model):
    """Log anxiety of the day with a 1-10 scale and optional notes."""

    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="The date and time when the mood was recorded."
    )
    entered_by: "UserForeignKey" = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.PROTECT
    )

    notes = models.TextField(blank=True, help_text="Optional notes.")

    @final
    class Meta:
        ordering = ["timestamp"]

    @override
    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.entered_by}"  # - Anxiety: {self.anxiety}, Energy: {self.energy}"


@final
class MetricType(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    help_text = models.TextField(_("help text"), blank=True)
    is_score = models.BooleanField(default=True)
    higher_is_better = models.BooleanField(
        default=True,
        help_text="Indicates if a higher score is better (True) or a lower score is better (False).",
    )

    @override
    def __str__(self) -> str:
        return self.name


@final
class Entry(models.Model):
    created_by: "UserForeignKey" = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False
    )
    created_on = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional notes.")
    effective_date = models.DateField(
        default=dt.date.today,
        help_text="The date this entry is effective for.",
    )

    class TimeOfDay(models.IntegerChoices):
        MORNING = 1, _("Morning")
        AFTERNOON = 2, _("Afternoon")
        EVENING = 3, _("Evening")

        __empty__ = _("Unspecified")

    time_of_day = models.IntegerField(
        choices=TimeOfDay.choices, default=None, null=True, blank=True
    )

    if TYPE_CHECKING:
        metric_set: "models.QuerySet[Metric]"  # pyright: ignore[reportUninitializedInstanceVariable]

    @final
    class Meta:
        ordering = ["-created_on"]
        verbose_name_plural = "Entries"

    @override
    def __str__(self) -> str:
        return f"Entry by {self.created_by} on {self.effective_date}"

    @admin.display(description=_("Metric Values"))
    def value_display(self) -> str:
        metric_strs = [
            f"{metric.metric_type.name}: {metric.score_value}"
            for metric in self.metric_set.all()
        ]
        if not metric_strs:
            return ""
        return ", ".join(metric_strs)


@final
class Metric(models.Model):
    metric_type = models.ForeignKey(MetricType, on_delete=models.PROTECT)
    entry = models.ForeignKey(Entry, on_delete=models.PROTECT)
    score_value = models.PositiveSmallIntegerField()

    @final
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entry", "metric_type"], name="unique_entry_metric"
            )
        ]

    @override
    def __str__(self) -> str:
        return f"{self.metric_type.name}({self.score_value})"
