from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from incredible_data.customers.models import UserStampedModel


class ContactPrimaryBaseModel(models.Model):
    contact = models.ForeignKey(
        "Contact",
        verbose_name=_("contact"),
        on_delete=models.CASCADE,
        related_name="%(class)s_contact",
    )
    primary = models.BooleanField(_("primary"), default=True)

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=["contact"],
                condition=Q(primary="True"),
                name="%(class)s_unique_primary",
            )
        ]


class Email(TimeStampedModel, UserStampedModel, ContactPrimaryBaseModel):
    email = models.EmailField(_("email"), max_length=254)
    slug = AutoSlugField(populate_from="email")

    def __str__(self):
        return self.email


class PhoneNumber(TimeStampedModel, UserStampedModel, ContactPrimaryBaseModel):
    number = PhoneNumberField(_("phone number"))
    slug = AutoSlugField(populate_from="number")

    def __str__(self):
        return str(self.number)


class Contact(TimeStampedModel, UserStampedModel):
    full_name = models.CharField(_("full name"), max_length=50)

    def __str__(self) -> str:
        return self.full_name
