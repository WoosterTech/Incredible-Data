import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TitleSlugDescriptionModel
from model_utils.models import TimeStampedModel

from incredible_data.contacts.models.utility_models import UserStampedModel


# Create your models here.
def short_uuid() -> str:
    return str(uuid.uuid4())[:5]


class ContainerStyle(TitleSlugDescriptionModel):
    """For easy visual identification of bins/containers."""

    def __str__(self) -> str:
        return self.title


class Container(TimeStampedModel, UserStampedModel):
    id = models.CharField(
        primary_key=True, max_length=5, default=short_uuid, unique=True
    )
    contents = models.TextField(_("contents"))
    image = models.ImageField(
        _("contents image"), upload_to="images/%Y/%m/", blank=True, null=True
    )
    style = models.ForeignKey(
        ContainerStyle,
        verbose_name=_("container style"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    slug = AutoSlugField(populate_from="id")
