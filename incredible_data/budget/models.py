import logging
from pathlib import Path

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField, ShortUUIDField
from django_extensions.db.models import TitleSlugDescriptionModel
from django_rubble.fields.db_fields import SimplePercentageField
from djmoney.models.fields import MoneyField

logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

ALLOWED_RECEIPT_EXTENSIONS = ["pdf", "png", "jpg"]


class ReversableModel(models.Model):
    """Adds a `get_absolute_url` method.

    Args:
        reverse_viewname (str): Name of the view to point to.
        reverse_kwargs (dict[str, str]): The kwargs to pass to `reverse` with the values
            as strings. Uses `getattr(self, value)` to get the actual value.
            Defaults to `{"pk", "pk"}`.
    """

    reverse_viewname: str
    reverse_kwargs: dict[str, str] = {"pk": "pk"}

    class Meta:
        abstract = True

    def get_absolute_url(self):
        from django.urls import reverse

        viewname = self.reverse_viewname
        reverse_kwargs = self.reverse_kwargs

        kwargs = {getattr(self, reverse_kwargs[key]) for key in reverse_kwargs}

        return reverse(viewname, kwargs=kwargs)


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


class ExpenseCategory(models.Model):
    name = models.CharField(_("name"), max_length=50)
    slug = AutoSlugField(populate_from=["name"])

    class Meta:
        verbose_name_plural = _("expense categories")

    def __str__(self) -> str:
        return self.name


class MerchantAlias(models.Model):
    alias = models.CharField(_("alias"), max_length=50)
    matched_merchant = models.ForeignKey(
        Merchant, verbose_name=_("matched merchant"), on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.alias} <-> {self.matched_merchant}"


class ReceiptFile(models.Model):
    file = models.FileField(
        _("receipt file"),
        upload_to="upload/receipts/%Y/%m/",
        max_length=100,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_RECEIPT_EXTENSIONS)
        ],
    )
    analyze_result = models.JSONField(editable=False, null=True)
    analyzed_datetime = models.DateTimeField(
        _("analyzed at"), editable=False, null=True
    )

    def __str__(self) -> str:
        return self.file.name


class Receipt(models.Model):
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
    grand_total_confidence = SimplePercentageField(
        _("grand total confidence"), max_digits=10, decimal_places=4
    )
    tax_rate = SimplePercentageField(
        _("tax rate"),
        decimal_places=5,
        max_digits=15,
        help_text=_("if applicable"),
        default=0.089,
    )
    receipt_file = models.ForeignKey(
        ReceiptFile,
        verbose_name=_("linked receipt"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        if self.merchant is not None and self.transaction_date is not None:
            return f"Receipt({self.merchant} - {self.transaction_date} - {self.grand_total})"  # noqa: E501
        return f"uploaded file: {self.receipt_file}"


class ReceiptItem(models.Model):
    uuid = ShortUUIDField(primary_key=True)
    product_code = models.CharField(_("product code or UPC"), max_length=50, blank=True)
    description = models.CharField(_("description"), max_length=100, blank=True)
    total_price = MoneyField(
        _("total price"), max_digits=19, decimal_places=4, default=0
    )
    parent_receipt = models.ForeignKey(
        Receipt, verbose_name=_("parent receipt"), on_delete=models.CASCADE
    )
    taxable = models.BooleanField(_("taxable"), default=False)
    expense_category = models.ForeignKey(
        ExpenseCategory,
        verbose_name=_("expense category"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        if self.product_code is not None or self.description is not None:
            return f"Item({self.description or '(no description)'}, code={self.product_code or '(no UPC)'}, price={self.total_price})"  # noqa: E501
        return f"unknown item, price={self.total_price}"
