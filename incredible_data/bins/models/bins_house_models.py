from datetime import date, timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from incredible_data.contacts.models.utility_models import UserStampedModel


class JournalEntry(TimeStampedModel, UserStampedModel):
    optional_asset = models.ForeignKey(
        "bins.Asset",
        verbose_name=_("asset"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    title = models.CharField(_("short title"), max_length=100)
    performed = models.DateField(_("performed"), default=date.today)
    next_due_date = models.DateField(
        _("next due date"), default=date.today + timedelta(days=30)
    )

    class EntryType(models.TextChoices):
        BROKEN = "BROKEN", _("broken")
        SCHEDULED = "SCHEDULED", _("scheduled")
        DEMAND = "DEMAND", _("on demand")

    entry_type = models.CharField(
        _("entry type"), max_length=25, choices=EntryType, default=EntryType.SCHEDULED
    )

    notes = models.TextField(_("notes"))
    slug = AutoSlugField(populate_from=["title", "performed", "id"])

    def __str__(self) -> str:
        return f"{self.title} (type: {self.entry_type}, date: {self.performed})"
