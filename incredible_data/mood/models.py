from typing import TYPE_CHECKING, TypeAlias, cast, final, override

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

# from incredible_data.helpers.fields import RatingField

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

    # anxiety = RatingField(scale_maximum=10)
    # energy = RatingField(scale_maximum=10)

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
    is_score = models.BooleanField(default=True)

    @override
    def __str__(self) -> str:
        return self.name


@final
class Entry(models.Model):
    created_by: "UserForeignKey" = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False
    )
    created_on = models.DateTimeField(auto_now_add=True)

    @override
    def __str__(self) -> str:
        return f"Entry by {self.created_by} on {self.created_on}"


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
        return f"Metric for {self.entry} - {self.metric_type}: {self.score_value}"
