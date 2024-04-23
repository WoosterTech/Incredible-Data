from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import ShortUUIDField
from django_extensions.db.models import TitleSlugDescriptionModel
from djmoney.models.fields import MoneyField
from model_utils.models import TimeStampedModel

from incredible_data.budget.budget_custom_fields import SimplePercentageField
from incredible_data.budget.receipt_services import analyze_receipt_file
from incredible_data.customers.models import UserStampedModel


def uploaded_receipt_path(instance: models.Model, filename: str) -> str:
    filename_path = Path(filename)
    datetime_now = timezone.now()
    return f"upload/receipts/{datetime_now:%Y}/{datetime_now:%m}/uploaded_receipt_{datetime_now:%Y%m%d-%H%M%S}{filename_path.suffix}"  # noqa: E501


class Merchant(TitleSlugDescriptionModel):
    verified = models.BooleanField(
        _("verified"), help_text=_("checked by a human"), default=False
    )

    def __str__(self) -> str:
        return f"{self.title}"


class MerchantAlias(models.Model):
    alias = models.CharField(_("alias"), max_length=50)
    matched_merchant = models.ForeignKey(
        Merchant, verbose_name=_("matched merchant"), on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.alias} <-> {self.matched_merchant}"


class Receipt(TimeStampedModel, UserStampedModel):
    receipt_file = models.FileField(
        _("receipt"), upload_to="upload/receipts/%Y/%m/", max_length=100
    )
    merchant = models.ForeignKey(
        Merchant,
        verbose_name=_("merchant"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    merchant_confidence = SimplePercentageField(
        _("merchant confidence"), max_digits=10, decimal_places=4
    )
    transaction_date = models.DateField(_("transaction date"), blank=True, null=True)
    transaction_date_confidence = SimplePercentageField(
        _("date confidence"), max_digits=10, decimal_places=4
    )
    grand_total = MoneyField(
        _("grand total"), blank=True, default=0, max_digits=19, decimal_places=4
    )
    tax_rate = SimplePercentageField(
        _("tax rate"), help_text=_("if applicable"), default=0.089
    )

    def __str__(self) -> str:
        if self.merchant is not None and self.transaction_date is not None:
            return f"Receipt({self.merchant} - {self.transaction_date:%Y%m%d} - {self.grand_total}"  # noqa: E501
        return f"uploaded file: {self.receipt_file}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            analyze_receipt_file.delay()
        return super().save(*args, **kwargs)


class ReceiptItem(models.Model):
    uuid = ShortUUIDField(primary_key=True, max_length=10)
    product_code = models.CharField(_("product code or UPC"), max_length=50, blank=True)
    description = models.CharField(_("description"), max_length=100, blank=True)
    total_price = MoneyField(
        _("total price"), max_digits=19, decimal_places=4, default=0
    )
    parent_receipt = models.ForeignKey(
        Receipt, verbose_name=_("parent receipt"), on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        if self.product_code is not None or self.description is not None:
            return f"Item({self.description or '(no description)'}, code={self.product_code or '(no UPC)'}, price={self.total_price})"  # noqa: E501
        return f"unknown item, price={self.total_price}"