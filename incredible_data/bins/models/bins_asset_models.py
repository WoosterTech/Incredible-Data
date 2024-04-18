from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField, ShortUUIDField
from django_extensions.db.models import TitleSlugDescriptionModel
from model_utils.models import TimeStampedModel

from incredible_data.contacts.models.utility_models import UserStampedModel


class Manufacturer(TitleSlugDescriptionModel):
    name = models.CharField(_("manufacturer"), max_length=50)
    website = models.URLField(_("website"), max_length=200, blank=True)
    slug = AutoSlugField(populate_from="name")


class Asset(TimeStampedModel, UserStampedModel):
    uuid = ShortUUIDField(primary_key=True, max_length=8)
    name = models.CharField(_("name"), max_length=50)
    manufacturer = models.ForeignKey(
        Manufacturer, verbose_name=_("manufacturer"), on_delete=models.PROTECT
    )
    model_name = models.CharField(_("model name"), max_length=50)
    model_number_str = models.CharField(_("model number"), max_length=50)
    serial_number_str = models.CharField(_("serial number"), max_length=50)
    acquisition_date = models.DateField(_("acquisition date"), default=date.today)
    location_container = models.ForeignKey(
        "bins.Container",
        verbose_name=_("container"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    slug = AutoSlugField(populate_from="uuid")
