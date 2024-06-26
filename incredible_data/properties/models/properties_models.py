from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TitleSlugDescriptionModel
from django_rubble.models.stamped_models import StampedModel
from django_rubble.utils import default_funcs
from djmoney.models.fields import MoneyField


class Utility(TitleSlugDescriptionModel):
    """All possible utilities for a property."""

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("admin:properties_utility_change", kwargs={"pk": self.pk})


class Property(StampedModel):
    address_line_1 = models.CharField(_("address 1"), max_length=50)
    address_line_2 = models.CharField(_("address 2"), max_length=50, blank=True)
    locality = models.CharField(_("city"), max_length=50)
    region = models.CharField(_("state"), max_length=50)
    postal_code = models.CharField(
        _("postal code"), help_text=_('aka "zip" code in the US'), max_length=10
    )


class UtilityBill(StampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    utility = models.ForeignKey(Utility, on_delete=models.PROTECT)
    billed_date = models.DateField(_("billed date"), default=default_funcs.django_today)
    due_date = models.DateField(_("due date"))
    past_due_amount = MoneyField(
        _("past due amount"),
        max_digits=10,
        decimal_places=2,
        default_currency="USD",
        default=0,
    )
    new_charges = MoneyField(
        _("new charges"), max_digits=10, decimal_places=2, default_currency="USD"
    )
    total_due = models.GeneratedField(
        _("total due"),
        F("past_due_amount") + F("new_charges"),
        output_field=MoneyField(),
    )


class Tenant(StampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    contact = models.ForeignKey("contacts.Contact", on_delete=models.PROTECT)
    move_in_date = models.DateField(
        _("move-in date"), default=default_funcs.django_today
    )
    move_out_date = models.DateField(_("move-out date"), blank=True, null=True)
    rent_due_date = models.PositiveSmallIntegerField(
        _("rent due date"), help_text=_("day of the month"), default=1
    )
    rent_amount = MoneyField(
        _("rent amount"), max_digits=10, decimal_places=2, default_currency="USD"
    )
