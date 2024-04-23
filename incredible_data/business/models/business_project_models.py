from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from incredible_data.contacts.models.utility_models import BaseNumberedModel


class Project(BaseNumberedModel):
    name = models.CharField(_("project name"), max_length=50)
    customer = models.ForeignKey(
        "customers.Customer", verbose_name=_("customer"), on_delete=models.PROTECT
    )
    notes = models.TextField(_("notes"), blank=True)
    order = models.ForeignKey(
        "business.Order",
        verbose_name=_("order"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    slug = AutoSlugField(populate_from=["pk", "name"])
    number_config = {
        "prefix": "PJ",
        "width": 4,
        "start_value": 100,
    }

    def __str__(self) -> str:
        return f"{self.number} {self.name}"
