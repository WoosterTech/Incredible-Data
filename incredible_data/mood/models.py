from typing import TYPE_CHECKING, cast, final, override

from django.conf import settings
from django.db import models

from incredible_data.helpers.fields import RatingField

if TYPE_CHECKING:
    import datetime as dt

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.db.models.expressions import Combinable

    TextField = models.TextField[str, str]
    DateTimeField = models.DateTimeField[
        str | dt.datetime | dt.date | Combinable, dt.datetime
    ]
else:
    TextField = models.TextField
    DateTimeField = models.DateTimeField

AUTH_USER_MODEL = cast("str", settings.AUTH_USER_MODEL)

if TYPE_CHECKING:
    from incredible_data.users.models import User

    UserForeignKey = models.ForeignKey[AbstractBaseUser | Combinable, User]
else:
    UserForeignKey = models.ForeignKey


# Create your models here.
@final
class Mood(models.Model):
    """Log anxiety of the day with a 1-10 scale and optional notes."""

    timestamp = DateTimeField(
        auto_now_add=True, help_text="The date and time when the mood was recorded."
    )
    entered_by = UserForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT)

    anxiety = RatingField(scale_maximum=10)
    energy = RatingField(scale_maximum=10)

    notes = TextField(blank=True, help_text="Optional notes.")

    @final
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ["timestamp"]

    @override
    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.entered_by} - Anxiety: {self.anxiety}, Energy: {self.energy}"
