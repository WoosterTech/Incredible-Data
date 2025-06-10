# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportIncompatibleVariableOverride=false
from typing import final, override

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class Manufacturer(models.Model):
    name = models.CharField(_("manufacturer name"), max_length=50)
    sku_code = models.CharField(
        _("sku code"),
        unique=True,
        help_text=_("shortened version used in item sku"),
        max_length=10,
    )

    class Meta:
        ordering: list[str] = ["name"]

    @override
    def __str__(self) -> str:
        return f"{self.name} | {self.sku_code}"

    def natural_key(self) -> str:
        return self.sku_code


@final
class ItemCategory(models.Model):
    name = models.CharField(_("category name"), max_length=50)
    sku_code = models.CharField(
        _("sku_code"),
        unique=True,
        help_text=_("shortened version used in item sku"),
        max_length=50,
    )

    class Meta:
        ordering: list[str] = ["name"]

    @override
    def __str__(self) -> str:
        return f"{self.name} | {self.sku_code}"

    def natural_key(self) -> str:
        return self.sku_code


@final
class SkuColor(models.Model):
    name = models.CharField(_("color name"), max_length=50)

    @override
    def __str__(self, *args, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        return self.name


@final
class Item(models.Model):
    sku = models.CharField(
        _("internal stock keeping unit"),
        help_text=_("MFG-CAT(-STYLE)(-SIZE)(-COLOR)"),
        max_length=50,
        blank=True,
    )
    description = models.CharField(_("description"), max_length=50)
    manufacturer = models.ForeignKey(
        Manufacturer,
        verbose_name=_(""),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    @override
    def __str__(self) -> str:
        return f"{self.description} | {self.sku}"
