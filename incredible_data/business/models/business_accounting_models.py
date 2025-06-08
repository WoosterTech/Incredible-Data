# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportIncompatibleVariableOverride=false
import contextlib
import logging
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any, cast, final, override

from django.db import models, transaction
from django.db.models import BaseConstraint, Count, F, Max, Sum, UniqueConstraint
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from django_rubble.models.stamped_models import (  # pyright: ignore[reportMissingTypeStubs]
    StampedModel,
)
from djmoney.models.fields import MoneyField
from model_utils.choices import Choices
from model_utils.models import StatusModel
from slugify import slugify

from incredible_data.contacts.models.utility_models import (
    BaseNumberedModel,
    NumberConfig,
    NumberedModel,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fourteen_days() -> date:
    return timezone.now() + timedelta(days=14)


def thirty_days() -> date:
    return timezone.now() + timedelta(days=30)


@final
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

    @override
    def __str__(self) -> str:
        return f"{self.number} - {self.customer}"

    def get_absolute_url(self):
        return reverse("order-detail", kwargs={"slug": self.slug})


@final
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

    if TYPE_CHECKING:

        @property
        def invoiceline_set(self) -> models.QuerySet["InvoiceLine"]:
            return self.invoiceline_set

    @override
    def __str__(self):
        return f"{self.customer} - {self.number}"

    def update_totals(self) -> None:
        """Aggregates the invoice lines and updates the totals."""
        total = self.get_subtotal()
        kwargs = {"subtotal": total, "grand_total": total}
        _ = self.__class__.objects.filter(pk=self.pk).update(**kwargs)  # pyright: ignore[reportAny]

    def get_subtotal(self) -> Decimal:
        aggregated = self.invoiceline_set.aggregate(
            subtotal=Sum(F("quantity") * F("unit_price"))
        )

        return Decimal(aggregated["subtotal"])  # pyright: ignore[reportAny]

    def normalize_rank(self) -> None:
        qs: models.QuerySet[InvoiceLine]
        qs = self.invoiceline_set.order_by("rank")
        result = qs.aggregate(Count("rank"), Max("rank"))

        count, max_rank = result["rank__count"], result["rank__max"]  # pyright: ignore[reportAny]

        if count in (max_rank, 0):
            return

        # shift all ranks outside current range to prevent uniqueness errors

        _ = qs.update(rank=F("rank") + int(max_rank))  # pyright: ignore[reportAny]

        # rewrite ranks starting at 1
        for (
            idx,
            line,
        ) in enumerate(qs):
            line.rank = idx + 1
        _ = qs.bulk_update(qs, ["rank"])

    def max_rank(self) -> int:
        """
        Returns the maximum rank of the invoice lines.
        If there are no lines, returns 0.
        """
        result = self.invoiceline_set.aggregate(Max("rank"))
        return result["rank__max"] if result["rank__max"] is not None else 0

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"slug": self.slug})


class InvoiceLineManager(models.Manager["InvoiceLine"]):
    @transaction.atomic
    def move_up(self, line: "InvoiceLine", distance: int = 1) -> None:
        """Moves the line up or down by the specified distance.

        If the distance is positive, moves up; if negative, moves down.
        If the line is already at the top or bottom, does nothing.
        """
        if line.rank <= distance:
            return

        invoice = cast("Invoice", line.invoice)

        invoice_qs = self.filter(invoice=invoice).order_by("rank")
        current_rank = cast("int", line.rank)
        new_rank = cast("int", line.rank - distance)
        lines_to_change = invoice_qs.filter(rank__gte=new_rank)

        msg = f"Moving line {line.rank} to {new_rank} in invoice {invoice.number}"
        logger.debug(msg)

        with contextlib.suppress(self.model.DoesNotExist):
            changed_lines = lines_to_change.update(rank=F("rank") + 1)
            msg = f"Changed lines: {changed_lines}"
            logger.debug(msg)
            if changed_lines > 0:
                line.rank = new_rank
                line.save(update_fields=["rank"])

                _ = invoice_qs.filter(rank_gt=current_rank).update(rank=F("rank") - 1)


@final
class InvoiceLine(models.Model):
    rank = models.PositiveSmallIntegerField(_("rank"), blank=True)
    description = models.CharField(_("description"), max_length=100)
    quantity = models.DecimalField(
        _("quantity"), max_digits=15, decimal_places=5, default=1
    )
    unit_price = MoneyField(_("unit price"), max_digits=19, decimal_places=4, default=0)
    invoice = models.ForeignKey(
        Invoice, verbose_name=_("invoice"), on_delete=models.CASCADE
    )

    objects = InvoiceLineManager()

    class Meta:
        constraints: list[BaseConstraint] = [
            UniqueConstraint(fields=["invoice", "rank"], name="unique_line_rank")
        ]
        ordering: list[str] = ["rank"]

    @override
    def __str__(self) -> str:
        return f"{self.description}|{self.invoice.number} - Line {self.rank}"

    @override
    def save(
        self,
        *args: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        **kwargs: bool | str | Iterable[str] | None,
    ) -> None:
        if TYPE_CHECKING:
            assert isinstance(self.invoice, Invoice)
        if self.rank is None:
            max_rank = self.invoice.max_rank()
            self.rank = max_rank + 1
        super().save(*args, **kwargs)  # pyright: ignore[reportAny]

        self.invoice.update_totals()

    @override
    def delete(
        self,
        *args: Any,  # pyright: ignore[reportExplicitAny, reportAny]
        **kwargs: Any,  # pyright: ignore[reportExplicitAny, reportAny]
    ) -> tuple[int, dict[str, int]]:
        invoice = cast("Invoice", self.invoice)
        this_rank = cast("int", self.rank)

        deleted = super().delete(*args, **kwargs)  # pyright: ignore[reportAny]

        _ = invoice.invoiceline_set.filter(rank__gt=this_rank).update(
            rank=F("rank") - 1
        )

        return deleted

    @property
    def extended_price(self) -> Decimal:
        return self.quantity * self.unit_price

    @property
    def line_number(self) -> int:
        return self.rank
