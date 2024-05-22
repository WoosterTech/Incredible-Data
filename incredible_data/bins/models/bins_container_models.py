from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TitleSlugDescriptionModel
from model_utils import Choices
from model_utils.models import TimeStampedModel
from shortuuid.django_fields import ShortUUIDField

from incredible_data.contacts.models.utility_models import UserStampedModel

# this is kept for a migration
from incredible_data.helpers import short_uuid  # noqa: F401
from incredible_data.helpers.functions import create_media_name

UUID_ALPHABET = settings.SHORTUUID_ALPHABET


class ContainerStyle(TitleSlugDescriptionModel):
    """For easy visual identification of bins/containers."""

    def __str__(self) -> str:
        return self.title


class Container(TimeStampedModel, UserStampedModel):
    id = ShortUUIDField(
        _("container id"),
        alphabet=UUID_ALPHABET,
        unique=True,
        primary_key=True,
        length=5,
        max_length=5,
    )
    contents = models.TextField(_("contents"))
    style = models.ForeignKey(
        ContainerStyle,
        verbose_name=_("container style"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    slug = AutoSlugField(populate_from="id")

    def __str__(self) -> str:
        return f"{self.id} | {self.contents:.25}"

    def get_absolute_url(self):
        return reverse("bins:container_detail", kwargs={"slug": self.slug})

    @property
    def primary_image(self):
        primary_image_qs = self.attachments.filter(
            attachment_type=ContainerAttachment.ATTACHMENT_TYPES.image, primary=True
        )

        if len(primary_image_qs) == 1:
            return primary_image_qs.first()

        return None


class ContainerAttachment(TimeStampedModel, UserStampedModel):
    container = models.ForeignKey(
        Container,
        verbose_name=_("container"),
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    name = models.CharField(
        _("name"),
        help_text=_("should auto-populate on save"),
        max_length=50,
        blank=True,
    )
    attachment = models.FileField(_("attachment"), upload_to="attachments/%Y/%m/")
    ATTACHMENT_TYPES = Choices(
        ("image", _("image")),
        ("document", _("document")),
        ("manual", _("manual")),
        ("other", _("other")),
    )
    attachment_type = models.CharField(
        _("attachment type"), choices=ATTACHMENT_TYPES, max_length=20
    )
    primary = models.BooleanField(_("primary attachment"), default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["container"],
                condition=Q(primary=True),
                name="unique_primary_attachment",
            )
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.name = create_media_name(self.attachment)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name or self.attachment.name
