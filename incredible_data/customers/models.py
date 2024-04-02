from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel


# Create your models here.
class UserStampedModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("modified by"),
        on_delete=models.CASCADE,
        related_name="%(class)s_modified_by",
    )

    class Meta:
        abstract = True


class Customer(TimeStampedModel, UserStampedModel):
    name = models.CharField(_("customer"), max_length=100)
    main_phone = models.ForeignKey(
        "contacts.PhoneNumber",
        verbose_name=_("organization phone"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    contacts = models.ManyToManyField(
        "contacts.Contact", verbose_name=_("contacts"), through="CustomerContact"
    )
    slug = AutoSlugField(populate_from="name")

    def __str__(self) -> str:
        return self.name


class CustomerContact(models.Model):
    customer = models.ForeignKey(
        Customer, verbose_name=_("customer"), on_delete=models.CASCADE
    )
    contact = models.ForeignKey(
        "contacts.Contact", verbose_name=_("contact"), on_delete=models.CASCADE
    )
    primary = models.BooleanField(_("primary"), default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["customer", "contact"],
                condition=Q(primary=True),
                name="single_primary_contact",
            )
        ]

    def __str__(self) -> str:
        return f"{self.customer} - {self.contact} | primary={self.primary}"
