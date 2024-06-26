from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Count, F, Max, Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from django_rubble.models.stamped_models import StampedModel
from djmoney.models.fields import MoneyField
from model_utils.choices import Choices
from model_utils.models import StatusModel
from slugify import slugify

from incredible_data.contacts.models.utility_models import (
    BaseNumberedModel,
    NumberConfig,
    NumberedModel,
)


def fourteen_days() -> date:
    return timezone.now() + timedelta(days=14)


def thirty_days() -> date:
    return timezone.now() + timedelta(days=30)


class Order(BaseNumberedModel):
    customer = models.ForeignKey(
        "customers.Customer",
        verbose_name=_("customer"),
        on_delete=models.PROTECT,
    )
    expected_date = models.DateField(
        _("expected completion date"),
        default=fourteen_days,
    )
    notes = models.TextField(_("order notes"), blank=True)
    slug = AutoSlugField(populate_from=["customer", "number"])
    number_config = NumberConfig(prefix="MHC", width=4, start_value=1)

    def __str__(self) -> str:
        return f"{self.number} - {self.customer}"


class Invoice(StampedModel, StatusModel, NumberedModel):
    number_config = NumberConfig(prefix="INV-", width=4, start_value=10)
    STATUS = Choices(
        ("draft", _("Draft")),
        ("stimate", _("Estimate")),
        ("invoiced", _("Invoiced")),
        ("paid", _("Paid")),
    )
    customer = models.ForeignKey(
        "customers.Customer", verbose_name=_("customer"), on_delete=models.PROTECT
    )
    terms = models.TextField(_("terms"), blank=True)
    notes = models.TextField(_("notes"), blank=True)
    subtotal = MoneyField(_("subtotal"), max_digits=19, decimal_places=4, default=0)
    grand_total = MoneyField(
        _("grand total"), max_digits=19, decimal_places=4, default=0
    )
    due_date = models.DateField(_("due date"), default=thirty_days)
    order = models.ForeignKey(
        Order, verbose_name=_("order"), on_delete=models.PROTECT, blank=True, null=True
    )

    slug = AutoSlugField(populate_from="number", slugify_function=slugify)

    def __str__(self):
        return f"{self.customer} - {self.number}"

    def update_totals(self) -> None:
        total = self.get_subtotal()
        kwargs = {"subtotal": total, "grand_total": total}
        self.__class__.objects.filter(pk=self.pk).update(**kwargs)

    def get_subtotal(self) -> Decimal:
        return self.invoiceline_set.aggregate(
            subtotal=Sum(F("quantity") * F("unit_price"))
        )["subtotal"]

    def normalize_rank(self) -> None:
        qs: models.QuerySet[InvoiceLine]
        qs = self.invoiceline_set.order_by("rank")
        result = qs.aggregate(Count("rank"), Max("rank"))

        count, max_rank = result["rank__count"], result["rank__max"]

        if count in (max_rank, 0):
            return

        # shift all ranks outside current range to prevent uniqueness errors

        qs.update(rank=F("rank") + int(max_rank))

        # rewrite ranks starting at 1
        for (
            idx,
            line,
        ) in enumerate(qs):
            line.rank = idx + 1
        qs.bulk_update(qs, ["rank"])

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"slug": self.slug})


class InvoiceLine(models.Model):
    rank = models.PositiveSmallIntegerField(_("rank"))
    description = models.CharField(_("description"), max_length=100)
    quantity = models.DecimalField(
        _("quantity"), max_digits=15, decimal_places=5, default=1
    )
    unit_price = MoneyField(_("unit price"), max_digits=19, decimal_places=4, default=0)
    invoice = models.ForeignKey(
        Invoice, verbose_name=_("invoice"), on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.description}|{self.invoice.number} - Line {self.rank}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.rank = self.get_next_rank()
        super().save(*args, **kwargs)

        self.invoice.update_totals()

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        deleted = super().delete(*args, **kwargs)

        self.invoice.normalize_rank()

        return deleted

    def get_next_rank(self) -> int:
        results = self.objects.filter(invoice=self.invoice).aggregate(Max("rank"))

        return results["rank__max"] + 1 if results["rank__max"] is not None else 1

    @property
    def extended_price(self):
        return self.quantity * self.unit_price

    @property
    def line_number(self):
        return self.rank
